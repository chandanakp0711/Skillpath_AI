"""
===============================================================================
 readiness.py  --  Career-Readiness scoring engine
===============================================================================
Implements the custom, fully-transparent 0-100 readiness score described in the
project specification:

    Technical Skills .... 40%
    Programming Skills .. 20%
    Soft Skills ......... 20%
    Project Experience .. 10%
    Career Alignment .... 10%

The score buckets into 4 bands:
    0-40 Beginner | 41-60 Intermediate | 61-80 Advanced | 81-100 Industry Ready

Everything here is deterministic (no ML) so the number is always explainable to
the student — a key requirement for a guidance tool.
===============================================================================
"""

from __future__ import annotations

from . import config

# "Target" breadths at which a pillar is considered fully covered.
TARGET_TECHNICAL = 4    # 4+ technical skills  -> full breadth
TARGET_LANGUAGES = 3    # 3+ programming langs -> full breadth
TARGET_SOFT = 4         # 4+ soft skills       -> full breadth


# --------------------------------------------------------------------------- #
#  Profile helper
# --------------------------------------------------------------------------- #
def make_profile(
    technical_list: list[str],
    language_list: list[str],
    soft_list: list[str],
    technical_rating: int,
    soft_rating: int,
    has_projects: str,
    career_interest: str,
    course: str | None = None,
    academic_year: str | None = None,
) -> dict:
    """Build the canonical profile dict consumed by every scorer."""
    return {
        "technical_list": list(technical_list),
        "language_list": list(language_list),
        "soft_list": list(soft_list),
        "technical_rating": int(technical_rating),
        "soft_rating": int(soft_rating),
        "has_projects": "Yes" if str(has_projects).lower().startswith("y") else "No",
        "career_interest": career_interest,
        "course": course,
        "academic_year": academic_year,
    }


def profile_from_row(row) -> dict:
    """Extract a profile dict from a cleaned-DataFrame row (see data_loader)."""
    return make_profile(
        technical_list=row.get("technical_list", []),
        language_list=row.get("language_list", []),
        soft_list=row.get("soft_list", []),
        technical_rating=row.get("technical_rating", 3),
        soft_rating=row.get("soft_rating", 3),
        has_projects=row.get("has_projects", "No"),
        career_interest=row.get("career_interest", ""),
        course=row.get("course"),
        academic_year=row.get("academic_year"),
    )


# --------------------------------------------------------------------------- #
#  Career-requirement match (also reused by skill-gap & target engineering)
# --------------------------------------------------------------------------- #
def career_match(profile: dict, career: str) -> dict:
    """
    How well a profile covers the *requirements* of a given career.

    Returns sub-matches in [0, 1] for tech / language / soft plus a combined
    ``overall`` score. The combined weighting (0.5/0.25/0.25) mirrors how much
    each pillar typically signals fit for a role.
    """
    spec = config.CAREERS[career]
    tech_have = set(profile["technical_list"])
    lang_have = set(profile["language_list"])
    soft_have = set(profile["soft_list"])

    def _coverage(have: set[str], weights: dict[str, float]) -> float:
        total = sum(weights.values())
        if total == 0:
            return 0.0
        got = sum(w for skill, w in weights.items() if skill in have)
        return got / total

    tech_match = _coverage(tech_have, spec["tech"])
    lang_match = _coverage(lang_have, spec["lang"])
    soft_match = _coverage(soft_have, spec["soft"])
    overall = 0.50 * tech_match + 0.25 * lang_match + 0.25 * soft_match
    return {
        "tech": tech_match,
        "lang": lang_match,
        "soft": soft_match,
        "overall": overall,
    }


# --------------------------------------------------------------------------- #
#  The five readiness pillars
# --------------------------------------------------------------------------- #
def _technical_pillar(profile: dict) -> float:
    breadth = min(len(profile["technical_list"]) / TARGET_TECHNICAL, 1.0)
    proficiency = profile["technical_rating"] / 5.0
    return 0.5 * breadth + 0.5 * proficiency


def _programming_pillar(profile: dict) -> float:
    return min(len(profile["language_list"]) / TARGET_LANGUAGES, 1.0)


def _soft_pillar(profile: dict) -> float:
    breadth = min(len(profile["soft_list"]) / TARGET_SOFT, 1.0)
    proficiency = profile["soft_rating"] / 5.0
    return 0.5 * breadth + 0.5 * proficiency


def _projects_pillar(profile: dict) -> float:
    # Hands-on experience is mostly binary, but we grant partial credit for
    # "No" so a single missing project does not zero out the whole pillar.
    return 1.0 if profile["has_projects"] == "Yes" else 0.15


def _alignment_pillar(profile: dict) -> float:
    """Skill coverage against the career the student is *interested* in."""
    interest = profile.get("career_interest", "")
    career = config.INTEREST_TO_CAREER.get(interest)
    if career is None:
        # Unknown interest -> best coverage across all careers.
        return max(career_match(profile, c)["overall"] for c in config.CAREER_LIST)
    return career_match(profile, career)["overall"]


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def compute_readiness(profile: dict) -> dict:
    """
    Compute the weighted 0-100 readiness score and a full breakdown.

    Returns a dict with:
        score      : float 0-100 (rounded to 1 dp)
        band       : str   (Beginner / Intermediate / Advanced / Industry Ready)
        emoji, colour
        pillars    : {name: {raw: 0-1, weighted_points: 0-100 contribution}}
    """
    pillars_raw = {
        "technical": _technical_pillar(profile),
        "programming": _programming_pillar(profile),
        "soft": _soft_pillar(profile),
        "projects": _projects_pillar(profile),
        "alignment": _alignment_pillar(profile),
    }

    score = 0.0
    breakdown: dict[str, dict] = {}
    for pillar, raw in pillars_raw.items():
        weight = config.READINESS_WEIGHTS[pillar]
        points = raw * weight * 100.0          # contribution to the 0-100 total
        score += points
        breakdown[pillar] = {
            "raw": round(raw, 3),
            "weight": weight,
            "max_points": round(weight * 100, 1),
            "points": round(points, 1),
        }

    score = round(max(0.0, min(100.0, score)), 1)
    label, emoji, colour = config.readiness_band(score)
    return {
        "score": score,
        "band": label,
        "emoji": emoji,
        "colour": colour,
        "pillars": breakdown,
    }


def readiness_for_row(row) -> dict:
    """Convenience wrapper: cleaned-DataFrame row -> readiness result."""
    return compute_readiness(profile_from_row(row))


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    demo = make_profile(
        technical_list=["Python", "Machine Learning", "Data Analysis", "SQL"],
        language_list=["Python", "R", "SQL"],
        soft_list=["Problem-Solving", "Communication", "Teamwork"],
        technical_rating=4,
        soft_rating=4,
        has_projects="Yes",
        career_interest="Data Scientist",
    )
    import json
    print(json.dumps(compute_readiness(demo), indent=2))
