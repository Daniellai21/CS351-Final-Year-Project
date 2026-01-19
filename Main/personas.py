import numpy as np
import random
import datetime
from merchants import MERCHANTS 

class Persona:
    def __init__(self, user_id, card_id, profile):
        """Initializes a persona from a behavior profile."""
        self.user_id = user_id
        self.card_id = card_id
        self.home_country = "GB"
        self.profile = profile['categories']
        self.merchant_memory = {}
        # Categories that should only occur once per day
        self.once_per_day_categories = {
            "lunch",
            "groceries",
            "utility_bill"
        }
        self.trip_config = {
            "trigger_category": "groceries",
            "trigger_prob": 0.55,       
            "max_addons": 2,               
            "addon_categories": ["coffee", "lunch"],
            "addon_probabilities": [0.6, 0.4],  
            "addon_time_window_minutes": 45     
        }
        self.skewed_amount_categories = {
            "groceries",
            "online_shopping",
            "utility_bill",
            "phone_bill",
            "transport_ride_hail",
            "subscription",
        }

        if self.user_id.startswith("USER_C_"):
            # commuter: 2 subs + phone + utilities
            self.recurring = [
                {"cat": "subscription", "day": 3},
                {"cat": "subscription", "day": 17},
                {"cat": "phone_bill", "day": 22},
                {"cat": "utility_bill", "day": 5},
            ]
        elif self.user_id.startswith("USER_S_"):
            # student: 1 sub + phone + smaller utilities
            self.recurring = [
                {"cat": "subscription", "day": 12},
                {"cat": "phone_bill", "day": 24},
                {"cat": "utility_bill", "day": 6},
            ]
        else:
            # homebody: 1 sub + phone + utilities
            self.recurring = [
                {"cat": "subscription", "day": 10},
                {"cat": "phone_bill", "day": 20},
                {"cat": "utility_bill", "day": 7},
            ]

    def simulate_day(self, current_date, transaction_id_counter):
        daily_transactions = []

        is_weekday = current_date.weekday() < 5
        day_type = 'prob_weekday' if is_weekday else 'prob_weekend'
        used_today = set()

        category_counts_today = {}

        recurring_txns, transaction_id_counter = self._generate_recurring_payments(
            current_date=current_date,
            transaction_id_counter=transaction_id_counter,
            used_today=used_today
        )
        daily_transactions.extend(recurring_txns)

        # Loop through every hour of the day
        for hour in range(24):
            # Loop through every category this persona knows about
            for cat, rules in self.profile.items():
                
                # If this category is once-per-day and already occurred, skip
                if cat in self.once_per_day_categories and cat in used_today:
                    continue

                if cat in {"transport_public", "transport_ride_hail"}:
                    if category_counts_today.get(cat, 0) >= 4:
                        continue
                
                # Get the probability of this action at this hour
                if day_type in rules:
                    hourly_prob = rules[day_type][hour]
                else:
                    continue # This persona doesn't do this on this day_type
                
                # Roll the dice
                if np.random.rand() < hourly_prob:
                    # --- TRANSACTION OCCURS ---
                    
                    # 1. Get transaction amount
                    amount = self._sample_amount(
                        rules['amount_mean'],
                        rules['amount_std'],
                        skewed=(cat in self.skewed_amount_categories)
                    )
                    
                    # 2. Get merchant details
                    if cat not in MERCHANTS: continue # Safety check
                    merchant_details = MERCHANTS[cat]
                    # 80%: use preferred merchant, 20%: choose other merchant
                    merchant_id = self._choose_merchant(cat, merchant_details)
                    
                    # 3. Create timestamp
                    timestamp = self._create_random_time(current_date, hour)
                    
                    # 4. Append transaction
                    daily_transactions.append({
                        'Transaction_id': transaction_id_counter,
                        'Timestamp': timestamp,
                        'Card_id': self.card_id,
                        'home_country': self.home_country,
                        'user_id': self.user_id,
                        'Transaction amount': amount,
                        'merchant_id': merchant_id,
                        'merchant_category': cat,
                        'merchant_country': merchant_details['country'],
                        'Channel': merchant_details['channel'],
                        'is_fraud': 0
                    })
                    transaction_id_counter += 1

                    category_counts_today[cat] = category_counts_today.get(cat, 0) + 1

                    if cat == self.trip_config["trigger_category"]:
                        extra_txns, transaction_id_counter = self._maybe_generate_trip_addons(
                        current_date=current_date,
                        base_timestamp=timestamp,
                        used_today=used_today,
                        transaction_id_counter=transaction_id_counter
                        )
                        daily_transactions.extend(extra_txns)

                    # Mark category as used today if it's once-per-day
                    if cat in self.once_per_day_categories:
                        used_today.add(cat)
                    
        return daily_transactions, transaction_id_counter
    
    def weekly_drift(self, drift_std=0.02):
        for cat, rules in self.profile.items():
            # multiplicative drift factor ~ N(1, drift_std)
            drift_factor = np.random.normal(1.0, drift_std)

            # Keep means from collapsing or exploding
            new_mean = rules['amount_mean'] * drift_factor
            rules['amount_mean'] = max(0.5, float(new_mean))

    def _choose_merchant(self, cat, merchant_details, stickiness=0.8):
        ids = merchant_details['ids']
        if not ids:
            return None

        # If no preferred merchant yet, pick one
        if cat not in self.merchant_memory:
            self.merchant_memory[cat] = random.choice(ids)

        preferred = self.merchant_memory[cat]

        # With probability stickiness, use preferred; otherwise choose a different one if possible
        if random.random() < stickiness:
            return preferred

        if len(ids) == 1:
            return preferred

        # Choose a non-preferred merchant
        other_ids = [m for m in ids if m != preferred]
        return random.choice(other_ids) if other_ids else preferred
    
    def _create_random_time(self, base_date, hour):
        """Helper to create a random time within a given hour."""
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return datetime.datetime(base_date.year, base_date.month, base_date.day, hour, minute, second)
    
    def _maybe_generate_trip_addons(self, current_date, base_timestamp, used_today, transaction_id_counter):
        cfg = self.trip_config
        extra_txns = []

        if random.random() > cfg["trigger_prob"]:
            return extra_txns, transaction_id_counter

        num_addons = random.randint(0, cfg["max_addons"])
        if num_addons == 0:
            return extra_txns, transaction_id_counter
        
        # Pick addon categories using weighted probabilities
        addon_cats = random.choices(
            population=cfg["addon_categories"],
            weights=cfg["addon_probabilities"],
            k=num_addons
        )

        for addon_cat in addon_cats:
            # Respect once-per-day categories
            if addon_cat in self.once_per_day_categories and addon_cat in used_today:
                continue

            # Must exist in this persona profile and in MERCHANTS
            if addon_cat not in self.profile or addon_cat not in MERCHANTS:
                continue

            rules = self.profile[addon_cat]
            merchant_details = MERCHANTS[addon_cat]

            amount = self._sample_amount(
                rules['amount_mean'],
                rules['amount_std'],
                skewed=(addon_cat in self.skewed_amount_categories)
            )

            # Merchant (sticky)
            merchant_id = self._choose_merchant(addon_cat, merchant_details)

            # Timestamp clustered near the groceries time
            ts = self._random_time_near(base_timestamp, cfg["addon_time_window_minutes"])

            extra_txns.append({
                'Transaction_id': transaction_id_counter,
                'Timestamp': ts,
                'Card_id': self.card_id,
                'home_country': self.home_country,
                'user_id': self.user_id,
                'Transaction amount': amount,
                'merchant_id': merchant_id,
                'merchant_category': addon_cat,
                'merchant_country': merchant_details['country'],
                'Channel': merchant_details['channel'],
                'is_fraud': 0
            })
            transaction_id_counter += 1

            if addon_cat in self.once_per_day_categories:
                used_today.add(addon_cat)

        return extra_txns, transaction_id_counter
    
    def _random_time_near(self, base_timestamp, window_minutes):
        offset = random.randint(-window_minutes, window_minutes)
        candidate = base_timestamp + datetime.timedelta(minutes=offset)

        # Clip to same date
        if candidate.date() != base_timestamp.date():
            if candidate < base_timestamp:
                candidate = datetime.datetime(
                    base_timestamp.year, base_timestamp.month, base_timestamp.day, 0, 0, 0
                )
            else:
                candidate = datetime.datetime(
                    base_timestamp.year, base_timestamp.month, base_timestamp.day, 23, 59, 59
                )

        return candidate
    
    def _generate_recurring_payments(self, current_date, transaction_id_counter, used_today):
        txns = []
        day_of_month = current_date.day

        for r in getattr(self, "recurring", []):
            if day_of_month != r["day"]:
                continue

            cat = r["cat"]
            if cat not in self.profile:
                continue  # must exist in profile categories
            if cat not in MERCHANTS:
                continue

            rules = self.profile[cat]
            merchant_details = MERCHANTS[cat]

            amount = self._sample_amount(
                rules['amount_mean'],
                rules['amount_std'],
                skewed=(cat in self.skewed_amount_categories)
            )

            # time jitter (usually early morning online billing)
            hour = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
            ts = self._create_random_time(current_date, hour)

            # merchant stickiness applies here too
            merchant_id = self._choose_merchant(cat, merchant_details)

            txns.append({
                'Transaction_id': transaction_id_counter,
                'Timestamp': ts,
                'Card_id': self.card_id,
                'home_country': self.home_country,
                'user_id': self.user_id,
                'Transaction amount': amount,
                'merchant_id': merchant_id,
                'merchant_category': cat,
                'merchant_country': merchant_details['country'],
                'Channel': merchant_details['channel'],
                'is_fraud': 0
            })
            transaction_id_counter += 1

            # (optional) mark once-per-day if you add these cats there later
            used_today.add(cat)

        return txns, transaction_id_counter
    
    def _sample_amount(self, mean, std, skewed=False):
        """
        Samples a transaction amount.
        - If skewed=False: normal distribution (tight, symmetric)
        - If skewed=True: lognormal distribution (right-skewed, human-like)
        """
        if not skewed:
            val = np.random.normal(mean, std)
            return round(max(0.01, val), 2)
        else:
            # Lognormal with similar scale but long right tail
            # We ignore std directly and control shape via sigma
            sigma = 0.6
            mu = np.log(max(mean, 0.1)) - 0.5 * sigma**2
            val = np.random.lognormal(mu, sigma)
            return round(max(0.01, val), 2)