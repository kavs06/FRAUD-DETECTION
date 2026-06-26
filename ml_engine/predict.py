import joblib


def load_models(logistic_path, rf_path=None, xgb_path=None):
    models = {
        "lr": joblib.load(logistic_path)
    }
    if rf_path:
        models["rf"] = joblib.load(rf_path)
    if xgb_path:
        models["xgb"] = joblib.load(xgb_path)
    return models


def predict_provider(model, X):
    return model.predict(X)


def predict_probability(model, X):
    return model.predict_proba(X)[:, 1]


def predict_single_provider(model, features):
    return model.predict(features)


def predict_single_probability(model, features):
    return model.predict_proba(features)[:, 1]
