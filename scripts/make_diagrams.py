"""
===============================================================================
 make_diagrams.py  --  Generate architecture & system-workflow diagrams (PNG)
===============================================================================
Pure-matplotlib renderer (no Graphviz dependency) that writes:
    assets/architecture_diagram.png
    assets/workflow_diagram.png

Run with:  python scripts/make_diagrams.py
===============================================================================
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config  # noqa: E402

C = config.THEME
ASSETS = config.ASSETS_DIR


# --------------------------------------------------------------------------- #
#  Drawing helpers
# --------------------------------------------------------------------------- #
def _box(ax, x, y, w, h, text, face, edge="#334155", text_color="#0f172a",
         fontsize=10, weight="bold"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
        linewidth=1.4, edgecolor=edge, facecolor=face, alpha=0.95, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=text_color, weight=weight, zorder=3,
            wrap=True)


def _arrow(ax, x1, y1, x2, y2, color="#475569", style="-|>"):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=18,
        linewidth=1.8, color=color, zorder=1,
        connectionstyle="arc3,rad=0.0"))


def _band(ax, x, y, w, h, color, label):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
        linewidth=0, facecolor=color, alpha=0.12, zorder=0))
    ax.text(x + 0.15, y + h - 0.28, label, ha="left", va="top",
            fontsize=11, color=color, weight="bold", style="italic")


# --------------------------------------------------------------------------- #
#  1. Architecture diagram (layered)
# --------------------------------------------------------------------------- #
def architecture_diagram(path: str) -> None:
    fig, ax = plt.subplots(figsize=(12.5, 9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.axis("off")
    ax.text(6, 10.5, "SkillPath AI — System Architecture", ha="center",
            fontsize=17, weight="bold", color=C["primary_dark"])

    layers = [
        (8.6, C["primary"], "Presentation Layer", [
            "Home", "Profile", "Prediction",
            "Growth", "Analytics", "About"]),
        (6.8, C["accent"], "Intelligence Layer", [
            "Readiness\nScoring", "Skill-Gap\nDetector", "Growth-Pathway\nGenerator",
            "Career-Fit\nRanking"]),
        (5.0, C["success"], "ML Layer", [
            "Logistic Reg.", "Decision Tree", "Random Forest",
            "Grad. Boost", "XGBoost"]),
        (3.2, C["warning"], "Processing Layer", [
            "Cleaning &\nImputation", "Feature\nEngineering", "Encoding &\nScaling",
            "Target\nEngineering"]),
        (1.4, "#a855f7", "Data Layer", [
            "skillgap_dataset.xlsx\n(500 students × 14 cols)", "Data Loader",
            "Saved Artefacts\n(.pkl / .json)"]),
    ]

    for y, color, label, items in layers:
        _band(ax, 0.3, y - 0.35, 11.4, 1.5, color, label)
        n = len(items)
        total_w = 8.8
        gap = 0.25
        bw = (total_w - gap * (n - 1)) / n
        x0 = 2.9
        for i, item in enumerate(items):
            x = x0 + i * (bw + gap)
            _box(ax, x, y, bw, 0.85, item, face="#ffffff",
                 edge=color, text_color="#1e293b", fontsize=8.5)

    # vertical flow arrows between layer centres
    for y_top, y_bot in [(8.55, 8.3), (6.75, 6.5), (4.95, 4.7), (3.15, 2.9)]:
        _arrow(ax, 6.7, y_top, 6.7, y_bot - 0.05, color="#64748b")

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[OK] wrote {path}")


# --------------------------------------------------------------------------- #
#  2. System workflow diagram (left-to-right pipeline)
# --------------------------------------------------------------------------- #
def workflow_diagram(path: str) -> None:
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.text(6.5, 7.5, "SkillPath AI — System Workflow", ha="center",
            fontsize=17, weight="bold", color=C["primary_dark"])

    # Offline training track (top row)
    ax.text(0.3, 6.7, "OFFLINE — Model Training (train.py)", fontsize=11,
            weight="bold", color=C["success"], style="italic")
    train_steps = [
        ("Load &\nClean Data", C["accent"]),
        ("Engineer\nTarget Label", C["accent"]),
        ("Preprocess &\nFeaturise", C["warning"]),
        ("Train 5\nModels + CV", C["success"]),
        ("Select Best\n& Save .pkl", C["primary"]),
    ]
    y = 5.5
    bw, bh, gap = 2.1, 0.95, 0.35
    x = 0.4
    centres = []
    for text, color in train_steps:
        _box(ax, x, y, bw, bh, text, face="#ffffff", edge=color,
             text_color="#1e293b", fontsize=9)
        centres.append(x + bw)
        x += bw + gap
    for i in range(len(train_steps) - 1):
        _arrow(ax, centres[i], y + bh / 2, centres[i] + gap, y + bh / 2,
               color=C["success"])

    # Inference track (bottom row)
    ax.text(0.3, 3.5, "ONLINE — Student Inference (app.py)", fontsize=11,
            weight="bold", color=C["primary"], style="italic")
    infer_steps = [
        ("Student\nProfile Form", C["primary"]),
        ("Featurise\n(same path)", C["warning"]),
        ("Load Model\n+ Predict", C["primary"]),
        ("Career +\nConfidence", C["success"]),
        ("Readiness ·\nGap · Pathway", C["accent"]),
        ("Dashboard\nVisuals", C["primary_dark"]),
    ]
    y2 = 2.2
    bw2, gap2 = 1.85, 0.25
    x = 0.4
    centres2 = []
    for text, color in infer_steps:
        _box(ax, x, y2, bw2, bh, text, face="#ffffff", edge=color,
             text_color="#1e293b", fontsize=8.5)
        centres2.append((x, x + bw2))
        x += bw2 + gap2
    for i in range(len(infer_steps) - 1):
        _arrow(ax, centres2[i][1], y2 + bh / 2, centres2[i + 1][0],
               y2 + bh / 2, color=C["primary"])

    # link saved model -> inference predict step
    _arrow(ax, 9.0, y, centres2[2][0] + 0.9, y2 + bh, color="#94a3b8",
           style="-|>")
    ax.text(9.7, 4.3, "saved\nartefacts", fontsize=8, color="#64748b",
            ha="center", style="italic")

    # legend
    handles = [
        mpatches.Patch(color=C["success"], label="Training pipeline"),
        mpatches.Patch(color=C["primary"], label="Inference pipeline"),
        mpatches.Patch(color=C["accent"], label="Intelligence engines"),
    ]
    ax.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
              bbox_to_anchor=(0.5, -0.02), fontsize=9)

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[OK] wrote {path}")


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    architecture_diagram(os.path.join(ASSETS, "architecture_diagram.png"))
    workflow_diagram(os.path.join(ASSETS, "workflow_diagram.png"))
    print("Diagrams generated in", ASSETS)
