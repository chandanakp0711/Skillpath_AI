"""Prediction page — career prediction, readiness, confidence & skill gaps."""

from __future__ import annotations

import streamlit as st

from src import config, visualizations as viz
from src.skill_gap import analyze_skill_gap
from . import components as ui


def _no_profile(goto) -> None:
    st.info("👋 Build your profile first to see your personalised prediction.")
    if st.button("👤 Go to Student Profile", type="primary"):
        goto("profile")


def render(goto) -> None:
    ui.hero("Your Career Prediction & Readiness",
            "Best-fit career, model confidence, readiness score and a full "
            "skill-gap breakdown.", icon="🔮")

    if "prediction" not in st.session_state or "profile" not in st.session_state:
        _no_profile(goto)
        ui.footer()
        return

    pred = st.session_state["prediction"]
    profile = st.session_state["profile"]
    career = pred["career"]
    spec = config.CAREERS[career]
    readiness = pred["readiness"]

    # Compute & cache the skill-gap report for this prediction.
    gap = analyze_skill_gap(profile, career)
    st.session_state["gap"] = gap

    # ---- Headline result ------------------------------------------------ #
    ui.section("🏆 Recommended Career", icon="")
    head_l, head_r = st.columns([2, 1])
    with head_l:
        st.markdown(
            f"""<div class="sp-card" style="border-left:5px solid {config.THEME['primary']}">
            <div class="sp-card-icon">{spec['icon']}</div>
            <h3 style="font-size:1.6rem">{career}</h3>
            <p>{spec['description']}</p>
            <p style="margin-top:.6rem"><b>Model confidence:</b>
            {pred['confidence']*100:.1f}% &nbsp;·&nbsp;
            <b>Readiness:</b> {readiness['emoji']} {readiness['band']}
            ({readiness['score']}/100)</p></div>""",
            unsafe_allow_html=True,
        )
        st.caption(f"Prediction source: {pred['source']}")
    with head_r:
        ui.band_chip(readiness["band"], readiness["colour"], readiness["emoji"])
        st.write("")
        for alt in pred["alternatives"]:
            st.markdown(
                f'<span class="sp-pill neutral">{alt["career"]} · '
                f'{alt["fit"]*100:.0f}% fit</span>', unsafe_allow_html=True)

    # ---- Gauges --------------------------------------------------------- #
    ui.section("📟 Readiness & Confidence Meters", icon="")
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(
            viz.readiness_speedometer(readiness["score"], readiness["band"],
                                      readiness["colour"]),
            width="stretch")
    with g2:
        st.plotly_chart(viz.confidence_gauge(pred["confidence"], career),
                        width="stretch")

    # ---- Readiness pillar progress bars --------------------------------- #
    ui.section("📊 Readiness Breakdown", "How each weighted pillar contributes "
               "to your score", "")
    pillar_labels = {"technical": "Technical Skills (40%)",
                     "programming": "Programming (20%)",
                     "soft": "Soft Skills (20%)",
                     "projects": "Project Experience (10%)",
                     "alignment": "Career Alignment (10%)"}
    pc1, pc2 = st.columns([1, 1])
    with pc1:
        for pillar, label in pillar_labels.items():
            info = readiness["pillars"][pillar]
            st.markdown(f"**{label}** — {info['points']:.1f}/{info['max_points']:.0f} pts")
            ui.progress(100 * info["points"] / info["max_points"],
                        readiness["colour"])
            st.write("")
    with pc2:
        st.plotly_chart(viz.pillar_radar(readiness), width="stretch")

    # ---- Probability distribution --------------------------------------- #
    ui.section("🎲 All Career Matches", "Model probability across every career", "")
    pcol1, pcol2 = st.columns([3, 2])
    with pcol1:
        st.plotly_chart(viz.probability_bar(pred["probabilities"]),
                        width="stretch")
    with pcol2:
        st.plotly_chart(viz.skill_coverage_bar(gap), width="stretch")

    # ---- Skill-gap analysis --------------------------------------------- #
    ui.section("🔍 Skill-Gap Analysis", f"What stands between you and "
               f"{career}", "")
    for line in gap["explanations"]:
        st.markdown(f"- {line}")

    st.write("")
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        st.markdown("**✅ Skills you have**")
        ui.pills(gap["have_technical"] + gap["have_languages"], "have")
    with gc2:
        st.markdown("**❌ Missing technical / languages**")
        ui.pills(gap["missing_technical"] + gap["missing_languages"], "missing")
    with gc3:
        st.markdown("**🤝 Soft-skill gaps**")
        ui.pills(gap["missing_soft"] or ["All covered 🎉"],
                 "missing" if gap["missing_soft"] else "have")

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("**💪 Strength areas**")
        ui.pills(gap["strength_areas"] or ["Keep building!"], "have")
    with sc2:
        st.markdown("**⚠️ Weak areas to prioritise**")
        ui.pills(gap["weak_areas"] or ["No major weaknesses"], "warn")

    # ---- CTA ------------------------------------------------------------ #
    st.write("")
    if st.button("🚀 Get my personalised growth pathway", type="primary",
                 width="stretch"):
        goto("growth")

    ui.footer()
