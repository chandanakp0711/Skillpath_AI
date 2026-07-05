"""
===============================================================================
 components.py  --  Reusable Streamlit UI building blocks + global CSS
===============================================================================
Centralises the look-and-feel so every page stays consistent and declarative.
All styling uses translucent surfaces and inherited text colour, so the UI
renders correctly in BOTH Streamlit light and dark mode.
===============================================================================
"""

from __future__ import annotations

import streamlit as st

# --------------------------------------------------------------------------- #
#  Global stylesheet
# --------------------------------------------------------------------------- #
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }

/* Tighten the default top padding */
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }

/* ---- Hero banner ---- */
.sp-hero {
    background: linear-gradient(120deg, #4338ca 0%, #6366f1 45%, #06b6d4 100%);
    border-radius: 20px; padding: 2.4rem 2rem; color: #fff;
    box-shadow: 0 18px 40px -18px rgba(79,70,229,0.7);
    margin-bottom: 1.4rem;
}
.sp-hero h1 { color:#fff; font-size: 2.05rem; font-weight: 800; margin: 0 0 .4rem 0; line-height:1.15; }
.sp-hero p  { color: rgba(255,255,255,.92); font-size: 1.05rem; margin: 0; max-width: 60ch; }
.sp-hero .sp-icon { font-size: 2.6rem; }

/* ---- Cards ---- */
.sp-card {
    background: rgba(127,127,127,0.07);
    border: 1px solid rgba(127,127,127,0.18);
    border-radius: 16px; padding: 1.25rem 1.35rem; height: 100%;
    transition: transform .15s ease, box-shadow .15s ease;
}
.sp-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px -16px rgba(99,102,241,.6); }
.sp-card h3 { margin: .1rem 0 .4rem 0; font-size: 1.05rem; font-weight: 700; }
.sp-card p  { margin: 0; opacity: .85; font-size: .92rem; line-height: 1.5; }
.sp-card .sp-card-icon { font-size: 1.7rem; }

/* ---- Metric / KPI cards ---- */
.sp-kpi {
    background: rgba(127,127,127,0.07);
    border: 1px solid rgba(127,127,127,0.18);
    border-left: 4px solid var(--accent, #6366f1);
    border-radius: 14px; padding: 1rem 1.2rem;
}
.sp-kpi .sp-kpi-val { font-size: 1.85rem; font-weight: 800; line-height: 1; }
.sp-kpi .sp-kpi-label { font-size: .82rem; opacity: .7; margin-top: .35rem; text-transform: uppercase; letter-spacing: .04em; }

/* ---- Section headers ---- */
.sp-section { margin: 1.6rem 0 .4rem 0; }
.sp-section h2 { font-size: 1.45rem; font-weight: 750; margin: 0; display:flex; align-items:center; gap:.5rem; }
.sp-section .sp-rule { height: 3px; width: 64px; border-radius: 3px;
    background: linear-gradient(90deg,#6366f1,#06b6d4); margin-top: .35rem; }
.sp-section p { opacity:.7; margin:.4rem 0 0 0; font-size:.92rem; }

/* ---- Pills / badges ---- */
.sp-pill { display:inline-block; padding: .28rem .7rem; border-radius: 999px;
    font-size: .82rem; font-weight: 600; margin: .18rem .22rem .18rem 0; }
.sp-pill.have    { background: rgba(34,197,94,.16);  color:#16a34a; border:1px solid rgba(34,197,94,.4); }
.sp-pill.missing { background: rgba(239,68,68,.14);  color:#dc2626; border:1px solid rgba(239,68,68,.4); }
.sp-pill.neutral { background: rgba(99,102,241,.14); color:#6366f1; border:1px solid rgba(99,102,241,.4); }
.sp-pill.warn    { background: rgba(245,158,11,.16); color:#d97706; border:1px solid rgba(245,158,11,.4); }

/* ---- Progress bar ---- */
.sp-progress-track { background: rgba(127,127,127,.18); border-radius: 999px; height: 16px; width: 100%; overflow:hidden; }
.sp-progress-fill  { height: 100%; border-radius: 999px; text-align:right; color:#fff;
    font-size:.7rem; font-weight:700; padding-right:8px; line-height:16px; }

/* ---- Band chip ---- */
.sp-band { display:inline-block; padding:.4rem 1rem; border-radius:999px; font-weight:700; font-size:.95rem; }

/* ---- Roadmap timeline ---- */
.sp-step { border-left: 3px solid #6366f1; padding: .2rem 0 1rem 1.1rem; margin-left:.4rem; position:relative; }
.sp-step::before { content:''; position:absolute; left:-9px; top:.25rem; width:15px; height:15px;
    border-radius:50%; background:#6366f1; box-shadow:0 0 0 4px rgba(99,102,241,.2); }
.sp-step h4 { margin:0 0 .3rem 0; font-size:1rem; font-weight:700; }
.sp-step ul { margin:.2rem 0 0 0; padding-left:1.1rem; }
.sp-step li { font-size:.9rem; opacity:.88; margin:.15rem 0; }

/* ---- Sidebar nav buttons ---- */
section[data-testid="stSidebar"] .stButton button {
    border-radius: 10px; font-weight: 600; text-align:left; justify-content:flex-start;
}

/* Footer note */
.sp-foot { opacity:.55; font-size:.8rem; text-align:center; margin-top:2rem; }
</style>
"""


def inject_css() -> None:
    """Inject the global stylesheet (call once per page render)."""
    st.markdown(_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Building blocks
# --------------------------------------------------------------------------- #
def hero(title: str, subtitle: str, icon: str = "🎯") -> None:
    st.markdown(
        f"""<div class="sp-hero">
            <div class="sp-icon">{icon}</div>
            <h1>{title}</h1><p>{subtitle}</p></div>""",
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str = "", icon: str = "") -> None:
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""<div class="sp-section"><h2>{icon} {title}</h2>
            <div class="sp-rule"></div>{sub}</div>""",
        unsafe_allow_html=True,
    )


def feature_card(icon: str, title: str, body: str) -> None:
    st.markdown(
        f"""<div class="sp-card"><div class="sp-card-icon">{icon}</div>
            <h3>{title}</h3><p>{body}</p></div>""",
        unsafe_allow_html=True,
    )


def kpi_card(value, label: str, accent: str = "#6366f1") -> None:
    st.markdown(
        f"""<div class="sp-kpi" style="--accent:{accent}">
            <div class="sp-kpi-val">{value}</div>
            <div class="sp-kpi-label">{label}</div></div>""",
        unsafe_allow_html=True,
    )


def pills(items: list[str], kind: str = "neutral") -> None:
    if not items:
        st.markdown('<span class="sp-pill neutral">— none —</span>',
                    unsafe_allow_html=True)
        return
    html = "".join(f'<span class="sp-pill {kind}">{i}</span>' for i in items)
    st.markdown(html, unsafe_allow_html=True)


def band_chip(band: str, colour: str, emoji: str = "") -> None:
    st.markdown(
        f'<span class="sp-band" style="background:{colour}22;color:{colour};'
        f'border:1px solid {colour}66">{emoji} {band}</span>',
        unsafe_allow_html=True,
    )


def progress(pct: float, colour: str = "#6366f1") -> None:
    pct = max(0, min(100, pct))
    st.markdown(
        f"""<div class="sp-progress-track">
          <div class="sp-progress-fill" style="width:{pct}%;
          background:linear-gradient(90deg,{colour},{colour}cc)">{pct:.0f}%</div>
        </div>""",
        unsafe_allow_html=True,
    )


def timeline_step(title: str, items: list[str]) -> None:
    lis = "".join(f"<li>{i}</li>" for i in items)
    st.markdown(
        f'<div class="sp-step"><h4>{title}</h4><ul>{lis}</ul></div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        '<div class="sp-foot">SkillPath AI · Built with Streamlit, scikit-learn '
        '& Plotly · For educational & career-guidance use.</div>',
        unsafe_allow_html=True,
    )
