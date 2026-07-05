"""Growth Pathway page — personalised roadmap, certs, resources & plans."""

from __future__ import annotations

import streamlit as st

from src import config
from src.growth_pathway import generate_pathway
from . import components as ui

_LEVEL_KIND = {"Foundation": "have", "Intermediate": "neutral", "Advanced": "warn"}
_PRIORITY_KIND = {"High": "missing", "Medium": "warn", "Low": "neutral"}


def render(goto) -> None:
    ui.hero("Your Personalised Growth Pathway",
            "A step-by-step roadmap — skills, projects, certifications, "
            "resources and action plans tailored to you.", icon="🚀")

    if "prediction" not in st.session_state or "profile" not in st.session_state:
        st.info("👋 Build your profile and run a prediction first.")
        if st.button("👤 Go to Student Profile", type="primary"):
            goto("profile")
        ui.footer()
        return

    profile = st.session_state["profile"]
    career = st.session_state["prediction"]["career"]
    gap = st.session_state.get("gap")
    pathway = generate_pathway(profile, career, gap)
    band = pathway["readiness_band"]

    st.markdown(
        f"#### 🎯 Target role: **{config.CAREERS[career]['icon']} {career}** "
        f"&nbsp;·&nbsp; Current level: **{band}** "
        f"({pathway['readiness_score']}/100)")

    tabs = st.tabs(["🎓 Skills & Certifications", "📚 Learning Resources",
                    "🗓️ Roadmap & Plans", "📝 Interview Prep"])

    # ---- Tab 1: skills, projects, certs --------------------------------- #
    with tabs[0]:
        ui.section("📌 Recommended Skills", "Priority-ordered for your goal", "")
        for item in pathway["recommended_skills"]:
            kind = _PRIORITY_KIND.get(item["priority"], "neutral")
            st.markdown(
                f'<span class="sp-pill {kind}">{item["priority"]}</span> '
                f'**{item["skill"]}** — {item["reason"]}',
                unsafe_allow_html=True)

        ui.section("🏗️ Recommended Projects", "Build these for your portfolio", "")
        for i, proj in enumerate(pathway["recommended_projects"], 1):
            st.markdown(f"**{i}.** {proj}")

        ui.section("📜 Recommended Certifications", "Levelled foundation → advanced", "")
        cc = st.columns(2)
        for idx, cert in enumerate(pathway["recommended_certifications"]):
            with cc[idx % 2]:
                kind = _LEVEL_KIND.get(cert["level"], "neutral")
                st.markdown(
                    f'<div class="sp-card" style="margin-bottom:.6rem">'
                    f'<span class="sp-pill {kind}">{cert["level"]}</span><br>'
                    f'<b>{cert["name"]}</b></div>', unsafe_allow_html=True)

    # ---- Tab 2: resources ----------------------------------------------- #
    with tabs[1]:
        ui.section("📚 Curated Learning Resources",
                   "Hand-picked courses for each recommended skill", "")
        for block in pathway["learning_resources"]:
            with st.expander(f"📘 {block['skill']}", expanded=False):
                for res in block["resources"]:
                    st.markdown(
                        f"- **[{res['title']}]({res['url']})** "
                        f"· _{res['platform']}_")
        ui.section("🌐 Top Platforms", "", "")
        plat_cols = st.columns(len(config.LEARNING_PLATFORMS))
        for col, (name, url) in zip(plat_cols, config.LEARNING_PLATFORMS.items()):
            with col:
                st.markdown(f"[**{name}**]({url})")

    # ---- Tab 3: roadmaps ------------------------------------------------ #
    with tabs[2]:
        ui.section("🗓️ Weekly Learning Roadmap", "~8 weeks to job-ready", "")
        for step in pathway["weekly_roadmap"]:
            ui.timeline_step(f"Week {step['week']} · {step['focus']}", step["tasks"])

        r1, r2 = st.columns(2)
        with r1:
            ui.section("⚡ 30-Day Action Plan", "", "")
            for p in pathway["plan_30_day"]:
                ui.timeline_step(f"{p['phase']} · {p['title']}", p["goals"])
        with r2:
            ui.section("📈 90-Day Career Growth Plan", "", "")
            for p in pathway["plan_90_day"]:
                ui.timeline_step(f"{p['month']} · {p['title']}", p["milestones"])

    # ---- Tab 4: interview prep ------------------------------------------ #
    with tabs[3]:
        prep = pathway["interview_prep"]
        ui.section("🎯 Core Interview Topics", f"For {career} roles", "")
        ui.pills(prep["topics"], "neutral")
        ui.section("✅ Preparation Checklist", prep["timeline"], "")
        for tip in prep["tips"]:
            st.markdown(f"- {tip}")

    ui.footer()
