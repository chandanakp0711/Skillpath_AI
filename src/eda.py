"""
===============================================================================
 eda.py  --  Exploratory Data Analysis aggregations
===============================================================================
Pure data-crunching helpers that turn the cleaned dataset into the summary
tables/series the dashboard charts consume. Keeping aggregation here (separate
from rendering in visualizations.py) keeps both testable and reusable.

Covers every EDA theme in the spec:
    * Student distribution  (course / year / career interest)
    * Skill analysis        (top technical skills / language popularity / soft)
    * Career readiness      (readiness & band distribution, skill-gap summary)
    * Correlation analysis  (numeric correlation matrix, tech-vs-soft)
===============================================================================
"""

from __future__ import annotations

from collections import Counter

import pandas as pd

from . import config
from .data_loader import load_clean
from .preprocessing import add_engineered_features
from .target_engineering import engineer_targets

# Numeric columns used for correlation analysis (friendly labels).
CORR_FEATURES = {
    "technical_rating": "Tech Rating",
    "soft_rating": "Soft Rating",
    "n_technical_skills": "# Tech Skills",
    "n_languages": "# Languages",
    "n_soft_skills": "# Soft Skills",
    "has_projects_bin": "Has Projects",
    "year_ordinal": "Academic Year",
    "readiness_score": "Readiness",
}


# --------------------------------------------------------------------------- #
#  Analysis frame (clean + engineered + target), built once
# --------------------------------------------------------------------------- #
def build_analysis_frame() -> pd.DataFrame:
    """Cleaned dataset enriched with readiness, target label & numeric helpers."""
    df = engineer_targets(load_clean())
    df = add_engineered_features(df)
    from .readiness import readiness_for_row
    res = df.apply(lambda r: readiness_for_row(r), axis=1)
    df["readiness_band"] = res.apply(lambda d: d["band"])
    return df


# --------------------------------------------------------------------------- #
#  Counters for multi-value skill columns
# --------------------------------------------------------------------------- #
def _count_tokens(df: pd.DataFrame, list_col: str) -> pd.Series:
    counter: Counter = Counter()
    for items in df[list_col]:
        counter.update(items)
    return pd.Series(counter).sort_values(ascending=False)


# --------------------------------------------------------------------------- #
#  Student distribution
# --------------------------------------------------------------------------- #
def course_distribution(df: pd.DataFrame) -> pd.Series:
    return df["course"].value_counts()


def year_distribution(df: pd.DataFrame) -> pd.Series:
    order = config.ACADEMIC_YEARS
    return df["academic_year"].value_counts().reindex(order).fillna(0).astype(int)


def career_interest_distribution(df: pd.DataFrame) -> pd.Series:
    return df["career_interest"].value_counts()


# --------------------------------------------------------------------------- #
#  Skill analysis
# --------------------------------------------------------------------------- #
def top_technical_skills(df: pd.DataFrame) -> pd.Series:
    return _count_tokens(df, "technical_list")


def language_popularity(df: pd.DataFrame) -> pd.Series:
    return _count_tokens(df, "language_list")


def soft_skill_distribution(df: pd.DataFrame) -> pd.Series:
    return _count_tokens(df, "soft_list")


# --------------------------------------------------------------------------- #
#  Career readiness
# --------------------------------------------------------------------------- #
def readiness_band_distribution(df: pd.DataFrame) -> pd.Series:
    order = [b[2] for b in config.READINESS_BANDS]
    return df["readiness_band"].value_counts().reindex(order).fillna(0).astype(int)


def recommended_career_distribution(df: pd.DataFrame) -> pd.Series:
    return df["recommended_career"].value_counts()


def skill_gap_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dataset-level skill-gap: for each readiness pillar, the average points
    students earn vs the maximum possible. The "gap" column highlights where
    students collectively fall short — a clear bar-chart story.
    """
    from .readiness import readiness_for_row
    rows = df.apply(lambda r: readiness_for_row(r)["pillars"], axis=1)
    records = []
    label_map = {
        "technical": "Technical Skills",
        "programming": "Programming",
        "soft": "Soft Skills",
        "projects": "Projects",
        "alignment": "Career Alignment",
    }
    for pillar, label in label_map.items():
        avg_points = float(pd.Series([p[pillar]["points"] for p in rows]).mean())
        max_points = config.READINESS_WEIGHTS[pillar] * 100
        records.append({
            "pillar": label,
            "avg_points": round(avg_points, 1),
            "max_points": round(max_points, 1),
            "gap": round(max_points - avg_points, 1),
            "attainment_pct": round(100 * avg_points / max_points, 1),
        })
    return pd.DataFrame(records)


# --------------------------------------------------------------------------- #
#  Correlation analysis
# --------------------------------------------------------------------------- #
def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in CORR_FEATURES if c in df.columns]
    corr = df[cols].corr(numeric_only=True)
    corr = corr.rename(index=CORR_FEATURES, columns=CORR_FEATURES)
    return corr


def tech_vs_soft(df: pd.DataFrame) -> pd.DataFrame:
    """Per-student technical vs soft composite (for the scatter plot)."""
    out = pd.DataFrame({
        "technical": df["technical_rating"] * df["n_technical_skills"],
        "soft": df["soft_rating"] * df["n_soft_skills"],
        "readiness": df["readiness_score"],
        "career_interest": df["career_interest"],
        "has_projects": df["has_projects"],
    })
    return out


def dataset_overview(df: pd.DataFrame) -> dict:
    """Headline KPIs for the dashboard hero cards."""
    return {
        "n_students": int(len(df)),
        "n_courses": int(df["course"].nunique()),
        "n_careers": int(df["recommended_career"].nunique()),
        "avg_readiness": round(float(df["readiness_score"].mean()), 1),
        "pct_with_projects": round(100 * (df["has_projects"] == "Yes").mean(), 1),
        "industry_ready_pct": round(
            100 * (df["readiness_band"] == "Industry Ready").mean(), 1),
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    frame = build_analysis_frame()
    print("Overview:", dataset_overview(frame))
    print("\nTop technical skills:\n", top_technical_skills(frame).head())
    print("\nSkill-gap summary:\n", skill_gap_summary(frame).to_string(index=False))
