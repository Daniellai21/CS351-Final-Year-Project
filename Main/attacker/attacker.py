import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import warnings 
warnings.filterwarnings('ignore', category=FutureWarning)

class BaseAttacker(ABC):
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
    
class CombinedAttacker(BaseAttacker):

    def __init__(self):
        super().__init__(name='combined')
        self.amount_scaling_attacker = AmountScalingAttacker()
        self.time_shift_attacker = TimeShiftAttacker()
        self.category_mimicry_attacker = CategoryMimicryAttacker()

    def perturb_transaction(self, txn: dict, user_history: list) -> dict:
        txn = txn.copy()

        txn = self.amount_scaling_attacker.perturb_transaction(txn, user_history)
        txn = self.time_shift_attacker.perturb_transaction(txn, user_history)
        txn = self.category_mimicry_attacker.perturb_transaction(txn, user_history)

        return txn