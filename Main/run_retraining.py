# imports
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import precision_recall_curve
from pipeline.feature_engineering import engineer_features
from pipeline.defender import predict
from attacker.attacker import AmountScalingAttacker, TimeShiftAttacker, CategoryMimicryAttacker, VelocitySpacingAttacker, CombinedAttacker, ScoreAwareAttacker

# 1. Load raw train and test data
raw_train_df = pd.read_csv('data/raw_train_transactions.csv')
raw_test_df = pd.read_csv('data/raw_test_transactions.csv')
raw_test_df = raw_test_df.sort_values('Timestamp').reset_index(drop=True) # Ensure chronological order for time-based attacks

# 2. Split test into Feedback (for learning) and Holdout (for final evaluation)
cutoff_idx = int(len(raw_test_df) * 0.5)
feedback_df = raw_test_df.iloc[:cutoff_idx].copy()
holdout_df = raw_test_df.iloc[cutoff_idx:].copy()

# 3. Engineer initial training set
featured_train_df = engineer_features(raw_train_df)

# 4. Set up scaler, attackers, models
model_names = ['lr_balanced', 'lr_naive', 'rf_balanced', 'rf_naive', 'xgb_balanced', 'xgb_naive']
models_original = {name: joblib.load(f'results/models/{name}.pkl') for name in model_names}
scaler = joblib.load('results/models/scaler.pkl')
feature_cols = ['amount_zscore', 'transactions_last_1h', 'amount_sum_last_24h', 'log_time_since_last_txn', 'is_new_category', 'is_foreign', 'hour_of_day', 'is_night']

# 5. Static attackers (pre-computable)
static_attackers = [
    AmountScalingAttacker(),
    TimeShiftAttacker(),
    CategoryMimicryAttacker(),
    VelocitySpacingAttacker(),
    CombinedAttacker()
]

# 6. Score-aware attacker (one per balanced model - computed each round)
score_aware_attackers = {model_name: ScoreAwareAttacker(base_attacker=CombinedAttacker(), model=models_original[model_name], scaler=scaler, feature_cols=feature_cols) for model_name in ['lr_balanced', 'rf_balanced', 'xgb_balanced']}

def get_clean_threshold(model, X, y):
    """Get optimal F1threshold from clean data"""
    y_proba = model.predict_proba(X)[:, 1]
    p, r, thresholds = precision_recall_curve(y, y_proba)
    f1s = 2 * (p * r) / (p + r + 1e-9)
    return thresholds[f1s[:-1].argmax()]

def evaluate_at_threshold(model, X, y, threshold):
    """Evaluate using a fixed threshold"""
    y_proba = model.predict_proba(X)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)
    return {
        'precision': precision_score(y, y_pred, zero_division=0),
        'recall': recall_score(y, y_pred, zero_division=0),
        'f1_score': f1_score(y, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y, y_proba)
    }

print("Pre-computing attacked datasets...")
attacked_data = {}
for attacker in static_attackers:
    print(f" - Generating {attacker.name}...")
    attacked_data[attacker.name] = {
        'feedback': engineer_features(attacker.attack(feedback_df)),
        'holdout': engineer_features(attacker.attack(holdout_df))
    }

# Isolate training data and model states
# For static attackers — one state per (attacker, model) pair
# For score-aware attackers — one state per model
training_states = {}
model_states = {}

for attacker in static_attackers:
    for model_name, model in models_original.items():
        state_key = (attacker.name, model_name)
        training_states[state_key] = featured_train_df.copy()
        model_states[state_key] = joblib.load(f'results/models/{model_name}.pkl')

for model_name in score_aware_attackers:
    state_key = (f'score_aware_combined', model_name)
    training_states[state_key] = featured_train_df.copy()
    model_states[state_key] = joblib.load(f'results/models/{model_name}.pkl')

# compute fixed thresholds from clean holdout
featured_holdout_df = engineer_features(holdout_df)
X_holdout_clean = pd.DataFrame(scaler.transform(featured_holdout_df[feature_cols]), columns=feature_cols)
y_holdout_clean = featured_holdout_df['is_fraud']

print("Computing fixed thresholds from clean holdout...")
fixed_thresholds = {}

for attacker in static_attackers:
    for model_name in model_names:
        state_key = (attacker.name, model_name)
        model = model_states[state_key]
        fixed_thresholds[state_key] = get_clean_threshold(model, X_holdout_clean, y_holdout_clean)
        print(f"  {model_name} vs {attacker.name}: threshold = {fixed_thresholds[state_key]:.3f}")

for model_name in score_aware_attackers:
    state_key = (f'score_aware_combined', model_name)
    model = model_states[state_key]
    fixed_thresholds[state_key] = get_clean_threshold(model, X_holdout_clean, y_holdout_clean)
    print(f"  {model_name} vs score-aware combined: threshold = {fixed_thresholds[state_key]:.3f}")

