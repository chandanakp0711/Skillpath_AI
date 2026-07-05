"""
===============================================================================
 data_loader.py  --  Load & normalise the raw Student Skill-Gap dataset
===============================================================================
The shipped spreadsheet has messy headers (leading spaces, a misspelt
"SOFT_SKILSS", a duplicated "RATING.1"), inconsistent academic-year labels
("Final Year" vs "Final") and multi-valued skill cells. This module turns that
raw file into a clean, analysis-ready DataFrame with canonical column names.
===============================================================================
"""

from __future__ import annotations

import os
import re

import pandas as pd

from . import config


# --------------------------------------------------------------------------- #
#  Year normalisation
# --------------------------------------------------------------------------- #
_YEAR_PATTERNS = [
    (re.compile(r"final", re.I), "Final Year"),
    (re.compile(r"3rd|third|3", re.I), "3rd Year"),
    (re.compile(r"2nd|second|2", re.I), "2nd Year"),
    (re.compile(r"1st|first|1", re.I), "1st Year"),
]


def _normalise_year(value: object) -> str:
    """Map any messy year label onto one of the 4 canonical buckets."""
    text = str(value).strip()
    for pattern, canonical in _YEAR_PATTERNS:
        if pattern.search(text):
            return canonical
    return "Final Year"  # sensible default for unknown labels


def _split_multi(value: object) -> list[str]:
    """Split a comma-separated skill cell into a clean list of tokens."""
    if pd.isna(value):
        return []
    return [tok.strip() for tok in str(value).split(",") if tok.strip()]


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def find_dataset() -> str:
    """Locate the dataset, preferring data/ then the project root."""
    for path in (config.RAW_DATASET_XLSX, config.RAW_DATASET_FALLBACK):
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "Could not find 'skillgap_dataset.xlsx' in data/ or the project root."
    )


def load_raw() -> pd.DataFrame:
    """Read the spreadsheet and apply canonical column names (no row cleaning)."""
    path = find_dataset()
    df = pd.read_excel(path)
    # Strip whitespace from headers, then rename to canonical names.
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns=config.COLUMN_RENAME_MAP)
    return df


def load_clean() -> pd.DataFrame:
    """
    Return a fully cleaned DataFrame:
        * canonical column names
        * normalised academic-year labels
        * trimmed categorical text
        * parsed multi-value skill columns into list[...] helper columns
        * derived count columns (n_technical_skills, etc.)
    The original raw columns are preserved alongside the helpers.
    """
    df = load_raw()

    # --- trim every object column ----------------------------------------- #
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # --- normalise academic year ------------------------------------------ #
    if "academic_year" in df.columns:
        df["academic_year"] = df["academic_year"].apply(_normalise_year)

    # --- normalise the Yes/No projects flag ------------------------------- #
    if "has_projects" in df.columns:
        df["has_projects"] = (
            df["has_projects"].str.strip().str.lower().map({"yes": "Yes", "no": "No"})
        ).fillna("No")

    # --- parse multi-value skill columns ---------------------------------- #
    df["technical_list"] = df["technical_skills"].apply(_split_multi)
    df["language_list"] = df["programming_languages"].apply(_split_multi)
    df["soft_list"] = df["soft_skills"].apply(_split_multi)

    # --- derived breadth counts ------------------------------------------- #
    df["n_technical_skills"] = df["technical_list"].apply(len)
    df["n_languages"] = df["language_list"].apply(len)
    df["n_soft_skills"] = df["soft_list"].apply(len)

    # --- coerce ratings to a clean 1-5 integer range ---------------------- #
    for rating_col in ("technical_rating", "soft_rating"):
        if rating_col in df.columns:
            df[rating_col] = (
                pd.to_numeric(df[rating_col], errors="coerce")
                .fillna(df[rating_col].median() if rating_col in df else 3)
                .clip(1, 5)
                .astype(int)
            )

    return df.reset_index(drop=True)


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    data = load_clean()
    print("Loaded:", data.shape)
    print(data[["academic_year", "course", "technical_rating",
                "n_technical_skills", "career_interest"]].head())
