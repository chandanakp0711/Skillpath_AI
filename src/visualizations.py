"""
===============================================================================
 visualizations.py  --  Interactive Plotly chart factory
===============================================================================
Every chart the app shows is built here so styling stays consistent and the
UI code remains declarative. All figures use transparent backgrounds and no
hard-coded font colour, so they look correct in BOTH Streamlit light and dark
mode (rendered with theme="streamlit").

Chart catalogue (maps to the spec's 10 required dashboard charts + extras):
    1. career_interest_pie            6. career_category_pie
    2. top_technical_skills_bar       7. correlation_heatmap
    3. language_trends_bar            8. tech_vs_soft_scatter
    4. readiness_histogram            9. confidence_gauge
    5. skill_gap_bar                 10. readiness_speedometer
  + course/year bars, soft-skill radar, probability bar, pillar radar ...
===============================================================================
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import config, eda

PALETTE = config.PLOTLY_PALETTE


# --------------------------------------------------------------------------- #
#  Shared styling
# --------------------------------------------------------------------------- #
def _style(fig: go.Figure, height: int = 380, title: str | None = None,
           showlegend: bool = True) -> go.Figure:
    """Apply the consistent, theme-aware look to a figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50 if title else 20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=showlegend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                    xanchor="center", x=0.5),
        title=dict(text=title, x=0.5, xanchor="center",
                   font=dict(size=16)) if title else None,
        hoverlabel=dict(bgcolor=config.THEME["card"], font_size=12),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)", zeroline=False)
    return fig


# --------------------------------------------------------------------------- #
#  1. Career interest distribution — pie
# --------------------------------------------------------------------------- #
def career_interest_pie(df: pd.DataFrame) -> go.Figure:
    data = eda.career_interest_distribution(df)
    fig = go.Figure(go.Pie(
        labels=data.index, values=data.values, hole=0.45,
        marker=dict(colors=PALETTE), textinfo="percent+label",
        textposition="inside", insidetextorientation="radial",
    ))
    return _style(fig, height=400, title="Career Interest Distribution",
                  showlegend=False)


# --------------------------------------------------------------------------- #
#  2. Top technical skills — horizontal bar
# --------------------------------------------------------------------------- #
def top_technical_skills_bar(df: pd.DataFrame) -> go.Figure:
    data = eda.top_technical_skills(df).sort_values()
    fig = go.Figure(go.Bar(
        x=data.values, y=data.index, orientation="h",
        marker=dict(color=data.values, colorscale="Tealgrn"),
        text=data.values, textposition="outside",
    ))
    return _style(fig, height=400, title="Most Popular Technical Skills",
                  showlegend=False)


# --------------------------------------------------------------------------- #
#  3. Programming language trends — bar
# --------------------------------------------------------------------------- #
def language_trends_bar(df: pd.DataFrame) -> go.Figure:
    data = eda.language_popularity(df)
    fig = go.Figure(go.Bar(
        x=data.index, y=data.values,
        marker=dict(color=data.values, colorscale="Purp"),
        text=data.values, textposition="outside",
    ))
    return _style(fig, height=380, title="Programming Language Popularity",
                  showlegend=False)


# --------------------------------------------------------------------------- #
#  4. Readiness score distribution — histogram
# --------------------------------------------------------------------------- #
def readiness_histogram(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=df["readiness_score"], nbinsx=24,
        marker=dict(color=config.THEME["primary"],
                    line=dict(color="rgba(255,255,255,0.3)", width=1)),
    ))
    # Band boundary guides.
    for boundary in (40, 60, 80):
        fig.add_vline(x=boundary, line_dash="dash",
                      line_color="rgba(148,163,184,0.5)")
    fig.update_layout(bargap=0.05)
    return _style(fig, height=380, title="Career-Readiness Score Distribution",
                  showlegend=False)


# --------------------------------------------------------------------------- #
#  5. Skill-gap analysis — bar (attained vs gap per pillar)
# --------------------------------------------------------------------------- #
def skill_gap_bar(df: pd.DataFrame) -> go.Figure:
    summary = eda.skill_gap_summary(df)
    fig = go.Figure()
    fig.add_bar(name="Attained", x=summary["pillar"], y=summary["avg_points"],
                marker_color=config.THEME["success"],
                text=summary["attainment_pct"].map(lambda v: f"{v:.0f}%"),
                textposition="inside")
    fig.add_bar(name="Gap", x=summary["pillar"], y=summary["gap"],
                marker_color="rgba(239,68,68,0.6)")
    fig.update_layout(barmode="stack")
    return _style(fig, height=400, title="Skill-Gap Analysis (avg points vs max)")


