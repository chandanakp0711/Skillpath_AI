"""
===============================================================================
 app.py  --  SkillPath AI · Streamlit application entry point
===============================================================================
Modern multi-page dashboard for the "Intelligent Skill Profiling for Career
Readiness & Growth Pathways" project.

Run with:
    streamlit run app.py
===============================================================================
"""

from __future__ import annotations

import streamlit as st

from src import config
from src.predict import model_is_trained
from app_pages import about, analytics, growth, home, prediction, profile
from app_pages import components as ui

# --------------------------------------------------------------------------- #
#  Page configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title=config.APP_SHORT_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()

# --------------------------------------------------------------------------- #
#  Navigation registry
# --------------------------------------------------------------------------- #
PAGES = {
    "home": ("🏠", "Home", home.render),
    "profile": ("👤", "Student Profile", profile.render),
    "prediction": ("🔮", "Prediction", prediction.render),
    "growth": ("🚀", "Growth Pathway", growth.render),
    "analytics": ("📊", "Analytics Dashboard", analytics.render),
    "about": ("ℹ️", "About Project", about.render),
}

if "page" not in st.session_state:
    st.session_state["page"] = "home"


def goto(page_key: str) -> None:
    """Programmatic navigation used by in-page CTA buttons."""
    st.session_state["page"] = page_key
    st.rerun()


# --------------------------------------------------------------------------- #
#  Sidebar
# --------------------------------------------------------------------------- #
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"<h1 style='font-size:1.5rem;margin-bottom:0'>{config.APP_ICON} "
            f"{config.APP_SHORT_TITLE}</h1>"
            "<p style='opacity:.65;margin-top:.2rem;font-size:.85rem'>"
            "Career Readiness & Growth</p><hr style='margin:.6rem 0'>",
            unsafe_allow_html=True,
        )

        for key, (icon, label, _) in PAGES.items():
            active = st.session_state["page"] == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         width="stretch",
                         type="primary" if active else "secondary"):
                goto(key)

        st.markdown("<hr style='margin:.8rem 0'>", unsafe_allow_html=True)

        # ---- Progress tracker ------------------------------------------- #
        st.markdown("**Your progress**")
        has_profile = "profile" in st.session_state
        has_pred = "prediction" in st.session_state
        st.markdown(
            f"{'✅' if has_profile else '⬜'} Profile built<br>"
            f"{'✅' if has_pred else '⬜'} Career predicted<br>"
            f"{'✅' if has_pred else '⬜'} Roadmap ready",
            unsafe_allow_html=True,
        )

        # ---- Model status ----------------------------------------------- #
        st.markdown("<hr style='margin:.8rem 0'>", unsafe_allow_html=True)
        if model_is_trained():
            st.success("🤖 ML model loaded", icon="✅")
        else:
            st.warning("Model not trained. Run `python train.py` "
                       "(a rule-based fallback is used meanwhile).")

        st.caption("💡 Toggle light/dark via the ☰ menu → Settings → Theme.")


# --------------------------------------------------------------------------- #
#  Main render loop
# --------------------------------------------------------------------------- #
def main() -> None:
    render_sidebar()
    page_key = st.session_state["page"]
    _icon, _label, render_fn = PAGES.get(page_key, PAGES["home"])
    render_fn(goto)


if __name__ == "__main__":
    main()
