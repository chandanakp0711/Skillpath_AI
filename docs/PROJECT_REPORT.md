# 📄 Project Report
## Intelligent Skill Profiling for Career Readiness & Growth Pathways

---

### Table of Contents
1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Problem Statement & Objectives](#3-problem-statement--objectives)
4. [Dataset Description](#4-dataset-description)
5. [Methodology](#5-methodology)
6. [Career-Readiness Scoring System](#6-career-readiness-scoring-system)
7. [Skill-Gap Detection & Growth Pathways](#7-skill-gap-detection--growth-pathways)
8. [Results & Evaluation](#8-results--evaluation)
9. [Application Design](#9-application-design)
10. [Testing & Validation](#10-testing--validation)
11. [Limitations & Future Work](#11-limitations--future-work)
12. [Conclusion](#12-conclusion)
13. [References](#13-references)

---

## 1. Abstract

Choosing a career is one of the most consequential — and most uncertain — decisions a student makes. **SkillPath AI** is an end-to-end machine-learning system that analyses a student's academic background, technical/programming/soft skills and interests to (a) **predict the most suitable career** among ten in-demand technology roles, (b) compute a transparent **0–100 career-readiness score**, (c) **detect skill gaps**, and (d) generate a **personalised, time-boxed growth roadmap**. Five classifiers are trained and compared; a **Random Forest** is automatically selected with **94% accuracy** and **0.94 macro-F1**. The system is delivered as a modern, multi-page **Streamlit** web application with 10+ interactive **Plotly** visualisations, light/dark theming and full deployment documentation.

---

## 2. Introduction

The gap between academic preparation and industry expectations is widely documented. Students frequently report uncertainty about which roles fit their skills, how "ready" they are, and what concrete steps will close the gap. Generic advice rarely accounts for an individual's specific skill mix.

SkillPath AI addresses this by combining **supervised machine learning** (for career prediction) with **transparent, rule-based domain logic** (for readiness scoring, gap detection and roadmap generation). This hybrid keeps the headline recommendation data-driven while ensuring every supporting number is fully explainable to the student — a critical property for a guidance tool.

---

## 3. Problem Statement & Objectives

**Problem.** Students lack clarity about suitable career paths, industry readiness, missing skills, learning roadmaps and certification requirements.

**Objectives.**
1. Predict a best-fit career from a student profile, with a confidence score.
2. Quantify industry readiness on an interpretable 0–100 scale.
3. Automatically identify missing skills, certifications and projects.
4. Generate a personalised learning roadmap (weekly / 30-day / 90-day).
5. Deliver everything through an attractive, user-friendly dashboard.

---

## 4. Dataset Description

**Name:** Student Skill-Gap Analysis · **Size:** 500 records × 14 columns.

| Feature | Type | Example values |
|---|---|---|
| Academic Year | Categorical (ordinal) | 1st / 2nd / 3rd / Final Year |
| Current Course | Categorical | B.Tech CSE, M.Tech AI, MBA … |
| Technical Skills | Multi-value | Python, SQL, Machine Learning … (8 tokens) |
| Programming Languages | Multi-value | Python, Java, JavaScript … (7 tokens) |
| Technical Skill Rating | Numeric (1–5) | 3 |
| Soft Skills | Multi-value | Communication, Leadership … (6 tokens) |
| Soft Skill Rating | Numeric (1–5) | 4 |
| Projects | Binary | Yes / No |
| Career Interest | Categorical | Data Scientist, AI Engineer … (6 values) |
| Learning Challenges | Categorical | Interview anxiety, Lack of experience … |
| Support Required | Categorical | Mentorship, Resume workshops … |
| Learning Method | Categorical | College curriculum, Self-study … |

**Data-quality notes.** The raw spreadsheet has messy headers (leading spaces, the misspelt `SOFT_SKILSS`, a duplicated `RATING.1`) and inconsistent academic-year labels (e.g. "Final" vs "Final Year"). The data loader normalises all of these. The dataset has no missing values or duplicates, but the pipeline still implements defensive handling for both.

---

## 5. Methodology

The pipeline implements every stage required by the specification.

### 5.1 Data Preprocessing
- **Missing values:** median imputation (numeric), mode imputation (categorical), empty-string for skill cells.
- **Duplicate removal:** exact-duplicate drop on non-PII columns.
- **Outlier detection:** 1.5 × IQR rule on numeric/engineered columns (with optional winsorising).
- **Feature scaling:** `StandardScaler` inside each model pipeline.

### 5.2 Exploratory Data Analysis
EDA spans **student distribution** (course / year / interest), **skill analysis** (top technical skills, language popularity, soft-skill spread), **readiness analysis** (score & band distribution, skill-gap summary) and **correlation analysis** (numeric correlation matrix, technical-vs-soft scatter). All are surfaced interactively in the Analytics dashboard.

Selected insight: *Career Alignment* is the weakest pillar across the cohort (~37% average attainment), and only ~49% of students report hands-on project experience — both prime targets for guidance.

### 5.3 Feature Engineering
54 model features are derived:
- Numeric: technical/soft ratings, skill-breadth counts, **engineered readiness score**, ordinal year, project flag.
- **One-hot** encodings for course, interest, challenge, support, method (25 columns).
- **Multi-hot** encodings for technical skills (8), languages (7) and soft skills (6).

### 5.4 Target Engineering
The dataset records *interest*, not *best-fit career*. We therefore engineer the target with a transparent **expert decision rubric**: the stated interest selects a career **family**, then course, signature skills and ratings refine the specific role. Reproducible label noise (6%) models real-world fuzziness and prevents tree models from trivially memorising the rule. The ten target careers are: *Data Scientist, Data Analyst, AI Engineer, Machine Learning Engineer, Cloud Engineer, DevOps Engineer, Cybersecurity Analyst, Software Developer, Full Stack Developer, Business Analyst.*

### 5.5 Modelling
Five classifiers are trained as `StandardScaler → estimator` pipelines: **Logistic Regression, Decision Tree, Random Forest, Gradient Boosting** and **XGBoost** (optional). Labels are integer-encoded for uniformity. Evaluation uses an 80/20 stratified hold-out plus **5-fold stratified cross-validation**. The model with the highest mean CV-F1 is auto-selected, refit on the full dataset, and serialised with the label encoder and feature-column list.

---

## 6. Career-Readiness Scoring System

A custom, fully transparent score (independent of the ML model):

```
Readiness (0–100) = 0.40·Technical + 0.20·Programming + 0.20·Soft
                  + 0.10·Projects + 0.10·Career-Alignment
```
- **Technical** = ½·breadth + ½·(rating/5)
- **Programming** = language breadth (capped at 3)
- **Soft** = ½·breadth + ½·(rating/5)
- **Projects** = 1.0 if "Yes" else 0.15
- **Alignment** = skill coverage of the interested career's requirements

Bands: **0–40 Beginner · 41–60 Intermediate · 61–80 Advanced · 81–100 Industry Ready.** The score is visualised as a speedometer gauge and per-pillar progress bars.

---

## 7. Skill-Gap Detection & Growth Pathways

**Skill-gap detection** compares the student against the requirement profile of the predicted career and reports: missing technical skills, missing languages, missing soft skills, recommended certifications, project gaps, strength areas and weak areas — each with a plain-English explanation and an overall *fit %*.

**Growth pathway** turns the gap report into action: priority-ordered skills (with reasons), portfolio project ideas, levelled certifications (e.g. *AWS Cloud Practitioner, Azure Fundamentals, Google Data Analytics, TensorFlow Developer*), curated resources (Coursera / Udemy / NPTEL / YouTube / freeCodeCamp), an interview-preparation plan, and concrete **weekly**, **30-day** and **90-day** plans that adapt to the student's readiness band.

---

## 8. Results & Evaluation

### 8.1 Model comparison (selected by CV-F1)

| Model | Accuracy | Precision | Recall | F1 | CV-F1 (±σ) |
|---|:--:|:--:|:--:|:--:|:--:|
| 🏆 **Random Forest** | **0.940** | **0.950** | **0.940** | **0.941** | **0.909 ± 0.03** |
| Decision Tree | 0.940 | 0.950 | 0.940 | 0.941 | 0.897 ± 0.03 |
| Gradient Boosting | 0.920 | 0.928 | 0.920 | 0.919 | 0.889 ± 0.02 |
| XGBoost | 0.900 | 0.908 | 0.900 | 0.899 | 0.881 ± 0.04 |
| Logistic Regression | 0.740 | 0.745 | 0.740 | 0.735 | 0.750 ± 0.02 |

### 8.2 Observations
- Tree ensembles dominate because the target is a non-linear, rule-shaped function; the linear model trails as expected.
- **Macro-F1 = 0.94** confirms strong performance across *all* ten classes, including minority careers (per-class F1 ranged 0.88–1.00).
- Top feature importances — `career_interest_*`, `JavaScript`, `Cloud Computing`, `has_projects`, `Go`, `Data Analysis`, `readiness_score` — exactly mirror the decision rubric, validating that the model learned the intended logic rather than spurious patterns.

### 8.3 Evaluation methodology
Accuracy, weighted precision/recall/F1, confusion matrix and 5-fold stratified cross-validation. CV (rather than a single split) drives model selection for robustness.

---

## 9. Application Design

A six-page Streamlit dashboard: **Home, Student Profile, Prediction, Growth Pathway, Analytics Dashboard, About.** Highlights: gradient hero banners, card-based layout, sidebar navigation with a progress tracker, custom CSS, light/dark mode, 10+ interactive Plotly charts (pie, horizontal bar, histogram, heatmap, scatter, **confidence gauge**, **readiness speedometer**), and a guided Profile → Prediction → Growth flow backed by session state.

---

## 10. Testing & Validation

End-to-end smoke tests use Streamlit's `AppTest` harness to render **every page** and run a full profile→prediction→roadmap flow, asserting zero exceptions. (This harness caught a real Plotly colorscale bug during development.) Each `src/` module additionally ships a `__main__` smoke test.

---

## 11. Limitations & Future Work

- **Synthetic-flavoured dataset.** Career interest in the source data is weakly correlated with skills; the engineered target encodes expert rules. Re-training on real labelled outcomes would increase external validity.
- **Self-reported skills/ratings** are subjective; future versions could validate via assessments or verified certificates.
- **Future work:** resume/LinkedIn parsing, an LLM-generated narrative roadmap, live job-market signals, collaborative filtering across student outcomes, and a feedback loop to continuously retrain.

---

## 12. Conclusion

SkillPath AI demonstrates a complete, production-quality ML application: a clean data pipeline, transparent feature/target engineering, rigorous model comparison with automated selection (94% accuracy), explainable readiness and gap analysis, an actionable growth roadmap, and a polished, deployable Streamlit dashboard. It is a practical blueprint for data-driven, student-facing career guidance.

---

## 13. References

1. Pedregosa et al., *Scikit-learn: Machine Learning in Python*, JMLR 2011.
2. Chen & Guestrin, *XGBoost: A Scalable Tree Boosting System*, KDD 2016.
3. Breiman, *Random Forests*, Machine Learning, 2001.
4. Streamlit Documentation — https://docs.streamlit.io
5. Plotly Python Documentation — https://plotly.com/python/
6. Course/certification references: Coursera, Udemy, NPTEL, freeCodeCamp, AWS/Azure/Google Cloud certification pages.
