import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


def train_logistic_regression(X_train, y_train, random_state=42):
    model = LogisticRegression(max_iter=1000, random_state=random_state)
    model.fit(X_train, y_train)
    return model


def train_random_forest(X_train, y_train, random_state=42):
    model = RandomForestClassifier(random_state=random_state)
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train, random_state=42):
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=random_state)
    model.fit(X_train, y_train)
    return model


def save_model(model, filepath):
    joblib.dump(model, filepath)


def save_scaler(scaler, filepath):
    joblib.dump(scaler, filepath)


def save_feature_names(feature_names, filepath):
    joblib.dump(feature_names, filepath)


def train_all_models(X_train, y_train, random_state=42):
    lr = train_logistic_regression(X_train, y_train, random_state=random_state)
    rf = train_random_forest(X_train, y_train, random_state=random_state)
    xgb = train_xgboost(X_train, y_train, random_state=random_state)
    return lr, rf, xgb


def save_models(models, paths):
    for name, model in models.items():
        joblib.dump(model, paths[name])
