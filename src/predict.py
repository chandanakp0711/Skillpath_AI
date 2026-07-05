"""
===============================================================================
 predict.py  --  Inference wrapper around the trained model
===============================================================================
Loads the serialised artefacts once and exposes a single high-level function,
``predict_career(profile)``, that the Streamlit app calls. It guarantees
train/inference feature parity by reusing the exact same preprocessing +
featurisation code path as training.

Returns everything the UI needs in one shot:
    * predicted career + confidence
    * full probability distribution over all careers
    * the deterministic readiness score & band
    * top alternative careers (by skill-coverage fit)
===============================================================================
"""

from __future__ import annotations

import os
from functools import lru_cache

import joblib
import pandas as pd

from . import config
from .preprocessing import add_engineered_features, featurize
from .readiness import compute_readiness
from .target_engineering import assign_recommended_career, top_alternative_careers


# --------------------------------------------------------------------------- #
#  Artefact loading (cached)
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def load_artifacts():
    """Load (model, label_encoder, feature_columns). Cached for the process."""
    if not os.path.exists(config.MODEL_PATH):
        raise FileNotFoundError(
            "Model artefacts not found. Run `python train.py` first."
        )
    model = joblib.load(config.MODEL_PATH)
    label_encoder = joblib.load(config.LABEL_ENCODER_PATH)
    feature_columns = joblib.load(config.FEATURE_COLUMNS_PATH)
    return model, label_encoder, feature_columns


def model_is_trained() -> bool:
    """True if the model artefacts exist on disk."""
    return all(os.path.exists(p) for p in
               (config.MODEL_PATH, config.LABEL_ENCODER_PATH,
                config.FEATURE_COLUMNS_PATH))


# --------------------------------------------------------------------------- #
#  Profile -> single-row featurised frame
# --------------------------------------------------------------------------- #
def profile_to_dataframe(profile: dict) -> pd.DataFrame:
    """Build a 1-row DataFrame mirroring the cleaned-dataset schema."""
    row = {
        "academic_year": profile.get("academic_year", "2nd Year"),
        "course": profile.get("course", config.COURSES[0]),
        "technical_rating": int(profile.get("technical_rating", 3)),
        "soft_rating": int(profile.get("soft_rating", 3)),
        "has_projects": "Yes" if str(profile.get("has_projects", "No")).lower().startswith("y") else "No",
        "career_interest": profile.get("career_interest", config.CAREER_INTERESTS[0]),
        "learning_challenge": profile.get("learning_challenge", config.LEARNING_CHALLENGES[0]),
        "support_required": profile.get("support_required", config.SUPPORT_OPTIONS[0]),
        "learning_method": profile.get("learning_method", config.LEARNING_METHODS[0]),
        "technical_list": profile.get("technical_list", []),
        "language_list": profile.get("language_list", []),
        "soft_list": profile.get("soft_list", []),
        "technical_skills": ", ".join(profile.get("technical_list", [])),
        "programming_languages": ", ".join(profile.get("language_list", [])),
        "soft_skills": ", ".join(profile.get("soft_list", [])),
    }
    return pd.DataFrame([row])


# --------------------------------------------------------------------------- #
#  Main inference entry point
# --------------------------------------------------------------------------- #
def predict_career(profile: dict) -> dict:
    """
    Predict the recommended career for a student profile.

    Parameters
    ----------
    profile : dict
        Keys: academic_year, course, technical_list, language_list, soft_list,
        technical_rating, soft_rating, has_projects, career_interest,
        learning_challenge, support_required, learning_method.

    Returns
    -------
    dict with keys: career, confidence (0-1), probabilities (sorted list of
    {career, prob}), readiness (full readiness dict), alternatives, source.
    """
    readiness = compute_readiness(profile)

    if not model_is_trained():
        # Graceful fallback: use the expert rubric directly (no ML model yet).
        career = assign_recommended_career(profile)
        alts = top_alternative_careers(profile, exclude=career, k=3)
        return {
            "career": career,
            "confidence": 0.0,
            "probabilities": [{"career": career, "prob": 1.0}],
            "readiness": readiness,
            "alternatives": [{"career": c, "fit": round(f, 3)} for c, f in alts],
            "source": "rule-based (model not trained)",
        }

    model, label_encoder, feature_columns = load_artifacts()
    df = add_engineered_features(profile_to_dataframe(profile))
    X = featurize(df).reindex(columns=feature_columns, fill_value=0)

    proba = model.predict_proba(X)[0]
    classes = label_encoder.classes_
    ranked = sorted(
        ({"career": c, "prob": float(p)} for c, p in zip(classes, proba)),
        key=lambda d: d["prob"], reverse=True,
    )
    best = ranked[0]
    alts = top_alternative_careers(profile, exclude=best["career"], k=3)

    return {
        "career": best["career"],
        "confidence": best["prob"],
        "probabilities": ranked,
        "readiness": readiness,
        "alternatives": [{"career": c, "fit": round(f, 3)} for c, f in alts],
        "source": "ml-model",
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    from .readiness import make_profile
    import json

    demo = make_profile(
        technical_list=["Python", "Machine Learning", "Cloud Computing", "Data Analysis"],
        language_list=["Python", "R"],
        soft_list=["Problem-Solving", "Communication", "Teamwork"],
        technical_rating=5, soft_rating=4, has_projects="Yes",
        career_interest="Data Scientist", course="M.Tech AI",
        academic_year="Final Year",
    )
    res = predict_career(demo)
    print("Predicted:", res["career"], f"({res['confidence']*100:.1f}%)")
    print("Readiness:", res["readiness"]["score"], res["readiness"]["band"])
    print("Top 3 probs:", json.dumps(res["probabilities"][:3], indent=2))
