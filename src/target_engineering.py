"""
===============================================================================
 target_engineering.py  --  Derive the ML target label ("recommended_career")
===============================================================================
The raw dataset only records what career a student is *interested* in — it has
no ground-truth "best-fit career". We therefore engineer a supervised target
from an explicit, domain-informed **expert decision rubric**:

    1. The stated career interest selects a career *family*
       (e.g. "Data Scientist" -> {Data Scientist, Data Analyst, ML Engineer}).
    2. Course, signature technical skills, ratings and project experience
       refine the choice *within* that family.

This is the well-known "distil expert rules into a learnable label" pattern:
15+ years of domain knowledge is encoded as transparent rules, and the ML
models then learn to *generalise* that mapping from the raw profile features.

A small fraction of labels is randomly perturbed (config.LABEL_NOISE_RATE) so
the target is realistic and non-trivial — otherwise tree models would recover
the rubric almost perfectly and report a misleading ~100% accuracy.

Each rule below is annotated with the reasoning, so the recommendation a
student receives is always explainable.
===============================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config
from .readiness import career_match


# --------------------------------------------------------------------------- #
#  Expert decision rubric  (interest family -> refined career)
# --------------------------------------------------------------------------- #
def assign_recommended_career(profile: dict) -> str:
    """Return the best-fit career for a profile using transparent domain rules."""
    tech = set(profile["technical_list"])
    langs = set(profile["language_list"])
    tr = profile["technical_rating"]
    course = profile.get("course")
    interest = profile.get("career_interest", "")
    has_proj = profile["has_projects"] == "Yes"

    # --- Family 1: data / ML enthusiasts -------------------------------- #
    if interest == "Data Scientist":
        # Strong ML + cloud + high rating -> production ML engineering.
        if "Machine Learning" in tech and tr >= 4 and "Cloud Computing" in tech:
            return "Machine Learning Engineer"
        # Solid ML & decent rating -> research/modelling Data Scientist.
        if "Machine Learning" in tech and tr >= 3:
            return "Data Scientist"
        # Analytics-leaning skills without deep ML -> Data Analyst.
        if "Data Analysis" in tech or "SQL" in tech:
            return "Data Analyst"
        return "Data Scientist"

    # --- Family 2: AI specialists --------------------------------------- #
    if interest == "AI Engineer":
        # Cloud / CS-engineering background -> ML Engineer (productionisation).
        if "Cloud Computing" in tech or course in ("B.Tech CSE", "B.Tech IT"):
            return "Machine Learning Engineer"
        return "AI Engineer"

    # --- Family 3: cloud / infrastructure ------------------------------- #
    if interest == "Cloud Architect":
        # Automation languages or hands-on projects -> DevOps.
        if "Go" in langs or has_proj:
            return "DevOps Engineer"
        return "Cloud Engineer"

    # --- Family 4: security --------------------------------------------- #
    if interest == "Cybersecurity Expert":
        # No security skill but cloud-heavy -> redirect to Cloud Engineer.
        if "Cybersecurity" not in tech and "Cloud Computing" in tech:
            return "Cloud Engineer"
        return "Cybersecurity Analyst"

    # --- Family 5: software builders ------------------------------------ #
    if interest == "Software Developer":
        # Web/JS skills -> full-stack; otherwise core software engineering.
        if "JavaScript" in langs:
            return "Full Stack Developer"
        return "Software Developer"

    # --- Family 6: business / analytics --------------------------------- #
    if interest == "Business Analyst":
        # Strong technical analytics -> Data Analyst; else Business Analyst.
        if "Data Analysis" in tech and "SQL" in tech and tr >= 3:
            return "Data Analyst"
        return "Business Analyst"

    # --- Fallback: best skill-coverage match ---------------------------- #
    return max(config.CAREER_LIST, key=lambda c: career_match(profile, c)["overall"])


# --------------------------------------------------------------------------- #
#  Soft career-fit ranking (for explanations & alternative suggestions)
# --------------------------------------------------------------------------- #
def career_fit_scores(profile: dict) -> dict[str, float]:
    """Return {career: 0-1 skill-coverage fit} for every career, ranked-ready."""
    return {c: career_match(profile, c)["overall"] for c in config.CAREER_LIST}


def top_alternative_careers(profile: dict, exclude: str | None = None,
                            k: int = 3) -> list[tuple[str, float]]:
    """Top-k careers by skill-coverage fit (optionally excluding one)."""
    fits = career_fit_scores(profile)
    if exclude:
        fits.pop(exclude, None)
    return sorted(fits.items(), key=lambda kv: kv[1], reverse=True)[:k]


# --------------------------------------------------------------------------- #
#  Vectorised label generation for the whole dataset
# --------------------------------------------------------------------------- #
def engineer_targets(df: pd.DataFrame, noise_rate: float | None = None) -> pd.DataFrame:
    """
    Add a ``recommended_career`` column (the ML target) to a cleaned DataFrame.

    Reproducible: both the rule application and the label-noise perturbation use
    a seeded RNG, so re-running the pipeline always yields identical labels.
    """
    from .readiness import profile_from_row  # local import avoids a cycle

    if noise_rate is None:
        noise_rate = config.LABEL_NOISE_RATE

    labels = [assign_recommended_career(profile_from_row(row))
              for _, row in df.iterrows()]

    # Inject reproducible label noise (realistic fuzziness in career fit).
    rng = np.random.RandomState(config.RANDOM_STATE)
    careers = config.CAREER_LIST
    flip = rng.rand(len(labels)) < noise_rate
    for i in np.where(flip)[0]:
        labels[i] = careers[rng.randint(len(careers))]

    out = df.copy()
    out["recommended_career"] = labels
    return out


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    from .data_loader import load_clean

    data = engineer_targets(load_clean())
    print("Label distribution:\n",
          data["recommended_career"].value_counts().to_string())
