"""
===============================================================================
 preprocessing.py  --  Data cleaning, feature engineering & featurisation
===============================================================================
Implements the full preprocessing stage required by the spec:

    * Missing-value handling      -> handle_missing()
    * Duplicate removal           -> remove_duplicates()
    * Outlier detection           -> detect_outliers()
    * Feature engineering         -> add_engineered_features()
    * Feature encoding            -> featurize()  (manual, deterministic)
    * Feature scaling             -> done inside the model Pipeline (train.py)

`featurize()` produces a fully-numeric matrix with a FIXED, config-driven
column order so a single student profile from the Streamlit form is encoded
*identically* to the training data (train/inference parity).
===============================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

# Academic-year ordinal mapping (juniors -> seniors)
YEAR_ORDINAL = {"1st Year": 1, "2nd Year": 2, "3rd Year": 3, "Final Year": 4}

# Numeric columns kept as-is (after engineering) for the model.
NUMERIC_FEATURES = [
    "technical_rating", "soft_rating",
    "n_technical_skills", "n_languages", "n_soft_skills",
    "readiness_score", "year_ordinal", "has_projects_bin",
]

# One-hot categorical columns: (source_column, prefix, catalogue)
ONEHOT_SPECS = [
    ("course", "course", config.COURSES),
    ("career_interest", "interest", config.CAREER_INTERESTS),
    ("learning_challenge", "challenge", config.LEARNING_CHALLENGES),
    ("support_required", "support", config.SUPPORT_OPTIONS),
    ("learning_method", "method", config.LEARNING_METHODS),
]

# Multi-hot columns: (list_column, prefix, catalogue)
MULTIHOT_SPECS = [
    ("technical_list", "tech", config.TECHNICAL_SKILLS),
    ("language_list", "lang", config.PROGRAMMING_LANGUAGES),
    ("soft_list", "soft", config.SOFT_SKILLS),
]


# --------------------------------------------------------------------------- #
#  1. Missing-value handling
# --------------------------------------------------------------------------- #
def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute any missing values:
        * numeric ratings  -> median
        * categoricals     -> mode (most frequent)
        * multi-value text -> empty string
    The shipped dataset is already complete, but a production pipeline must be
    defensive against partially-filled future data.
    """
    df = df.copy()
    for col in ("technical_rating", "soft_rating"):
        if col in df:
            median = int(df[col].median()) if df[col].notna().any() else 3
            df[col] = df[col].fillna(median)
    cat_cols = ["academic_year", "course", "career_interest",
                "learning_challenge", "support_required", "learning_method",
                "has_projects"]
    for col in cat_cols:
        if col in df and df[col].isna().any():
            mode = df[col].mode(dropna=True)
            df[col] = df[col].fillna(mode.iloc[0] if len(mode) else "Unknown")
    for col in ("technical_skills", "programming_languages", "soft_skills"):
        if col in df:
            df[col] = df[col].fillna("")
    return df


# --------------------------------------------------------------------------- #
#  2. Duplicate removal
# --------------------------------------------------------------------------- #
def remove_duplicates(df: pd.DataFrame, report: bool = False):
    """Drop exact duplicate rows (ignoring the PII name/email columns)."""
    subset = [c for c in df.columns
              if c not in config.PII_COLUMNS
              and not isinstance(df[c].iloc[0] if len(df) else None, list)]
    before = len(df)
    deduped = df.drop_duplicates(subset=subset).reset_index(drop=True)
    removed = before - len(deduped)
    if report:
        return deduped, removed
    return deduped


# --------------------------------------------------------------------------- #
#  3. Outlier detection (IQR method)
# --------------------------------------------------------------------------- #
def detect_outliers(df: pd.DataFrame, columns: list[str] | None = None) -> dict:
    """
    Detect outliers in numeric columns using the 1.5*IQR rule and return a
    per-column summary. Ratings are bounded 1-5 so genuine outliers are rare —
    this mainly guards the engineered count/score columns.
    """
    if columns is None:
        columns = [c for c in ("technical_rating", "soft_rating",
                               "n_technical_skills", "n_languages",
                               "n_soft_skills", "readiness_score")
                   if c in df.columns]
    summary = {}
    for col in columns:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (series < low) | (series > high)
        summary[col] = {
            "lower_bound": round(float(low), 2),
            "upper_bound": round(float(high), 2),
            "n_outliers": int(mask.sum()),
            "pct_outliers": round(100 * mask.mean(), 2),
        }
    return summary