results = []

for round_num in range(8):
    print(f"\n--- Round {round_num + 1} ---")
    
    for attacker in static_attackers:
        
        # Grab the pre-computed datasets for this attacker
        attacked_feedback_df = attacked_data[attacker.name]['feedback']
        attacked_holdout_df = attacked_data[attacker.name]['holdout']
        
        X_holdout = pd.DataFrame(scaler.transform(attacked_holdout_df[feature_cols]), columns=feature_cols)
        y_holdout = attacked_holdout_df['is_fraud']
        X_feedback = pd.DataFrame(scaler.transform(attacked_feedback_df[feature_cols]), columns=feature_cols)

        for model_name in model_names:
            state_key = (attacker.name, model_name)
            
            # Grab the specific model and training data for this timeline
            current_model = model_states[state_key]
            current_train_df = training_states[state_key]

            # 1. Evaluate defender on Holdout -> record metrics
            metrics = evaluate_at_threshold(current_model, X_holdout, y_holdout, fixed_thresholds[state_key])

            results.append({
                'round': round_num,
                'attacker': attacker.name,
                'model': model_name,
                'recall': metrics['recall'],
                'f1_score': metrics['f1_score'],
                'precision': metrics['precision'],
                'roc_auc': metrics['roc_auc']
            })

            # 2. Find detected attacks in the FEEDBACK set to learn from
            predictions = predict(current_model, X_feedback)
            detected = attacked_feedback_df[(attacked_feedback_df['is_fraud'] == 1) & (predictions == 1)]

            # 3. Accumulate knowledge independently
            current_train_df = pd.concat([current_train_df, detected]).drop_duplicates(subset='Transaction_id')
            training_states[state_key] = current_train_df # Save it back

            # 4. Scale and retrain this specific model
            X_train_new = pd.DataFrame(scaler.transform(current_train_df[feature_cols]), columns=feature_cols)
            y_train_new = current_train_df['is_fraud']
            current_model.fit(X_train_new, y_train_new)
            
            # Save the retrained model back to the state dictionary
            model_states[state_key] = current_model

    for model_name, sa_attacker in score_aware_attackers.items():
        state_key = ('score_aware_combined', model_name)
        current_model = model_states[state_key]
        current_train_df = training_states[state_key]

        print(f"  Computing score-aware attacks for {model_name} (round {round_num + 1})...")

        # update attacker with current model state
        sa_attacker.update_model(current_model)

        # recompute attack each round using updated model
        attacked_feedback_df = engineer_features(sa_attacker.attack(feedback_df))
        attacked_holdout_df = engineer_features(sa_attacker.attack(holdout_df))

        X_holdout = pd.DataFrame(scaler.transform(attacked_holdout_df[feature_cols]), columns=feature_cols)
        y_holdout = attacked_holdout_df['is_fraud']
        X_feedback = pd.DataFrame(scaler.transform(attacked_feedback_df[feature_cols]), columns=feature_cols)

        # evaluate
        metrics = evaluate_at_threshold(current_model, X_holdout, y_holdout, fixed_thresholds[state_key])
        results.append({
            'round': round_num,
            'attacker': sa_attacker.name,
            'model': model_name,
            'recall': metrics['recall'],
            'f1_score': metrics['f1_score'],
            'precision': metrics['precision'],
            'roc_auc': metrics['roc_auc']
        })

        # learn from detected attacks
        predictions = predict(current_model, X_feedback)
        detected = attacked_feedback_df[(attacked_feedback_df['is_fraud'] == 1) & (predictions == 1)]
        current_train_df = pd.concat([current_train_df, detected]).drop_duplicates(subset='Transaction_id')
        training_states[state_key] = current_train_df # Save it back

        # retrain
        X_train_new = pd.DataFrame(scaler.transform(current_train_df[feature_cols]), columns=feature_cols)
        y_train_new = current_train_df['is_fraud']
        current_model.fit(X_train_new, y_train_new)
        model_states[state_key] = current_model

    if round_num > 0:
        equilibrium = True
        for attacker in static_attackers:
            curr = np.mean([r['recall'] for r in results if r['round'] == round_num and r['attacker'] == attacker.name])
            prev = np.mean([r['recall'] for r in results if r['round'] == round_num - 1 and r['attacker'] == attacker.name])
            if abs(curr - prev) >= 0.005:
                equilibrium = False
                break
        if equilibrium:
            print(f"\nEquilibrium reached at Round {round_num + 1}!")
            break

# save results
results_df = pd.DataFrame(results)
results_df.to_csv('results/retraining_results.csv', index=False)
print("Retraining results saved!")