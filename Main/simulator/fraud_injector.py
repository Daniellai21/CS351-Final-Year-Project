import pandas as pd
import numpy as np
import random
import datetime
from simulator.merchants import MERCHANTS

FRAUD_COUNTRIES = ['NG', 'RU', 'BR', 'IN', 'CN', 'RO']

def build_user_profiles(df: pd.DataFrame) -> dict:
    """
    Build a profile for each user from their legitimate transaction history.
    """
    profiles = {}

    for user_id, user_df in df.groupby('user_id'):
        profiles[user_id] = {
            'amount_mean': user_df['Transaction amount'].mean(),
            'amount_std': user_df['Transaction amount'].std(),
            'typical_hour': pd.to_datetime(user_df['Timestamp']).dt.hour.mode()[0],
            'used_categories': set(user_df['merchant_category']),
            'home_country': 'GB'
        }

    return profiles

# Fraud Pattern 1: High Value Night Fraud
def generate_high_value_night_fraud(user_id: str, profile: dict, df: pd.DataFrame) -> dict:
    """
    Generate a high value transaction at an unusual hour at a novel merchant.
    """
    if pd.isna(profile['amount_std']):
        amount = profile['amount_mean'] * 3
    else:
        amount = profile['amount_mean'] + 3 * profile['amount_std']
    hour = random.randint(1, 5)
    merchant_cat = random.choice(list(MERCHANTS.keys()))
    merchant_details = MERCHANTS[merchant_cat]

    start_date = datetime.date(2025, 1, 1)
    random_days = random.randint(0, 89)
    fraud_date = start_date + datetime.timedelta(days=random_days)

    return {
        'Transaction_id': None, 
        'Timestamp': datetime.datetime(fraud_date.year, fraud_date.month, fraud_date.day, hour, random.randint(0, 59), random.randint(0, 59)),   
        'user_id': user_id,
        'Card_id': df[df['user_id'] == user_id].iloc[0]['Card_id'],         
        'home_country': profile['home_country'],
        'Transaction amount': amount,
        'merchant_id': random.choice(merchant_details['ids']),
        'merchant_category': merchant_cat,
        'merchant_country': merchant_details['country'],
        'Channel': merchant_details['channel'],
        'is_fraud': 1
    }

# Fraud Pattern 2: Velocity Fraud
def generate_velocity_fraud(user_id: str, profile: dict, df: pd.DataFrame) -> list:
    """
    Generate multiple transactions in rapid succession on the same card
    """
    num_transactions = random.randint(3, 6)
    hour = profile['typical_hour']

    start_date = datetime.date(2025, 1, 1)
    random_days = random.randint(0, 89)
    fraud_date = start_date + datetime.timedelta(days=random_days)
    base_time = datetime.datetime(fraud_date.year, fraud_date.month, fraud_date.day, hour, random.randint(0, 59), 0)

    transactions = []
    for i in range(num_transactions):
        if pd.isna(profile['amount_std']):
            amount = profile['amount_mean']
        else:
            amount = np.random.normal(profile['amount_mean'], profile['amount_std'])
        amount = max(0.01, amount)  # Ensure non-negative amounts
        merchant_cat = random.choice(list(MERCHANTS.keys()))
        merchant_details = MERCHANTS[merchant_cat]

        transactions.append({
            'Transaction_id': None, 
            'Timestamp': base_time + datetime.timedelta(seconds=i*30),  
            'user_id': user_id,
            'Card_id': df[df['user_id'] == user_id].iloc[0]['Card_id'],         
            'home_country': profile['home_country'],
            'Transaction amount': amount,
            'merchant_id': random.choice(merchant_details['ids']),
            'merchant_category': merchant_cat,
            'merchant_country': merchant_details['country'],
            'Channel': merchant_details['channel'],
            'is_fraud': 1
        })

    return transactions

