# imports
import pandas as pd
import numpy as np
import joblib
from pipeline.feature_engineering import engineer_features
from pipeline.defender import evaluate_model, predict
from attacker.attacker import AmountScalingAttacker, TimeShiftAttacker, CategoryMimicryAttacker, CombinedAttacker

# load raw train and test data
raw_train_df = pd.read_csv('data/raw_train_transactions.csv')
raw_test_df = pd.read_csv('data/raw_test_transactions.csv')

featured_train_df = engineer_features(raw_train_df)

# set up scaler, attackers, models
model_names = ['lr_balanced', 'lr_naive', 'rf_balanced', 'rf_naive', 'xgb_balanced', 'xgb_naive']
models = {name: joblib.load(f'results/models/{name}.pkl') for name in model_names}
scaler = joblib.load('results/models/scaler.pkl')

attackers = [
    AmountScalingAttacker(),
    TimeShiftAttacker(),
    CategoryMimicryAttacker(),
    CombinedAttacker()
]

# define feature cols
feature_cols = ['amount_zscore', 'transactions_last_1h', 'transactions_last_24h', 'time_since_last_txn', 'is_new_category', 'is_foreign']

results = []

# retraining loop (max 10 rounds)
for round in range(10):
    print(f"Round {round + 1}")
    
    # for each attacker:
    for attacker in attackers:
        for model_name, model in models.items():
            print(f"Evaluating {model_name} against {attacker.name} attack")

            # attack test data
            attacked_test_df = attacker.attack(raw_test_df)

            # feature engineer attacked test data
            attacked_test_df = engineer_features(attacked_test_df)

            # evaluate defender → record metrics
            X_attacked = pd.DataFrame(scaler.transform(attacked_test_df[feature_cols]), columns=feature_cols)
            y_attacked = attacked_test_df['is_fraud']
            metrics = evaluate_model(model, X_attacked, y_attacked)

            results.append({
                'round': round,
                'attacker': attacker.name,
                'model': model_name,
                'recall': metrics['recall'],
                'f1_score': metrics['f1_score'],
                'precision': metrics['precision'],
                'roc_auc': metrics['roc_auc']
            })

            # find detected attacks
            predictions = predict(model, X_attacked)
            detected = attacked_test_df[(attacked_test_df['is_fraud'] == 1) & (predictions == 1)]

            combined_train = pd.concat([featured_train_df, detected])

            # scale it
            X_train_new = pd.DataFrame(scaler.transform(combined_train[feature_cols]),columns=feature_cols)
            y_train_new = combined_train['is_fraud']

            # retrain
            model.fit(X_train_new, y_train_new)
    
    # check for equilibrium → break if reached
    current_recall = np.mean([r['recall'] for r in results if r['round'] == round])

    if round > 0:
        previous_recall = np.mean([r['recall'] for r in results if r['round'] == round - 1])
        recall_diff = abs(current_recall - previous_recall)
        if recall_diff < 0.005:
            print("Equilibrium reached!")
            break

for model_name, model in models.items():
    joblib.dump(model, f'results/models/{model_name}_retrained.pkl')
print("Retrained models saved!")

# save results
results_df = pd.DataFrame(results)
results_df.to_csv('results/retraining_results.csv', index=False)
print("Retraining results saved!")