"""
===============================================================================
 skill_gap.py  --  Skill-gap detection & explanation engine
===============================================================================
Given a student profile and a target career, this module identifies — with a
plain-English explanation for each finding:

    * Missing technical skills        * Strength areas
    * Missing programming languages    * Weak areas
    * Missing soft skills              * Recommended certifications
    * Missing project experience       * Overall fit / readiness gap

Everything is derived deterministically from the career requirement profiles in
config.CAREERS and the readiness pillar breakdown, so the guidance is fully
transparent and reproducible.
===============================================================================
"""

from __future__ import annotations

from . import config
from .readiness import career_match, compute_readiness

# Friendly labels for the readiness pillars.
PILLAR_LABELS = {
    "technical": "Technical skills",
    "programming": "Programming languages",
    "soft": "Soft skills",
    "projects": "Project experience",
    "alignment": "Career alignment",
}

STRONG_THRESHOLD = 0.72   # pillar raw score considered a strength
WEAK_THRESHOLD = 0.50     # pillar raw score considered a weakness


def _missing_and_have(required: dict[str, float], have: set[str]):
    """Split a weighted requirement dict into (missing, have) lists by weight."""
    ordered = sorted(required.items(), key=lambda kv: kv[1], reverse=True)
    missing = [s for s, _ in ordered if s not in have]
    present = [s for s, _ in ordered if s in have]
    return missing, present


def analyze_skill_gap(profile: dict, career: str) -> dict:
    """
    Produce a complete skill-gap report for ``career``.

    Returns a dict with missing/strength lists, recommended certifications,
    project guidance, weak/strong pillars, a fit %, the readiness gap to
    "Industry Ready", and a list of human-readable explanations.
    """
    spec = config.CAREERS[career]
    tech_have = set(profile["technical_list"])
    lang_have = set(profile["language_list"])
    soft_have = set(profile["soft_list"])

    miss_tech, have_tech = _missing_and_have(spec["tech"], tech_have)
    miss_lang, have_lang = _missing_and_have(spec["lang"], lang_have)
    miss_soft, have_soft = _missing_and_have(spec["soft"], soft_have)

    match = career_match(profile, career)
    readiness = compute_readiness(profile)

    # Weak / strong pillars from the readiness breakdown.
    strengths, weaknesses = [], []
    for pillar, info in readiness["pillars"].items():
        label = PILLAR_LABELS[pillar]
        if info["raw"] >= STRONG_THRESHOLD:
            strengths.append(label)
        elif info["raw"] < WEAK_THRESHOLD:
            weaknesses.append(label)

    # Project gap.
    has_projects = profile["has_projects"] == "Yes"
    missing_projects = not has_projects

    # Readiness gap to the "Industry Ready" threshold (81).
    industry_ready_floor = 81
    readiness_gap = max(0, industry_ready_floor - readiness["score"])

    # --- Build human-readable explanations ------------------------------- #
    explanations: list[str] = []
    explanations.append(
        f"Your profile covers **{match['overall']*100:.0f}%** of the core "
        f"requirements for a **{career}**."
    )
    if miss_tech:
        explanations.append(
            f"To strengthen your technical foundation, focus on "
            f"**{', '.join(miss_tech)}** — these are core to this role."
        )
    else:
        explanations.append(
            "You already cover the key technical skills for this role — excellent!"
        )
    if miss_lang:
        explanations.append(
            f"Add **{', '.join(miss_lang)}** to your programming toolkit."
        )
    if miss_soft:
        explanations.append(
            f"Develop these soft skills to stand out: **{', '.join(miss_soft)}**."
        )
    if missing_projects:
        explanations.append(
            "You have **no project experience** recorded — building 2-3 portfolio "
            "projects is the single fastest way to boost your readiness."
        )
    if weaknesses:
        explanations.append(
            f"Your weakest areas right now are **{', '.join(weaknesses)}** — "
            f"prioritise these in your learning plan."
        )
    if strengths:
        explanations.append(
            f"Keep leveraging your strengths in **{', '.join(strengths)}**."
        )
    if readiness_gap > 0:
        explanations.append(
            f"You are **{readiness_gap:.0f} points** away from the "
            f"'Industry Ready' band (81+). The roadmap below closes that gap."
        )
    else:
        explanations.append(
            "You are already in the 'Industry Ready' band — focus on depth, "
            "certifications and interview practice."
        )

    return {
        "career": career,
        "fit_pct": round(match["overall"] * 100, 1),
        "match_detail": {k: round(v * 100, 1) for k, v in match.items()},
        "missing_technical": miss_tech,
        "have_technical": have_tech,
        "missing_languages": miss_lang,
        "have_languages": have_lang,
        "missing_soft": miss_soft,
        "have_soft": have_soft,
        "recommended_certifications": spec["certifications"],
        "missing_projects": missing_projects,
        "suggested_projects": spec["projects"],
        "strength_areas": strengths,
        "weak_areas": weaknesses,
        "readiness_score": readiness["score"],
        "readiness_band": readiness["band"],
        "readiness_gap": round(readiness_gap, 1),
        "explanations": explanations,
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    from .readiness import make_profile
    import json

    demo = make_profile(
        technical_list=["Python", "SQL"],
        language_list=["Python"],
        soft_list=["Communication"],
        technical_rating=3, soft_rating=2, has_projects="No",
        career_interest="Data Scientist", course="B.Sc Data Science",
    )
    report = analyze_skill_gap(demo, "Data Scientist")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "explanations"}, indent=2))
    print("\nExplanations:")
    for e in report["explanations"]:
        print(" -", e)
