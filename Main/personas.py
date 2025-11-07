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

    def simulate_day(self, current_date, transaction_id_counter):
        daily_transactions = []
        is_weekday = current_date.weekday() < 5
        if is_weekday:
            day_type = 'prob_weekday'
        else:
            day_type = 'prob_weekend'

        # Loop through every hour of the day
        for hour in range(24):
            # Loop through every category this persona knows about
            for cat, rules in self.profile.items():
                
                # Get the probability of this action at this hour
                if day_type in rules:
                    hourly_prob = rules[day_type][hour]
                else:
                    continue # This persona doesn't do this on this day_type
                
                # Roll the dice
                if np.random.rand() < hourly_prob:
                    # --- TRANSACTION OCCURS ---
                    
                    # 1. Get transaction amount
                    amount = round(np.random.normal(rules['amount_mean'], rules['amount_std']), 2)
                    if amount < 0: amount = 0.01 # Ensure non-negative
                    
                    # 2. Get merchant details
                    if cat not in MERCHANTS: continue # Safety check
                    merchant_details = MERCHANTS[cat]
                    
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
                        'merchant_id': random.choice(merchant_details['ids']),
                        'merchant_category': cat,
                        'merchant_country': merchant_details['country'],
                        'Channel': merchant_details['channel'],
                        'is_fraud': 0
                    })
                    transaction_id_counter += 1
                    
        return daily_transactions, transaction_id_counter
    
    def _create_random_time(self, base_date, hour):
        """Helper to create a random time within a given hour."""
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return datetime.datetime(base_date.year, base_date.month, base_date.day, hour, minute, second)