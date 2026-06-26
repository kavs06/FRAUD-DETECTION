from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    results = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "avg_precision": average_precision_score(y_test, y_proba),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred, target_names=["Not Fraud", "Fraud"]),
        "y_pred": y_pred,
        "y_proba": y_proba,
    }
    return results


def plot_confusion_matrix(cm):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d",
                xticklabels=["Not Fraud", "Fraud"],
                yticklabels=["Not Fraud", "Fraud"],
                linewidths=0.5, linecolor="white")
    plt.title("Confusion Matrix", fontweight="bold")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.show()


def classification_report_summary(report):
    print("Full Classification Report:")
    print(report)


def threshold_analysis(y_test, y_proba, thresholds):
    results = []
    for thresh in thresholds:
        y_pred_t = (y_proba >= thresh).astype(int)
        results.append({
            "threshold": thresh,
            "precision": precision_score(y_test, y_pred_t, zero_division=0),
            "recall": recall_score(y_test, y_pred_t),
            "f1": f1_score(y_test, y_pred_t),
            "caught_fraud": y_pred_t[y_test == 1].sum(),
            "total_fraud": (y_test == 1).sum(),
        })
    return results


def roc_curve_plot(y_test, y_proba):
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, color="#4C9BE8", linewidth=2.5,
             label=f"AUC = {auc:.3f}")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1)
    plt.fill_between(fpr, tpr, alpha=0.1, color="#4C9BE8")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve", fontsize=13, fontweight="bold")
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.show()


def precision_recall_curve_plot(y_test, y_proba):
    precision_curve, recall_curve, thresholds = precision_recall_curve(y_test, y_proba)
    ap_score = average_precision_score(y_test, y_proba)
    plt.figure(figsize=(7, 5))
    plt.plot(recall_curve, precision_curve, color="#E84C4C", linewidth=2.5,
             label=f"AP = {ap_score:.3f}")
    plt.axhline(y=y_test.mean(), color="gray", linestyle="--", linewidth=1,
                label=f"Baseline (AP = {y_test.mean():.3f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve", fontsize=13, fontweight="bold")
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
