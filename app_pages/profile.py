"""Student Profile page — capture academic details, skills & interests."""

from __future__ import annotations

import streamlit as st

from src import config
from src.predict import predict_career
from src.readiness import make_profile
from . import components as ui

# Default values pre-loaded into the form (also used by "Load sample").
_DEFAULTS = {
    "f_year": "Final Year",
    "f_course": "B.Sc Data Science",
    "f_tech": ["Python", "Machine Learning", "Data Analysis", "SQL"],
    "f_tech_rating": 4,
    "f_langs": ["Python", "R"],
    "f_soft": ["Problem-Solving", "Communication", "Teamwork"],
    "f_soft_rating": 4,
    "f_projects": "Yes",
    "f_interest": "Data Scientist",
    "f_challenge": "Lack of experience",
    "f_support": "Mentorship programs",
    "f_method": "Online",
}


def _ensure_defaults() -> None:
    for key, val in _DEFAULTS.items():
        st.session_state.setdefault(key, val)


def render(goto) -> None:
    ui.hero(
        "Build Your Student Profile",
        "Tell us about your academic background, skills and interests. "
        "Our ML engine analyses everything in seconds.",
        icon="👤",
    )
    _ensure_defaults()

    # ---- Load a sample profile (must run BEFORE the widgets) ------------ #
    cta_l, cta_r = st.columns([3, 1])
    with cta_r:
        if st.button("🎲 Load sample", width="stretch"):
            for key, val in _DEFAULTS.items():
                st.session_state[key] = val
            st.toast("Sample profile loaded!")

    # ---- The form ------------------------------------------------------- #
    with st.form("profile_form"):
        ui.section("🎓 Academic Details")
        a, b = st.columns(2)
        with a:
            st.selectbox("Academic Year", config.ACADEMIC_YEARS, key="f_year")
        with b:
            st.selectbox("Current Course", config.COURSES, key="f_course")

        ui.section("💻 Technical Skills")
        st.multiselect("Technical skills you know", config.TECHNICAL_SKILLS,
                       key="f_tech")
        st.slider("Self-rated technical proficiency", 1, 5, key="f_tech_rating",
                  help="1 = novice · 5 = expert")
        st.multiselect("Programming languages", config.PROGRAMMING_LANGUAGES,
                       key="f_langs")

        ui.section("🤝 Soft Skills")
        st.multiselect("Soft skills", config.SOFT_SKILLS, key="f_soft")
        st.slider("Self-rated soft-skill proficiency", 1, 5, key="f_soft_rating")

        ui.section("🎯 Interests & Experience")
        c, d = st.columns(2)
        with c:
            st.selectbox("Primary career interest", config.CAREER_INTERESTS,
                         key="f_interest")
            st.radio("Do you have hands-on project experience?", ["Yes", "No"],
                     key="f_projects", horizontal=True)
        with d:
            st.selectbox("Biggest learning challenge", config.LEARNING_CHALLENGES,
                         key="f_challenge")
            st.selectbox("Support you need most", config.SUPPORT_OPTIONS,
                         key="f_support")
        st.selectbox("Preferred learning method", config.LEARNING_METHODS,
                     key="f_method")

        submitted = st.form_submit_button(
            "🔮 Analyse My Career Readiness", width="stretch",
            type="primary")

    # ---- Handle submission ---------------------------------------------- #
    if submitted:
        if not st.session_state["f_tech"]:
            st.error("Please select at least one technical skill.")
            return

        profile = make_profile(
            technical_list=st.session_state["f_tech"],
            language_list=st.session_state["f_langs"],
            soft_list=st.session_state["f_soft"],
            technical_rating=st.session_state["f_tech_rating"],
            soft_rating=st.session_state["f_soft_rating"],
            has_projects=st.session_state["f_projects"],
            career_interest=st.session_state["f_interest"],
            course=st.session_state["f_course"],
            academic_year=st.session_state["f_year"],
        )
        # Extra categorical fields used by the model.
        profile["learning_challenge"] = st.session_state["f_challenge"]
        profile["support_required"] = st.session_state["f_support"]
        profile["learning_method"] = st.session_state["f_method"]

        with st.spinner("Analysing your profile with the ML model…"):
            st.session_state["profile"] = profile
            st.session_state["prediction"] = predict_career(profile)

        st.success("✅ Analysis complete! Head to the Prediction page for your results.")
        if st.button("➡️ View my prediction", type="primary"):
            goto("prediction")

    ui.footer()
