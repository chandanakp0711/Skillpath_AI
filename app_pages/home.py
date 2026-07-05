"""Home page — project overview, objectives, features & career domains."""

from __future__ import annotations

import streamlit as st

from src import config
from . import components as ui


def render(goto) -> None:
    ui.hero(
        "Intelligent Skill Profiling for Career Readiness & Growth",
        "Analyse your skills, predict your best-fit career, uncover skill gaps "
        "and get a personalised, week-by-week growth roadmap — powered by "
        "Machine Learning.",
        icon="🎯",
    )

    # ---- Call to action ------------------------------------------------- #
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("🚀 Build my profile", width="stretch", type="primary"):
            goto("profile")
    with c2:
        if st.button("📊 Explore analytics", width="stretch"):
            goto("analytics")
    with c3:
        if st.button("ℹ️ How it works", width="stretch"):
            goto("about")

    # ---- Objectives ----------------------------------------------------- #
    ui.section("Project Objectives", "What this system sets out to achieve", "🎯")
    objectives = [
        ("🧭", "Career Clarity", "Recommend the most suitable career path from a student's skills and interests."),
        ("📐", "Readiness Scoring", "Quantify industry readiness with a transparent 0-100 score."),
        ("🔍", "Skill-Gap Analysis", "Pinpoint exactly which skills, projects & certifications are missing."),
        ("🛤️", "Growth Pathways", "Generate an actionable 30 / 90-day learning roadmap."),
    ]
    cols = st.columns(4)
    for col, (icon, title, body) in zip(cols, objectives):
        with col:
            ui.feature_card(icon, title, body)

    # ---- Key features --------------------------------------------------- #
    ui.section("Key Features", "Everything packed into one intelligent dashboard", "✨")
    features = [
        ("🤖", "ML Career Prediction", "Random-Forest model selected from 5 algorithms predicts your best-fit role with a confidence score."),
        ("📊", "10+ Interactive Charts", "Plotly dashboards for skills, readiness, correlations and live gauges."),
        ("📈", "Readiness Meter", "A weighted speedometer across technical, programming, soft, project & alignment pillars."),
        ("🎓", "Certifications & Resources", "Curated Coursera / Udemy / NPTEL / freeCodeCamp paths for every gap."),
        ("📝", "Interview Prep", "Role-specific topics, mock-interview plan and resume tips."),
        ("🗓️", "Action Plans", "Concrete weekly, 30-day and 90-day plans tailored to your level."),
    ]
    for row in (features[:3], features[3:]):
        cols = st.columns(3)
        for col, (icon, title, body) in zip(cols, row):
            with col:
                ui.feature_card(icon, title, body)

    # ---- Career domains ------------------------------------------------- #
    ui.section("Career Domains Covered", "10 in-demand technology careers", "💼")
    careers = list(config.CAREERS.items())
    for start in range(0, len(careers), 5):
        cols = st.columns(5)
        for col, (name, spec) in zip(cols, careers[start:start + 5]):
            with col:
                ui.feature_card(spec["icon"], name, spec["description"])

    ui.footer()
