import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    auc
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_and_evaluate():
    data_path = os.path.join(DATA_DIR, "orders_dataset.csv")
    df = pd.read_csv(data_path)
    
    print(f"Loaded dataset: {df.shape[0]} samples, {df.shape[1]} columns")
    print(f"Positive class (Returned): {df['returned'].mean():.2%}")
    
    # Feature columns - PRE-PURCHASE SIGNALS ONLY (Zero leakage)
    categorical_features = ["category", "fit_type"]
    numeric_features = [
        "price",
        "size_guide_available",
        "description_completeness",
        "discount_applied",
        "bracketing_order",
        "historical_return_rate",
        "product_size_return_rate"
    ]
    
    feature_cols = categorical_features + numeric_features
    X = df[feature_cols]
    y = df["returned"]
    
    # Stratified Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ]
    )
    
    # Define candidate models
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",
            random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            max_depth=6,
            min_samples_split=4,
            class_weight="balanced",
            random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=120,
            learning_rate=0.08,
            max_depth=4,
            random_state=42
        )
    }
    
    results = {}
    best_model_name = None
    best_f1 = -1.0
    best_pipeline = None
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, clf in models.items():
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        
        # 5-fold cross validation on training data
        cv_f1_scores = cross_val_score(pipeline, X_train, y_train, cv=skf, scoring="f1")
        
        # Train on full train set
        pipeline.fit(X_train, y_train)
        
        # Evaluate on test set
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_prob)
        
        # Precision-Recall AUC
        precisions, recalls, _ = precision_recall_curve(y_test, y_prob)
        pr_auc = auc(recalls, precisions)
        
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        print(f"\n--- {name} ---")
        print(f"  CV F1 Mean: {cv_f1_scores.mean():.4f} (+/- {cv_f1_scores.std():.4f})")
        print(f"  Test Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | ROC-AUC: {roc_auc:.4f} | PR-AUC: {pr_auc:.4f}")
        print(f"  Confusion Matrix: {cm}")
        
        results[name] = {
            "model_name": name,
            "cv_f1_mean": round(float(cv_f1_scores.mean()), 4),
            "cv_f1_std": round(float(cv_f1_scores.std()), 4),
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4),
            "pr_auc": round(float(pr_auc), 4),
            "confusion_matrix": cm,
            "test_sample_count": len(y_test)
        }
        
        # Select best model based on balanced F1 score & ROC-AUC
        score_metric = (f1 * 0.6) + (roc_auc * 0.4)
        if score_metric > best_f1:
            best_f1 = score_metric
            best_model_name = name
            best_pipeline = pipeline

    print(f"\n>>> Best Performing Model: {best_model_name} (Combined Score: {best_f1:.4f})")
    
    # Extract Feature Importances / Coefficients
    feature_names = []
    # numeric features retain names
    feature_names.extend(numeric_features)
    # categorical one-hot feature names
    cat_encoder = best_pipeline.named_steps["preprocessor"].named_transformers_["cat"]
    encoded_cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
    feature_names.extend(encoded_cat_names)
    
    clf_step = best_pipeline.named_steps["classifier"]
    importances = {}
    if hasattr(clf_step, "feature_importances_"):
        raw_imp = clf_step.feature_importances_
        for fn, imp in zip(feature_names, raw_imp):
            importances[fn] = round(float(imp), 4)
    elif hasattr(clf_step, "coef_"):
        raw_imp = np.abs(clf_step.coef_[0])
        # normalize
        raw_imp = raw_imp / np.sum(raw_imp)
        for fn, imp in zip(feature_names, raw_imp):
            importances[fn] = round(float(imp), 4)
            
    # Sort importances
    sorted_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
    
    # Save best model pipeline
    model_save_path = os.path.join(MODELS_DIR, "best_return_risk_model.joblib")
    joblib.dump({
        "pipeline": best_pipeline,
        "feature_cols": feature_cols,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "best_model_name": best_model_name
    }, model_save_path)
    
    # Save metadata and all model benchmarks
    metrics_payload = {
        "trained_at": pd.Timestamp.now().isoformat(),
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features_used": feature_cols,
        "best_model": best_model_name,
        "models_benchmark": results,
        "feature_importances": sorted_importances,
        "synthetic_data_disclaimer": "Trained on synthetic demonstration data following realistic apparel e-commerce distribution patterns. For academic demonstration purposes only."
    }
    
    metrics_save_path = os.path.join(MODELS_DIR, "model_metrics.json")
    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)
        
    print(f"Model saved to: {model_save_path}")
    print(f"Metrics saved to: {metrics_save_path}")

if __name__ == "__main__":
    train_and_evaluate()

