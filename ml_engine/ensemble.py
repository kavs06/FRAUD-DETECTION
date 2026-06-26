import joblib
import numpy as np


def load_models(logistic_path, rf_path, xgb_path):
    models = {
        "lr": joblib.load(logistic_path),
        "rf": joblib.load(rf_path),
        "xgb": joblib.load(xgb_path),
    }
    return models


def ensemble_predict(models, X):
    preds = np.column_stack([
        models["lr"].predict(X),
        models["rf"].predict(X),
        models["xgb"].predict(X),
    ])
    votes = np.sum(preds, axis=1)
    return (votes >= 2).astype(int)


def ensemble_predict_proba(models, X):
    probs = np.column_stack([
        models["lr"].predict_proba(X)[:, 1],
        models["rf"].predict_proba(X)[:, 1],
        models["xgb"].predict_proba(X)[:, 1],
    ])
    return np.mean(probs, axis=1)


def weighted_voting(models, X, weights=None):
    if weights is None:
        weights = {"lr": 1.0, "rf": 1.0, "xgb": 1.0}

    probs = np.column_stack([
        weights["lr"] * models["lr"].predict_proba(X)[:, 1],
        weights["rf"] * models["rf"].predict_proba(X)[:, 1],
        weights["xgb"] * models["xgb"].predict_proba(X)[:, 1],
    ])
    avg_probs = np.sum(probs, axis=1) / sum(weights.values())
    return (avg_probs >= 0.5).astype(int)


def load_all_models(logistic_path, rf_path, xgb_path):
    return load_models(logistic_path, rf_path, xgb_path)
