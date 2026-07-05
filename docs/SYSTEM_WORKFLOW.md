# 🔄 System Workflow — SkillPath AI

The system has two tracks: an **offline training pipeline** (run once via `train.py`) and an **online inference flow** (every time a student uses the app). They meet at the saved model artefacts.

![Workflow Diagram](../assets/workflow_diagram.png)

---

## 1. Offline training pipeline (`python train.py`)

```mermaid
flowchart LR
    A[("📄 skillgap_dataset.xlsx")] --> B[Load & Clean<br/>data_loader.py]
    B --> C[Engineer Target<br/>target_engineering.py]
    C --> D[Preprocess<br/>impute · dedupe · outliers]
    D --> E[Feature Engineering<br/>readiness · counts · encodings]
    E --> F[Featurise → 54 features]
    F --> G{Train & 5-fold CV}
    G --> H1[Logistic Regression]
    G --> H2[Decision Tree]
    G --> H3[Random Forest]
    G --> H4[Gradient Boosting]
    G --> H5[XGBoost]
    H1 & H2 & H3 & H4 & H5 --> I[Compare by CV-F1]
    I --> J[/Select Best Model/]
    J --> K[("💾 best_model.pkl<br/>label_encoder.pkl<br/>feature_columns.pkl<br/>metrics.json")]
```

**Steps**

1. **Load & clean** the 500-row spreadsheet → canonical columns, normalised years, parsed skill lists.
2. **Engineer the target** `recommended_career` via the expert rubric + seeded label noise.
3. **Preprocess** — impute missing values, drop duplicates, IQR outlier scan.
4. **Feature-engineer** — readiness score, breadth counts, ordinal year, binary flags.
5. **Featurise** — one-hot + multi-hot + numeric → a fixed 54-column matrix.
6. **Train & cross-validate** 5 classifiers (StandardScaler + estimator pipelines).
7. **Select** the highest mean CV-F1 model, **refit** on all data, **serialise** with `joblib`, write `metrics.json` + `metadata.json`.

---

## 2. Online inference flow (`streamlit run app.py`)

```mermaid
sequenceDiagram
    actor S as 👤 Student
    participant UI as Streamlit UI
    participant PR as predict.py
    participant FE as preprocessing.featurize()
    participant M as Random Forest (.pkl)
    participant IN as Intelligence engines

    S->>UI: Fill profile form (skills, ratings, interest…)
    UI->>PR: predict_career(profile)
    PR->>FE: build single-row feature matrix (same path as training)
    FE-->>PR: 54-feature vector
    PR->>M: predict_proba(X)
    M-->>PR: career + probabilities (confidence)
    PR->>IN: readiness · skill-gap · alternatives
    IN-->>PR: scores + explanations
    PR-->>UI: prediction bundle
    UI-->>S: Career + gauges + gap analysis
    S->>UI: "Get my growth pathway"
    UI->>IN: generate_pathway(profile, career)
    IN-->>UI: skills · certs · resources · weekly/30/90-day plans
    UI-->>S: 🚀 Personalised roadmap
```

---

## 3. User journey

```mermaid
flowchart LR
    Home([🏠 Home]) --> Profile([👤 Build Profile])
    Profile --> Predict([🔮 Prediction + Readiness + Gaps])
    Predict --> Growth([🚀 Growth Pathway])
    Predict -. explore .-> Analytics([📊 Analytics Dashboard])
    Home -. learn .-> About([ℹ️ About])
```

**Typical flow:** Home → build a profile → view the predicted career, readiness speedometer, confidence gauge and skill-gap analysis → open the personalised growth pathway (skills, certifications, resources, interview prep, 30/90-day plans). The Analytics dashboard and About page are available any time from the sidebar.
