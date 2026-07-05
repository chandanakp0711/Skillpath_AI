"""
Build (and execute) the EDA + Modeling Jupyter notebook from code, so the
shipped .ipynb contains rendered plots and tables. Reuses the project's own
modules to stay DRY and loads saved metrics instead of retraining.

Run:  python scripts/build_notebook.py
"""

from __future__ import annotations

import os
import sys

import nbformat as nbf
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "notebooks", "01_EDA_and_Modeling.ipynb")

CELLS: list[tuple[str, str]] = [
    ("md", """# 📊 EDA & Modeling — Intelligent Skill Profiling for Career Readiness

This notebook walks through the data science workflow behind **SkillPath AI**:
data loading & cleaning, exploratory data analysis, feature & target engineering,
and the model-comparison results. It reuses the project's `src/` modules so it
stays perfectly in sync with the application."""),

    ("code", """import warnings; warnings.filterwarnings("ignore")
%matplotlib inline
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 110

from src.data_loader import load_clean
from src import eda, config
print("Libraries loaded. Careers:", len(config.CAREER_LIST))"""),

    ("md", "## 1. Load & inspect the dataset"),
    ("code", """df = load_clean()
print("Shape:", df.shape)
df[["academic_year","course","technical_skills","programming_languages",
    "technical_rating","soft_rating","has_projects","career_interest"]].head()"""),

    ("code", """df.describe(include=[np.number])"""),

    ("md", "## 2. Data quality — missing values & duplicates"),
    ("code", """print("Missing values per column:\\n", df.isnull().sum().to_string())
# Exclude parsed list columns (lists are unhashable) when checking duplicates.
scalar_cols = [c for c in df.columns if not c.endswith("_list")]
print("\\nDuplicate rows:", df[scalar_cols].duplicated().sum())"""),

    ("md", """## 3. Exploratory Data Analysis — Student distribution
Course-wise, academic-year and career-interest distributions."""),
    ("code", """frame = eda.build_analysis_frame()
fig, ax = plt.subplots(1, 3, figsize=(16, 4))
eda.course_distribution(frame).plot(kind="bar", ax=ax[0], color="#6366f1", title="Course-wise Distribution")
eda.year_distribution(frame).plot(kind="bar", ax=ax[1], color="#06b6d4", title="Academic-Year Distribution")
eda.career_interest_distribution(frame).plot(kind="bar", ax=ax[2], color="#22c55e", title="Career-Interest Distribution")
for a in ax: a.set_xlabel(""); a.tick_params(axis="x", rotation=45)
plt.tight_layout(); plt.show()"""),

    ("md", "## 4. Skill analysis — technical skills, languages & soft skills"),
    ("code", """fig, ax = plt.subplots(1, 3, figsize=(16, 4))
eda.top_technical_skills(frame).sort_values().plot(kind="barh", ax=ax[0], color="#6366f1", title="Top Technical Skills")
eda.language_popularity(frame).plot(kind="bar", ax=ax[1], color="#a855f7", title="Programming-Language Popularity")
eda.soft_skill_distribution(frame).plot(kind="bar", ax=ax[2], color="#f59e0b", title="Soft-Skill Distribution")
ax[1].tick_params(axis="x", rotation=45); ax[2].tick_params(axis="x", rotation=45)
plt.tight_layout(); plt.show()"""),

    ("md", """## 5. Career-readiness analysis
The custom 0–100 readiness score and its band distribution."""),
    ("code", """fig, ax = plt.subplots(1, 2, figsize=(14, 4))
sns.histplot(frame["readiness_score"], bins=24, kde=True, color="#6366f1", ax=ax[0])
for b in (40, 60, 80): ax[0].axvline(b, ls="--", c="grey")
ax[0].set_title("Readiness-Score Distribution")
eda.readiness_band_distribution(frame).plot(kind="bar", ax=ax[1],
    color=["#ef4444","#f59e0b","#3b82f6","#22c55e"], title="Readiness Band Distribution")
ax[1].tick_params(axis="x", rotation=20)
plt.tight_layout(); plt.show()
print(eda.skill_gap_summary(frame).to_string(index=False))"""),

    ("md", "## 6. Correlation analysis"),
    ("code", """plt.figure(figsize=(8, 6))
sns.heatmap(eda.correlation_matrix(frame), annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, vmin=-1, vmax=1, square=True, cbar_kws={"shrink": .8})
plt.title("Feature Correlation Matrix"); plt.tight_layout(); plt.show()"""),

    ("md", """## 7. Target engineering
The ML target `recommended_career` is produced by an expert decision rubric
(interest → family → refined by course/skills) plus light label noise."""),
    ("code", """ax = eda.recommended_career_distribution(frame).sort_values().plot(
    kind="barh", figsize=(9, 4.5), color="#06b6d4",
    title="Engineered Target: Recommended-Career Distribution")
ax.set_xlabel("students"); plt.tight_layout(); plt.show()"""),

    ("md", "## 8. Preprocessing & featurisation"),
    ("code", """from src.preprocessing import run_preprocessing, featurize, detect_outliers
proc = run_preprocessing(load_clean())
X = featurize(proc)
print("Feature matrix:", X.shape)
print("Sample feature columns:", list(X.columns[:10]), "...")
print("\\nOutlier scan (IQR):")
for k, v in detect_outliers(proc).items():
    print(f"  {k:<20} outliers={v['n_outliers']} ({v['pct_outliers']}%)")"""),

    ("md", """## 9. Model comparison & evaluation
Loaded from `models/model_metrics.json` (produced by `python train.py`).
Five classifiers are compared; the best is auto-selected by 5-fold CV F1."""),
    ("code", """import json, os
with open(config.METRICS_PATH) as fh: metrics = json.load(fh)
rows = [{"Model": n, "Accuracy": round(m["accuracy"],3), "Precision": round(m["precision"],3),
         "Recall": round(m["recall"],3), "F1": round(m["f1"],3), "CV-F1": round(m["cv_f1_mean"],3)}
        for n, m in metrics["models"].items()]
comp = pd.DataFrame(rows).sort_values("CV-F1", ascending=False).reset_index(drop=True)
print("Best model (auto-selected):", metrics["best_model"])
comp"""),

    ("code", """best = metrics["models"][metrics["best_model"]]
cm = np.array(best["confusion_matrix"]); classes = metrics["classes"]
plt.figure(figsize=(8.5, 7))
sns.heatmap(cm, annot=True, fmt="d", cmap="Purples", xticklabels=classes, yticklabels=classes)
plt.title(f"Confusion Matrix — {metrics['best_model']}")
plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.xticks(rotation=45, ha="right")
plt.tight_layout(); plt.show()"""),

    ("code", """imp = metrics["feature_importance"]; top = dict(list(imp.items())[:15])
plt.figure(figsize=(9, 5))
pd.Series(top).sort_values().plot(kind="barh", color="#6366f1")
plt.title(f"Top 15 Feature Importances — {metrics['best_model']}")
plt.xlabel("importance"); plt.tight_layout(); plt.show()"""),

    ("md", """## 10. Conclusion
- The pipeline cleans 500 student records, engineers **54 features** and a transparent
  expert-rubric **target**.
- Five models are compared; **Random Forest** is auto-selected with **~94% accuracy**
  and **0.94 macro-F1**.
- Feature importances mirror the decision rubric (career interest, JavaScript, Cloud
  Computing, projects), confirming the model learned the intended logic.
- The trained artefacts power the **SkillPath AI** Streamlit app for live career
  prediction, readiness scoring, skill-gap detection and growth-pathway generation."""),
]


def build() -> None:
    nb = new_notebook()
    nb.cells = [new_markdown_cell(src) if kind == "md" else new_code_cell(src)
                for kind, src in CELLS]
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }

    try:
        from nbclient import NotebookClient
        print("Executing notebook (this runs the EDA cells)...")
        client = NotebookClient(nb, timeout=180, kernel_name="python3",
                                resources={"metadata": {"path": ROOT}})
        client.execute()
        print("[OK] executed with rendered outputs")
    except Exception as exc:  # pragma: no cover
        print(f"[warn] execution skipped ({exc}); shipping un-executed notebook")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        nbf.write(nb, fh)
    print(f"[OK] wrote {OUT}")


if __name__ == "__main__":
    sys.path.insert(0, ROOT)
    build()
