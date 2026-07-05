"""Analytics Dashboard page — every EDA & model-performance visualisation."""

from __future__ import annotations

import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from src import config, eda
from src import visualizations as viz
from . import components as ui


@st.cache_data(show_spinner="Crunching the dataset…")
def _frame() -> pd.DataFrame:
    return eda.build_analysis_frame()


@st.cache_data(show_spinner=False)
def _metrics() -> dict | None:
    if not os.path.exists(config.METRICS_PATH):
        return None
    with open(config.METRICS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def render(goto) -> None:
    ui.hero("Analytics Dashboard",
            "Interactive exploration of 500 student profiles, skill trends, "
            "readiness patterns and model performance.", icon="📊")

    df = _frame()
    overview = eda.dataset_overview(df)

    # ---- KPI row -------------------------------------------------------- #
    kpis = [
        (overview["n_students"], "Students", "#6366f1"),
        (overview["n_careers"], "Career Paths", "#06b6d4"),
        (f"{overview['avg_readiness']}", "Avg Readiness", "#22c55e"),
        (f"{overview['pct_with_projects']}%", "Have Projects", "#f59e0b"),
        (f"{overview['industry_ready_pct']}%", "Industry Ready", "#ef4444"),
    ]
    for col, (val, label, accent) in zip(st.columns(len(kpis)), kpis):
        with col:
            ui.kpi_card(val, label, accent)

    tabs = st.tabs(["👥 Students", "💡 Skills", "📈 Readiness",
                    "🔗 Correlations", "🤖 Model Performance"])

    # ---- Students ------------------------------------------------------- #
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(viz.course_distribution_bar(df), width="stretch")
        with c2:
            st.plotly_chart(viz.year_distribution_bar(df), width="stretch")
        st.plotly_chart(viz.career_interest_pie(df), width="stretch")

    # ---- Skills --------------------------------------------------------- #
    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(viz.top_technical_skills_bar(df), width="stretch")
        with c2:
            st.plotly_chart(viz.language_trends_bar(df), width="stretch")
        st.plotly_chart(viz.soft_skill_radar(df), width="stretch")

    # ---- Readiness ------------------------------------------------------ #
    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(viz.readiness_histogram(df), width="stretch")
        with c2:
            st.plotly_chart(viz.readiness_band_pie(df), width="stretch")
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(viz.skill_gap_bar(df), width="stretch")
        with c4:
            st.plotly_chart(viz.career_category_pie(df), width="stretch")

    # ---- Correlations --------------------------------------------------- #
    with tabs[3]:
        st.plotly_chart(viz.correlation_heatmap(df), width="stretch")
        st.plotly_chart(viz.tech_vs_soft_scatter(df), width="stretch")
        st.caption("Tip: drag to zoom, double-click to reset, hover for details.")

    # ---- Model performance ---------------------------------------------- #
    with tabs[4]:
        metrics = _metrics()
        if metrics is None:
            st.warning("Model not trained yet. Run `python train.py` to populate "
                       "performance metrics.")
        else:
            ui.section("🏅 Model Comparison",
                       f"Best model: {metrics['best_model']} "
                       f"(auto-selected by cross-validation F1)", "")
            rows = []
            for name, m in metrics["models"].items():
                rows.append({
                    "Model": name,
                    "Accuracy": round(m["accuracy"], 3),
                    "Precision": round(m["precision"], 3),
                    "Recall": round(m["recall"], 3),
                    "F1": round(m["f1"], 3),
                    "CV F1": round(m["cv_f1_mean"], 3),
                })
            table = pd.DataFrame(rows).sort_values("CV F1", ascending=False)
            st.dataframe(
                table.style.highlight_max(
                    subset=["Accuracy", "Precision", "Recall", "F1", "CV F1"],
                    color="rgba(34,197,94,0.3)"),
                width="stretch", hide_index=True)

            c1, c2 = st.columns([3, 2])
            with c1:
                imp = metrics["feature_importance"]
                top = dict(list(imp.items())[:15][::-1])
                fig = px.bar(x=list(top.values()), y=list(top.keys()),
                             orientation="h",
                             color=list(top.values()),
                             color_continuous_scale="Tealgrn",
                             labels={"x": "Importance", "y": ""})
                fig.update_layout(height=460, paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)",
                                  coloraxis_showscale=False,
                                  margin=dict(l=10, r=10, t=40, b=10),
                                  title="Top 15 Feature Importances")
                st.plotly_chart(fig, width="stretch")
            with c2:
                best = metrics["models"][metrics["best_model"]]
                cm = best["confusion_matrix"]
                classes = metrics["classes"]
                fig = px.imshow(cm, x=classes, y=classes, text_auto=True,
                                color_continuous_scale="Purples",
                                labels={"x": "Predicted", "y": "Actual"})
                fig.update_layout(height=460, paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)",
                                  margin=dict(l=10, r=10, t=40, b=10),
                                  title=f"Confusion Matrix — {metrics['best_model']}")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, width="stretch")

    ui.footer()
