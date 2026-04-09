"""
Adversarial attacker framework for evasion attacks on fraud detection models.

Implements a polymorphic class hierarchy where each attacker targets specific
behavioural features. All perturbations operate on raw transaction fields
(amount, timestamp, category) before feature engineering runs.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from pipeline.feature_engineering import compute_features
import warnings 
warnings.filterwarnings('ignore', category=FutureWarning)

class BaseAttacker(ABC):
    """Abstract base class for all evasion attackers.

    Handles the common logic of iterating through transactions per user,
    maintaining a legitimate transaction history, and only perturbing
    fraudulent transactions while passing legitimate ones through unchanged.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        pass

    def attack(self, transaction: pd.DataFrame) -> pd.DataFrame:
        transaction = transaction.sort_values('Timestamp').reset_index(drop=True)
        
        # group by user and apply perturbation
        def perturb_group(group):
            user_history = []
            perturbed_rows = []
            for _, row in group.iterrows():
                if row['is_fraud'] == 0:
                    perturbed_rows.append(row.to_dict())
                    user_history.append(row.to_dict())
                    continue
                else:
                    perturbed_row = self.perturb_transaction(row.to_dict(), user_history)
                    perturbed_rows.append(perturbed_row)
            return pd.DataFrame(perturbed_rows)

        perturbed_transaction = transaction.groupby('user_id').apply(perturb_group).reset_index(drop=True)
        return perturbed_transaction

class AmountScalingAttacker(BaseAttacker):
    def __init__(self, scale_factor: float = 0.9):
        super().__init__(name='amount_scaling')
        self.scale_factor = scale_factor

    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        txn = txn.copy()

        if not user_history:
            return txn
        
        amount = [h['Transaction amount'] for h in user_history]
        mean_amount = np.mean(amount)
        
        noise = np.random.normal(0, 0.12 * mean_amount)
        txn['Transaction amount'] = max(0, mean_amount * self.scale_factor + noise)

        return txn
    
class TimeShiftAttacker(BaseAttacker):
    def __init__(self):
        super().__init__(name='time_shift')

    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        txn = txn.copy()
        hour = pd.to_datetime(txn['Timestamp']).hour
        
        if hour in [0, 1, 2, 3, 4, 5]:  
            # night fraud - shift to daytime
            shift_seconds = (7 - hour) * 3600
        else:
            # day fraud
            shift_seconds = np.random.randint(-3600, 3600)

        new_time = pd.to_datetime(txn['Timestamp']) + pd.Timedelta(seconds=shift_seconds)
        txn['Timestamp'] = new_time.strftime('%Y-%m-%d %H:%M:%S')
        return txn
    
class CategoryMimicryAttacker(BaseAttacker):
    def __init__(self):
        super().__init__(name='category_mimicry')

    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        txn = txn.copy()

        if not user_history:
            return txn
        
        seen_categories = set(h['merchant_category'] for h in user_history)
        txn['merchant_category'] = np.random.choice(list(seen_categories))

        return txn
    
class VelocitySpacingAttacker(BaseAttacker):
    def __init__(self, min_gap_seconds: int = 4000):
        super().__init__(name='velocity_spacing')
        self.min_gap_seconds = min_gap_seconds

    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        txn = txn.copy()

        if not user_history:
            return txn
        
        # find the most recent transaction time
        last_txn_time = pd.to_datetime(user_history[-1]['Timestamp'])
        current_txn_time = pd.to_datetime(txn['Timestamp'])
        gap = (current_txn_time - last_txn_time).total_seconds()

        # if transactions are too close to the last one, space it out
        if gap < self.min_gap_seconds:
            new_time = last_txn_time + pd.Timedelta(seconds=self.min_gap_seconds)
            txn['Timestamp'] = new_time.strftime('%Y-%m-%d %H:%M:%S')

        return txn
    
class CombinedAttacker(BaseAttacker):

    def __init__(self):
        super().__init__(name='combined')
        self.amount_scaling_attacker = AmountScalingAttacker()
        self.time_shift_attacker = TimeShiftAttacker()
        self.category_mimicry_attacker = CategoryMimicryAttacker()
        self.velocity_spacing_attacker = VelocitySpacingAttacker()

    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        txn = txn.copy()

        txn = self.amount_scaling_attacker.perturb_transaction(txn, user_history)
        txn = self.time_shift_attacker.perturb_transaction(txn, user_history)
        txn = self.category_mimicry_attacker.perturb_transaction(txn, user_history)
        txn = self.velocity_spacing_attacker.perturb_transaction(txn, user_history)

        return txn
    
class ScoreAwareAttacker(BaseAttacker):
    """An adaptive attacker that uses the model's predicted probabilities to guide its perturbations."""
    def __init__(self, base_attacker, model, scaler, feature_cols):
        super().__init__(name=f'score_aware_{base_attacker.name}')
        self.base_attacker = base_attacker
        self.model = model
        self.scaler = scaler
        self.feature_cols = feature_cols

    def update_model(self, model):
        """Update the queried model - called after each retraining round"""
        self.model = model
    
    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        original_score = self._get_score(txn, user_history)
        perturbed_txn = self.base_attacker.perturb_transaction(txn, user_history)
        perturbed_score = self._get_score(perturbed_txn, user_history)

        # only commit if perturbation reduces the score
        if perturbed_score < original_score:
            return perturbed_txn
        else:
            return txn
        
    def _get_score(self, txn: dict, user_history: list) -> float:
        """Compute the model's fraud probability for a given transaction"""
        txn = txn.copy()
        txn['Timestamp'] = pd.to_datetime(txn['Timestamp'])
        txn.setdefault('user_id', 'unknown')
        txn.setdefault('fraud_campaign', None)

        converted_history = []
        for h in user_history:
            h_copy = h.copy()
            h_copy['Timestamp'] = pd.to_datetime(h_copy['Timestamp'])
            converted_history.append(h_copy)
            
        features = compute_features(txn, converted_history)
        feature_vector = pd.DataFrame([[features.get(col, 0) for col in self.feature_cols]], columns=self.feature_cols)
        scaled = pd.DataFrame(self.scaler.transform(feature_vector), columns=self.feature_cols)
        return self.model.predict_proba(scaled)[0][1]
        