import pandas as pd
from attacker.attacker import AmountScalingAttacker, TimeShiftAttacker, CategoryMimicryAttacker, CombinedAttacker
from pipeline.feature_engineering import engineer_features

df = pd.read_csv('data/raw_test_transactions.csv')
print(f"Raw data shape: {df.shape}")

attackers = [
    AmountScalingAttacker(),
    TimeShiftAttacker(),
    CategoryMimicryAttacker(),
    CombinedAttacker()
]

for attacker in attackers:
    print(f"Running attack: {attacker.name}")
    attacked_df = attacker.attack(df)
    # apply feature engineering
    attacked_df = engineer_features(attacked_df)
    # save with a meaningful filename using attacker.name
    attacked_df.to_csv(f'data/attacked_transactions_{attacker.name}.csv', index=False)

    print(f"Attacked data shape: {attacked_df.shape}")
    print(attacked_df.head())
    print(attacked_df.describe())

print("Attacked transactions saved!")