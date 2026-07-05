"""
End-to-end smoke tests for SkillPath AI.

Runs the Streamlit app through every page with the AppTest harness and exercises
the ML pipeline, asserting no exceptions are raised. Run with:

    python -m tests.test_app        # plain runner
    pytest tests/test_app.py        # if pytest is installed
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit.testing.v1 import AppTest  # noqa: E402

from src.predict import predict_career  # noqa: E402
from src.readiness import make_profile  # noqa: E402

PAGES = ["home", "profile", "prediction", "growth", "analytics", "about"]


def _sample_profile() -> dict:
    p = make_profile(
        technical_list=["Python", "Machine Learning", "Cloud Computing"],
        language_list=["Python", "C++"],
        soft_list=["Problem-Solving", "Teamwork", "Communication"],
        technical_rating=5, soft_rating=4, has_projects="Yes",
        career_interest="AI Engineer", course="M.Tech AI",
        academic_year="Final Year",
    )
    p.update(learning_challenge="Lack of experience",
             support_required="Mentorship programs", learning_method="Online")
    return p


def test_all_pages_render_without_profile():
    """Every page must render even before a profile is built."""
    at = AppTest.from_file("app.py", default_timeout=60).run()
    assert not at.exception, at.exception
    for page in PAGES:
        at.session_state["page"] = page
        at.run()
        assert not at.exception, f"{page} raised: {at.exception}"
    print("[OK] all pages render without a profile")


def test_full_flow_with_prediction():
    """Build a profile + prediction, then render result-dependent pages."""
    profile = _sample_profile()
    prediction = predict_career(profile)
    assert prediction["career"] in __import__("src.config", fromlist=["CAREER_LIST"]).CAREER_LIST

    at = AppTest.from_file("app.py", default_timeout=60)
    at.session_state["profile"] = profile
    at.session_state["prediction"] = prediction
    for page in ["prediction", "growth"]:
        at.session_state["page"] = page
        at.run()
        assert not at.exception, f"{page} raised: {at.exception}"
    print(f"[OK] full flow rendered (predicted: {prediction['career']}, "
          f"{prediction['confidence']*100:.0f}% confidence, "
          f"readiness {prediction['readiness']['score']})")


if __name__ == "__main__":
    test_all_pages_render_without_profile()
    test_full_flow_with_prediction()
    print("\nALL SMOKE TESTS PASSED [OK]")