def cap_outliers(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Winsorise the given numeric columns to their 1.5*IQR fences."""
    df = df.copy()
    for col in columns:
        if col not in df:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        df[col] = series.clip(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    return df


# --------------------------------------------------------------------------- #
#  4. Feature engineering
# --------------------------------------------------------------------------- #
def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add model-ready engineered columns:
        * readiness_score   (the custom 0-100 score — strong predictor)
        * year_ordinal      (1..4)
        * has_projects_bin  (0/1)
    Count columns (n_technical_skills, ...) are produced by the data loader.
    """
    from .readiness import readiness_for_row  # avoid import cycle

    df = df.copy()
    # Ensure breadth counts exist (when featurising a hand-built inference row).
    if "n_technical_skills" not in df:
        df["n_technical_skills"] = df["technical_list"].apply(len)
    if "n_languages" not in df:
        df["n_languages"] = df["language_list"].apply(len)
    if "n_soft_skills" not in df:
        df["n_soft_skills"] = df["soft_list"].apply(len)

    df["readiness_score"] = df.apply(lambda r: readiness_for_row(r)["score"], axis=1)
    df["year_ordinal"] = df["academic_year"].map(YEAR_ORDINAL).fillna(2).astype(int)
    df["has_projects_bin"] = (df["has_projects"] == "Yes").astype(int)
    return df


# --------------------------------------------------------------------------- #
#  5. Featurisation (encoding) — deterministic column order
# --------------------------------------------------------------------------- #
def get_feature_columns() -> list[str]:
    """The full, fixed list of model feature columns (config-driven)."""
    cols = list(NUMERIC_FEATURES)
    for _src, prefix, catalogue in ONEHOT_SPECS:
        cols += [f"{prefix}__{val}" for val in catalogue]
    for _src, prefix, catalogue in MULTIHOT_SPECS:
        cols += [f"{prefix}__{val}" for val in catalogue]
    return cols


def featurize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode a cleaned + engineered DataFrame into a numeric feature matrix with
    the canonical column order from ``get_feature_columns()``.
    """
    out = pd.DataFrame(index=df.index)

    # Numeric (defensive fill so a sparse inference row never breaks).
    for col in NUMERIC_FEATURES:
        out[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

    # One-hot encode known categories.
    for src, prefix, catalogue in ONEHOT_SPECS:
        values = df.get(src, pd.Series([""] * len(df), index=df.index)).astype(str)
        for cat in catalogue:
            out[f"{prefix}__{cat}"] = (values == cat).astype(int)

    # Multi-hot encode skill lists.
    for src, prefix, catalogue in MULTIHOT_SPECS:
        lists = df.get(src, pd.Series([[]] * len(df), index=df.index))
        for skill in catalogue:
            out[f"{prefix}__{skill}"] = lists.apply(
                lambda lst, s=skill: int(s in lst) if isinstance(lst, (list, set)) else 0
            )

    # Guarantee exact column order.
    return out[get_feature_columns()]


# --------------------------------------------------------------------------- #
#  Convenience: full cleaning pipeline (load -> clean -> engineer)
# --------------------------------------------------------------------------- #
def run_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the complete cleaning + feature-engineering chain to a raw-clean df."""
    df = handle_missing(df)
    df = remove_duplicates(df)
    df = add_engineered_features(df)
    return df


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    from .data_loader import load_clean

    data = run_preprocessing(load_clean())
    X = featurize(data)
    print("Feature matrix:", X.shape)
    print("First 12 columns:", list(X.columns[:12]))
    print("Outliers:", detect_outliers(data))
