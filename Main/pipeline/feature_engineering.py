import pandas as pd
import numpy as np

def compute_features(txn, user_history):
    features = {}

    # Identifier columns
    features['Transaction_id'] = txn['Transaction_id']
    features['Timestamp'] = txn['Timestamp']
    features['user_id'] = txn['user_id']
    features['is_fraud'] = txn['is_fraud']
    features['fraud_campaign'] = txn['fraud_campaign']

    # Feature 1: amount z-score
    if user_history:
        amounts = [h['Transaction amount'] for h in user_history]
        mean_amount = np.mean(amounts)
        if len(amounts) > 1:
            std_amount = np.std(amounts)
        else:
            std_amount = 0
        features['amount_zscore'] = (txn['Transaction amount'] - mean_amount) / std_amount if std_amount > 0 else 0
    else:
        features['amount_zscore'] = 0

    # Feature 2: transactions in last 1 hour
    features['transactions_last_1h'] = sum(1 for h in user_history if 0 < (txn['Timestamp'] - h['Timestamp']).total_seconds() <= 3600)

    # Feature 3: transactions in last 24 hours
    features['transactions_last_24h'] = sum(1 for h in user_history if 0 < (txn['Timestamp'] - h['Timestamp']).total_seconds() <= 86400)

    # Feature 4: time since last transaction
    if user_history:
        features['time_since_last_txn'] = (txn['Timestamp'] - user_history[-1]['Timestamp']).total_seconds()
    else:
        features['time_since_last_txn'] = 0

    # Feature 5: is it a new category for the user
    seen_categories = set(h['merchant_category'] for h in user_history)
    features['is_new_category'] = int(txn['merchant_category'] not in seen_categories)

    # Feature 6: is it a foreign country
    features['is_foreign'] = int(txn['merchant_country'] != 'GB')

    return features

def engineer_features(df):
    df = df.sort_values('Timestamp').reset_index(drop=True)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    feature_rows = []

    for user_id, user_txns in df.groupby('user_id'):
        user_history = []

        for idx, txn in user_txns.iterrows():
            # compute features using user_history
            features = compute_features(txn, user_history)
            feature_rows.append(features)

            # add current txn to history after computing features
            user_history.append(txn)

    return pd.DataFrame(feature_rows)