# Fraud Pattern 3: Account Takeover Fraud
def generate_account_takeover_fraud(user_id: str, profile: dict, df: pd.DataFrame) -> dict:
    """
    Generate a transaction in a category the user has never used before.
    """
    if pd.isna(profile['amount_std']):
        amount = profile['amount_mean']
    else:
        amount = np.random.normal(profile['amount_mean'], profile['amount_std'])
    amount = max(0.01, amount)  # Ensure non-negative amounts
    hour = (profile['typical_hour'] + random.randint(-2, 2)) % 24
    new_categories = set(MERCHANTS.keys()) - profile['used_categories']
    if not new_categories:
        new_categories = set(MERCHANTS.keys())
    merchant_cat = random.choice(list(new_categories))
    merchant_details = MERCHANTS[merchant_cat]
    start_date = datetime.date(2025, 1, 1)
    random_days = random.randint(0, 89)
    fraud_date = start_date + datetime.timedelta(days=random_days)

    return {
        'Transaction_id': None, 
        'Timestamp': datetime.datetime(fraud_date.year, fraud_date.month, fraud_date.day, hour, random.randint(0, 59), random.randint(0, 59)),   
        'user_id': user_id,
        'Card_id': df[df['user_id'] == user_id].iloc[0]['Card_id'],         
        'home_country': profile['home_country'],
        'Transaction amount': amount,
        'merchant_id': random.choice(merchant_details['ids']),
        'merchant_category': merchant_cat,
        'merchant_country': merchant_details['country'],
        'Channel': merchant_details['channel'],
        'is_fraud': 1
    }

# Fraud Pattern 4: Geographic Anomaly Fraud
def generate_geographic_anomaly_fraud(user_id: str, profile: dict, df: pd.DataFrame) -> dict:
    """
    Generate a transaction from a country the user has never transacted from before.
    """
    if pd.isna(profile['amount_std']):
        amount = profile['amount_mean']
    else:
        amount = np.random.normal(profile['amount_mean'], profile['amount_std'])
    amount = max(0.01, amount)  # Ensure non-negative amounts
    hour = (profile['typical_hour'] + random.randint(-2, 2)) % 24
    fraud_country = random.choice(FRAUD_COUNTRIES)
    start_date = datetime.date(2025, 1, 1)
    random_days = random.randint(0, 89)
    fraud_date = start_date + datetime.timedelta(days=random_days)
    merchant_cat = random.choice(list(MERCHANTS.keys()))
    merchant_details = MERCHANTS[merchant_cat]

    return {
        'Transaction_id': None, 
        'Timestamp': datetime.datetime(fraud_date.year, fraud_date.month, fraud_date.day, hour, random.randint(0, 59), random.randint(0, 59)),   
        'user_id': user_id,
        'Card_id': df[df['user_id'] == user_id].iloc[0]['Card_id'],         
        'home_country': profile['home_country'],
        'Transaction amount': amount,
        'merchant_id': random.choice(merchant_details['ids']),
        'merchant_category': merchant_cat,
        'merchant_country': fraud_country,
        'Channel': merchant_details['channel'],
        'is_fraud': 1
    }

# Main function to inject fraud into the dataset
def inject_fraud(df: pd.DataFrame, fraud_rate: float = 0.02) -> pd.DataFrame:
    """
    Inject fraudulent transactions inot the clean dataframe.
    """
    campaigns = {
        'smash_and_grab': ['velocity', 'high_value_night'],
        'account_takeover_geo': ['account_takeover', 'geographic_anomaly'],
        'single_high_value': ['high_value_night'],
        'single_velocity': ['velocity'],
        'single_account_takeover': ['account_takeover'],
        'single_geographic': ['geographic_anomaly']
    }

    pattern_functions = {
        'high_value_night': generate_high_value_night_fraud,
        'velocity': generate_velocity_fraud,  
        'account_takeover': generate_account_takeover_fraud,
        'geographic_anomaly': generate_geographic_anomaly_fraud
    }

    profiles = build_user_profiles(df)
    all_users = list(profiles.keys())

    fraud_transactions = []
    target_fraud_count = int(len(df) * fraud_rate)

    while len(fraud_transactions) < target_fraud_count:
        campaign = random.choice(list(campaigns.keys()))
        patterns = campaigns[campaign]
        user_id = random.choice(all_users)
        profile = profiles[user_id]
        for pattern in patterns:
            if len(fraud_transactions) >= target_fraud_count:
                break
            func = pattern_functions[pattern]
            result = func(user_id, profile, df)
            if isinstance(result, list):
                for txn in result:
                    txn['fraud_campaign'] = campaign
                fraud_transactions.extend(result)
            else:
                result['fraud_campaign'] = campaign
                fraud_transactions.append(result)

    fraud_df = pd.DataFrame(fraud_transactions)
    combined_df = pd.concat([df, fraud_df], ignore_index=True)
    combined_df = combined_df.sample(frac=1).reset_index(drop=True)  # Shuffle the dataset
    combined_df['Transaction_id'] = range(1, len(combined_df) + 1) 

    return combined_df