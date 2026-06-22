"""
Data preparation script.

Splits the synthetic dataset using an 80/20 temporal cutoff (no random splitting
to prevent look-ahead bias), then applies the feature engineering pipeline.
Outputs: raw_train/test_transactions.csv, featured_transactions_v2.csv
"""

import pandas as pd
from pipeline.feature_engineering import engineer_features

df = pd.read_csv('data/demo_synthetic_transactions.csv')
print(f"Raw data shape: {df.shape}")

# Save raw test set before feature engineering
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
cutoff = df['Timestamp'].quantile(0.8)
raw_test_df = df[df['Timestamp'] > cutoff]
raw_test_df.to_csv('data/demo_raw_test_transactions.csv', index=False)
print(f"Raw test set saved: {raw_test_df.shape}")

# Save raw train set before feature engineering
raw_train_df = df[df['Timestamp'] <= cutoff]
raw_train_df.to_csv('data/demo_raw_train_transactions.csv', index=False)
print(f"Raw train set saved: {raw_train_df.shape}")

featured_df = engineer_features(df)
print(f"Featured data shape: {featured_df.shape}")
print(featured_df.head())
print(featured_df.describe())

featured_df.to_csv('data/demo_featured_transactions_v2.csv', index=False)
print("Featured transactions saved!")