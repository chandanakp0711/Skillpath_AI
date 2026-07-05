"""
===============================================================================
 model_training.py  --  Train, evaluate, compare & persist ML models
===============================================================================
Trains the classifiers required by the spec, compares them with a consistent
evaluation protocol, auto-selects the best one and serialises every artefact
the Streamlit app needs at inference time.

Models
------
    * Logistic Regression          (linear baseline)
    * Decision Tree                (interpretable non-linear)
    * Random Forest                (bagged ensemble)
    * Gradient Boosting            (boosted ensemble, sklearn)
    * XGBoost                      (optional — only if the package is present)

Evaluation
----------
    Accuracy · Precision · Recall · F1 (weighted) · Confusion matrix ·
    5-fold stratified cross-validation (F1-weighted).

The "best" model is chosen by mean cross-validation F1 (robust to a single
lucky/unlucky test split), then refit on the full dataset before saving.
===============================================================================
"""

from __future__ import annotations

import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from . import config
from .data_loader import load_clean
from .preprocessing import featurize, get_feature_columns, run_preprocessing
from .target_engineering import engineer_targets

# XGBoost is optional — degrade gracefully if it is not installed.
try:
    from xgboost import XGBClassifier
    _HAS_XGB = True
except Exception:  # pragma: no cover
    _HAS_XGB = False


# --------------------------------------------------------------------------- #
#  Model zoo
# --------------------------------------------------------------------------- #
def build_models() -> dict[str, Pipeline]:
    """Return {name: sklearn Pipeline(StandardScaler -> classifier)}."""
    rs = config.RANDOM_STATE
    models: dict[str, Pipeline] = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, C=1.0, random_state=rs)),
        ]),
        "Decision Tree": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", DecisionTreeClassifier(max_depth=12, min_samples_leaf=5,
                                           random_state=rs)),
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            # max_features=0.6 lets each split see most features — important here
            # because the target is driven by a few strong categorical signals
            # (career interest, course) that aggressive subsampling would dilute.
            ("clf", RandomForestClassifier(n_estimators=400, max_depth=None,
                                           min_samples_leaf=1, max_features=0.6,
                                           n_jobs=-1, random_state=rs)),
        ]),
        "Gradient Boosting": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(n_estimators=300, max_depth=3,
                                               learning_rate=0.1, random_state=rs)),
        ]),
    }
    if _HAS_XGB:
        models["XGBoost"] = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", XGBClassifier(
                n_estimators=400, max_depth=5, learning_rate=0.1,
                subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
                objective="multi:softprob", tree_method="hist",
                eval_metric="mlogloss", random_state=rs, n_jobs=-1,
            )),
        ])
    return models


# --------------------------------------------------------------------------- #
#  Dataset assembly
# --------------------------------------------------------------------------- #
def build_dataset():
    """Load -> engineer target -> preprocess -> featurise. Returns (df, X, y)."""
    df = engineer_targets(load_clean())
    df = run_preprocessing(df)
    X = featurize(df)
    y = df["recommended_career"].values
    return df, X, y


# --------------------------------------------------------------------------- #
#  Training / evaluation
# --------------------------------------------------------------------------- #
def evaluate_model(pipe, X_train, X_test, y_train, y_test, X_all, y_all) -> dict:
    """Fit on train, score on test, and run 5-fold CV on the full data."""
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)
    cv_scores = cross_val_score(pipe, X_all, y_all, cv=cv,
                                scoring="f1_weighted", n_jobs=-1)

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "cv_f1_mean": float(cv_scores.mean()),
        "cv_f1_std": float(cv_scores.std()),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "y_pred": y_pred,
    }


def feature_importance(pipe, feature_names: list[str]) -> dict[str, float]:
    """Extract importances (trees) or |coef| magnitude (linear) from a pipeline."""
    clf = pipe.named_steps["clf"]
    if hasattr(clf, "feature_importances_"):
        imp = np.asarray(clf.feature_importances_, dtype=float)
    elif hasattr(clf, "coef_"):
        imp = np.abs(np.asarray(clf.coef_, dtype=float)).mean(axis=0)
    else:  # pragma: no cover
        return {}
    imp = imp / imp.sum() if imp.sum() else imp
    return {name: float(v) for name, v in zip(feature_names, imp)}


def train_and_select(verbose: bool = True) -> dict:
    """Run the whole training pipeline and persist the best model + artefacts."""
    t0 = time.time()
    df, X, y = build_dataset()
    feature_names = get_feature_columns()

    # Encode string labels -> integers (uniform across all models incl. XGBoost)
    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.20, stratify=y_enc, random_state=config.RANDOM_STATE
    )

    models = build_models()
    results: dict[str, dict] = {}
    class_names = list(label_encoder.classes_)

    for name, pipe in models.items():
        if verbose:
            print(f"  - Training {name} ...", flush=True)
        res = evaluate_model(pipe, X_train, X_test, y_train, y_test, X, y_enc)
        # Human-readable per-class report on the test split.
        report = classification_report(
            y_test, res.pop("y_pred"),
            labels=range(len(class_names)), target_names=class_names,
            output_dict=True, zero_division=0,
        )
        res["per_class"] = report
        res["pipeline"] = pipe
        results[name] = res
        if verbose:
            print(f"      acc={res['accuracy']:.3f}  f1={res['f1']:.3f}  "
                  f"cv_f1={res['cv_f1_mean']:.3f}+/-{res['cv_f1_std']:.3f}")

    # --- pick the best by mean CV F1 ------------------------------------- #
    best_name = max(results, key=lambda n: results[n]["cv_f1_mean"])
    best_pipe = results[best_name]["pipeline"]

    # Refit the winner on the FULL dataset for production use.
    best_pipe.fit(X, y_enc)
    importances = feature_importance(best_pipe, feature_names)

    # --- persist artefacts ----------------------------------------------- #
    joblib.dump(best_pipe, config.MODEL_PATH)
    joblib.dump(label_encoder, config.LABEL_ENCODER_PATH)
    joblib.dump(feature_names, config.FEATURE_COLUMNS_PATH)

    metrics_out = {
        "best_model": best_name,
        "selection_metric": "cv_f1_mean",
        "classes": class_names,
        "feature_importance": dict(sorted(importances.items(),
                                          key=lambda kv: kv[1], reverse=True)),
        "models": {
            name: {k: v for k, v in res.items() if k != "pipeline"}
            for name, res in results.items()
        },
    }
    with open(config.METRICS_PATH, "w", encoding="utf-8") as fh:
        json.dump(metrics_out, fh, indent=2)

    metadata = {
        "n_samples": int(len(df)),
        "n_features": len(feature_names),
        "n_classes": len(class_names),
        "classes": class_names,
        "label_distribution": df["recommended_career"].value_counts().to_dict(),
        "test_size": 0.20,
        "random_state": config.RANDOM_STATE,
        "xgboost_available": _HAS_XGB,
        "train_seconds": round(time.time() - t0, 1),
        "models_trained": list(results.keys()),
    }
    with open(config.METADATA_PATH, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    if verbose:
        print(f"\n  [OK] Best model: {best_name} "
              f"(cv_f1={results[best_name]['cv_f1_mean']:.3f})")
        print(f"  [OK] Artefacts saved to {config.MODELS_DIR}")
        print(f"  [OK] Finished in {metadata['train_seconds']}s")

    return {"best_name": best_name, "results": results,
            "metrics": metrics_out, "metadata": metadata}


if __name__ == "__main__":  # pragma: no cover
    train_and_select(verbose=True)
