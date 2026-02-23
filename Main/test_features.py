import pandas as pd
from pipeline.feature_engineering import engineer_features

df = pd.read_csv('data/synthetic_transactions_v1.csv')
print(f"Raw data shape: {df.shape}")

featured_df = engineer_features(df)
print(f"Featured data shape: {featured_df.shape}")
print(featured_df.head())
print(featured_df.describe())

featured_df.to_csv('data/featured_transactions_v1.csv', index=False)
print("Featured transactions saved!")