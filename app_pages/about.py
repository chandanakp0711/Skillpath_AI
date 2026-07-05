"""About page — methodology, algorithms, dataset & tech stack."""

from __future__ import annotations

import json
import os

import streamlit as st

from src import config
from . import components as ui


def _load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return None


def render(goto) -> None:
    ui.hero("About This Project",
            "Methodology, machine-learning approach, dataset details and the "
            "technology behind SkillPath AI.", icon="ℹ️")

    meta = _load_json(config.METADATA_PATH)
    metrics = _load_json(config.METRICS_PATH)

    # ---- Methodology ---------------------------------------------------- #
    ui.section("🧪 Methodology", "The end-to-end machine-learning pipeline", "")
    steps = [
        ("1 · Data Loading & Cleaning", "Load the 500-student dataset, normalise messy headers, "
         "standardise academic-year labels and parse multi-valued skill columns."),
        ("2 · Preprocessing", "Missing-value imputation, duplicate removal, IQR outlier detection "
         "and feature scaling."),
        ("3 · Feature Engineering", "Skill-breadth counts, a 0-100 readiness score, ordinal year "
         "encoding, plus one-hot & multi-hot skill encodings — 54 features in total."),
        ("4 · Target Engineering", "An expert decision rubric maps each profile to a best-fit career; "
         "light label noise keeps the task realistic."),
        ("5 · Model Training & Selection", "Five classifiers are trained, cross-validated and compared; "
         "the best is auto-selected and serialised with joblib."),
        ("6 · Inference & Guidance", "The model predicts a career + confidence, then rule-based engines "
         "produce the skill-gap report and growth pathway."),
    ]
    for title, body in steps:
        ui.timeline_step(title, [body])

    # ---- Algorithms ----------------------------------------------------- #
    ui.section("🤖 Algorithms Used", "Five models compared, best auto-selected", "")
    algos = [
        ("📏 Logistic Regression", "Linear, highly interpretable baseline."),
        ("🌳 Decision Tree", "Captures non-linear, rule-like decision boundaries."),
        ("🌲 Random Forest", "Bagged ensemble — robust & accurate."),
        ("⚡ Gradient Boosting", "Sequentially boosted trees for high accuracy."),
        ("🚀 XGBoost", "Optimised gradient boosting (optional dependency)."),
    ]
    cols = st.columns(len(algos))
    for col, (title, body) in zip(cols, algos):
        with col:
            ui.feature_card(title.split()[0], title.split(" ", 1)[1], body)

    if metrics:
        best = metrics["best_model"]
        bm = metrics["models"][best]
        st.success(
            f"🏅 **Best model: {best}** — Accuracy {bm['accuracy']*100:.1f}% · "
            f"F1 {bm['f1']*100:.1f}% · CV-F1 {bm['cv_f1_mean']*100:.1f}% "
            f"(selected automatically by cross-validation).")
        st.caption("Evaluation: Accuracy · Precision · Recall · F1 · Confusion "
                   "Matrix · 5-fold Stratified Cross-Validation.")

    # ---- Readiness formula ---------------------------------------------- #
    ui.section("📐 Readiness Scoring Formula", "A transparent, weighted 0-100 score", "")
    f1, f2 = st.columns([3, 2])
    with f1:
        st.markdown("""
| Pillar | Weight | What it measures |
|---|---|---|
| Technical Skills | **40%** | Breadth × self-rated proficiency |
| Programming | **20%** | Number of languages known |
| Soft Skills | **20%** | Breadth × self-rated proficiency |
| Project Experience | **10%** | Hands-on portfolio work |
| Career Alignment | **10%** | Skill match to the chosen career |
""")
    with f2:
        st.markdown("""
**Readiness bands**
- 🌱 **0–40** Beginner
- 📘 **41–60** Intermediate
- 🚀 **61–80** Advanced
- 🏆 **81–100** Industry Ready
""")

    # ---- Dataset -------------------------------------------------------- #
    ui.section("🗂️ Dataset Information", "Student Skill-Gap Analysis", "")
    d1, d2, d3 = st.columns(3)
    with d1:
        ui.kpi_card(meta["n_samples"] if meta else 500, "Student Records", "#6366f1")
    with d2:
        ui.kpi_card(meta["n_features"] if meta else 54, "Engineered Features", "#06b6d4")
    with d3:
        ui.kpi_card(meta["n_classes"] if meta else 10, "Career Classes", "#22c55e")
    st.markdown("""
**Source fields:** Academic Year · Current Course · Technical Skills ·
Programming Languages · Technical Skill Rating · Soft Skills · Soft Skill Rating ·
Projects · Career Interest · Learning Challenges · Support Required · Learning Method.
""")

    # ---- Tech stack ----------------------------------------------------- #
    ui.section("🛠️ Technology Stack", "", "")
    ui.pills(["Python 3", "Streamlit", "scikit-learn", "XGBoost", "Plotly",
              "Pandas", "NumPy", "Seaborn / Matplotlib", "Joblib"], "neutral")

    st.info("📌 **Disclaimer:** Recommendations are guidance generated from a "
            "model trained on a sample dataset. Use them as a directional aid "
            "alongside mentors and your own research — not as a definitive verdict.")
    ui.footer()