# --------------------------------------------------------------------------- #
#  6. Student career category analysis — pie
# --------------------------------------------------------------------------- #
def career_category_pie(df: pd.DataFrame) -> go.Figure:
    data = eda.recommended_career_distribution(df)
    fig = go.Figure(go.Pie(
        labels=data.index, values=data.values, hole=0.35,
        marker=dict(colors=PALETTE), textinfo="percent",
        pull=[0.04] * len(data),
    ))
    return _style(fig, height=420, title="Recommended Career Category Distribution",
                  showlegend=True)


# --------------------------------------------------------------------------- #
#  7. Correlation matrix — heatmap
# --------------------------------------------------------------------------- #
def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    corr = eda.correlation_matrix(df)
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
    )
    fig.update_traces(textfont_size=10)
    return _style(fig, height=460, title="Feature Correlation Matrix",
                  showlegend=False)


# --------------------------------------------------------------------------- #
#  8. Technical vs soft skill — scatter
# --------------------------------------------------------------------------- #
def tech_vs_soft_scatter(df: pd.DataFrame) -> go.Figure:
    data = eda.tech_vs_soft(df)
    fig = px.scatter(
        data, x="technical", y="soft", color="career_interest",
        size="readiness", size_max=18, opacity=0.75,
        color_discrete_sequence=PALETTE,
        labels={"technical": "Technical strength (rating x #skills)",
                "soft": "Soft-skill strength (rating x #skills)",
                "career_interest": "Career Interest"},
        hover_data={"readiness": True},
    )
    return _style(fig, height=440, title="Technical vs Soft Skill Comparison")


# --------------------------------------------------------------------------- #
#  9. Career-prediction confidence — gauge
# --------------------------------------------------------------------------- #
def confidence_gauge(confidence: float, career: str = "") -> go.Figure:
    pct = round(confidence * 100, 1)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": "%", "font": {"size": 34}},
        title={"text": f"Prediction Confidence<br><span style='font-size:0.8em'>{career}</span>",
               "font": {"size": 15}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": config.THEME["primary"]},
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(239,68,68,0.35)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.35)"},
                {"range": [70, 100], "color": "rgba(34,197,94,0.35)"},
            ],
            "threshold": {"line": {"color": config.THEME["accent"], "width": 4},
                          "thickness": 0.75, "value": pct},
        },
    ))
    return _style(fig, height=300, showlegend=False)


# --------------------------------------------------------------------------- #
#  10. Personalised readiness meter — speedometer
# --------------------------------------------------------------------------- #
def readiness_speedometer(score: float, band: str = "", colour: str = "#6366f1") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        number={"suffix": "/100", "font": {"size": 30}},
        delta={"reference": 81, "increasing": {"color": config.THEME["success"]},
               "decreasing": {"color": config.THEME["danger"]},
               "suffix": " vs Industry-Ready"},
        title={"text": f"Readiness Meter<br><span style='font-size:0.85em'>{band}</span>",
               "font": {"size": 15}},
        gauge={
            "axis": {"range": [0, 100], "tickvals": [0, 40, 60, 80, 100]},
            "bar": {"color": colour, "thickness": 0.3},
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(239,68,68,0.30)"},
                {"range": [40, 60], "color": "rgba(245,158,11,0.30)"},
                {"range": [60, 80], "color": "rgba(59,130,246,0.30)"},
                {"range": [80, 100], "color": "rgba(34,197,94,0.30)"},
            ],
            "threshold": {"line": {"color": "white", "width": 4},
                          "thickness": 0.8, "value": score},
        },
    ))
    return _style(fig, height=320, showlegend=False)


# --------------------------------------------------------------------------- #
#  Extra charts
# --------------------------------------------------------------------------- #
def course_distribution_bar(df: pd.DataFrame) -> go.Figure:
    data = eda.course_distribution(df)
    fig = go.Figure(go.Bar(x=data.index, y=data.values,
                           marker_color=PALETTE[: len(data)],
                           text=data.values, textposition="outside"))
    return _style(fig, height=360, title="Course-wise Distribution", showlegend=False)


def year_distribution_bar(df: pd.DataFrame) -> go.Figure:
    data = eda.year_distribution(df)
    fig = go.Figure(go.Bar(x=data.index, y=data.values,
                           marker_color=config.THEME["accent"],
                           text=data.values, textposition="outside"))
    return _style(fig, height=360, title="Academic-Year Distribution", showlegend=False)


