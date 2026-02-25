import joblib
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

def load_model(model_name: str):
    """Load a saved model from results/models/"""
    model_path = f'results/models/{model_name}.pkl'
    return joblib.load(model_path)

def predict(model, X, threshold=0.5):
    """Return binary predictions (0 or 1)"""
    return (predict_proba(model, X) > threshold).astype(int)

def predict_proba(model, X):
    """Return fraud probability scores"""
    return model.predict_proba(X)[:, 1]

def evaluate_model(model, X, y) -> dict:
    """Return dictionary of metrics without printing"""
    y_proba = predict_proba(model, X)
    y_pred = (y_proba > 0.5).astype(int)

    metrics = {
        'precision': precision_score(y, y_pred),
        'recall': recall_score(y, y_pred),
        'f1_score': f1_score(y, y_pred),
        'roc_auc': roc_auc_score(y, y_proba)
    }
    return metrics