def soft_skill_radar(df: pd.DataFrame) -> go.Figure:
    data = eda.soft_skill_distribution(df)
    fig = go.Figure(go.Scatterpolar(
        r=list(data.values) + [data.values[0]],
        theta=list(data.index) + [data.index[0]],
        fill="toself", line_color=config.THEME["primary"],
        fillcolor="rgba(99,102,241,0.35)",
    ))
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                 radialaxis=dict(showticklabels=True, ticks="")))
    return _style(fig, height=380, title="Soft-Skill Distribution", showlegend=False)


def readiness_band_pie(df: pd.DataFrame) -> go.Figure:
    data = eda.readiness_band_distribution(df)
    colours = {b[2]: b[4] for b in config.READINESS_BANDS}
    fig = go.Figure(go.Pie(
        labels=data.index, values=data.values, hole=0.5,
        marker=dict(colors=[colours.get(b, PALETTE[0]) for b in data.index]),
        textinfo="percent+label", textposition="inside",
    ))
    return _style(fig, height=360, title="Readiness Band Distribution",
                  showlegend=False)


# --------------------------------------------------------------------------- #
#  Per-student charts (prediction page)
# --------------------------------------------------------------------------- #
def probability_bar(probabilities: list[dict], top_k: int = 6) -> go.Figure:
    """Horizontal bar of the model's top-k career probabilities."""
    top = probabilities[:top_k][::-1]
    careers = [p["career"] for p in top]
    probs = [round(p["prob"] * 100, 1) for p in top]
    colors = ["#22c55e" if i == len(top) - 1 else config.THEME["primary"]
              for i in range(len(top))]
    fig = go.Figure(go.Bar(
        x=probs, y=careers, orientation="h", marker_color=colors,
        text=[f"{p}%" for p in probs], textposition="outside",
    ))
    fig.update_xaxes(range=[0, max(probs) * 1.2 if probs else 100])
    return _style(fig, height=320, title="Top Career Matches (model probability)",
                  showlegend=False)


def pillar_radar(readiness: dict) -> go.Figure:
    """Radar of a single student's 5 readiness-pillar raw scores (0-100%)."""
    labels = {"technical": "Technical", "programming": "Programming",
              "soft": "Soft Skills", "projects": "Projects",
              "alignment": "Alignment"}
    pillars = readiness["pillars"]
    keys = list(labels)
    r = [round(pillars[k]["raw"] * 100, 1) for k in keys]
    theta = [labels[k] for k in keys]
    fig = go.Figure(go.Scatterpolar(
        r=r + [r[0]], theta=theta + [theta[0]], fill="toself",
        line_color=readiness.get("colour", config.THEME["primary"]),
        fillcolor="rgba(99,102,241,0.3)", name="You",
    ))
    fig.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(range=[0, 100], showticklabels=True, ticks="")))
    return _style(fig, height=360, title="Your Readiness Profile", showlegend=False)


def skill_coverage_bar(gap: dict) -> go.Figure:
    """Student's coverage of a target career's requirements, per category."""
    detail = gap["match_detail"]
    cats = ["Technical", "Languages", "Soft Skills", "Overall"]
    vals = [detail.get("tech", 0), detail.get("lang", 0),
            detail.get("soft", 0), detail.get("overall", 0)]
    fig = go.Figure(go.Bar(
        x=cats, y=vals, marker_color=[PALETTE[0], PALETTE[1], PALETTE[2], PALETTE[5]],
        text=[f"{v:.0f}%" for v in vals], textposition="outside",
    ))
    fig.update_yaxes(range=[0, 110])
    return _style(fig, height=320,
                  title=f"Your Skill Coverage for {gap['career']}", showlegend=False)


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    frame = eda.build_analysis_frame()
    figs = [career_interest_pie(frame), top_technical_skills_bar(frame),
            language_trends_bar(frame), readiness_histogram(frame),
            skill_gap_bar(frame), career_category_pie(frame),
            correlation_heatmap(frame), tech_vs_soft_scatter(frame),
            confidence_gauge(0.78, "Data Scientist"),
            readiness_speedometer(72.5, "Advanced", "#3b82f6")]
    print(f"Built {len(figs)} figures successfully.")
    for f in figs:
        assert isinstance(f, go.Figure)
    print("All figures are valid Plotly Figures.")
