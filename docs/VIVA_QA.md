# ❓ Viva Questions & Answers
### Intelligent Skill Profiling for Career Readiness & Growth Pathways

A comprehensive Q&A bank covering the project, the ML concepts behind it, and likely follow-ups.

---

## A. Project Overview

**Q1. What does your project do in one sentence?**
It analyses a student's skills and interests to predict the best-fit career (with a confidence score), measure industry readiness on a 0–100 scale, detect skill gaps, and generate a personalised learning roadmap — delivered as a Streamlit web app.

**Q2. Why is this a machine-learning problem and not just `if/else` rules?**
The career recommendation is framed as **multi-class classification**: from 54 profile features the model predicts one of 10 careers and outputs a probability distribution (confidence). While we *seed* the labels from an expert rubric, the trained model **generalises** to unseen skill combinations and yields calibrated probabilities, which plain rules cannot.

**Q3. Who are the users and what's the benefit?**
Students and career counsellors. The benefit is **clarity** — a concrete role, a readiness number, an explicit gap list, and an actionable 30/90-day plan, all in one place.

---

## B. Dataset & Preprocessing

**Q4. Describe the dataset.**
"Student Skill-Gap Analysis" — 500 records, 14 columns: academic year, course, technical/programming/soft skills (multi-value), two 1–5 ratings, a projects flag, career interest, learning challenge, support needed and learning method.

**Q5. What preprocessing steps did you implement?**
Missing-value imputation (median/mode/empty), duplicate removal, IQR-based outlier detection, feature engineering, encoding (one-hot + multi-hot) and scaling (`StandardScaler`).

**Q6. The data has no missing values — why build imputation?**
Production robustness. Future or partially-filled data must not crash the pipeline, so we impute defensively.

**Q7. How did you handle the multi-value skill columns?**
Comma-separated cells are parsed into lists and then **multi-hot encoded** — one binary column per known skill token (8 technical + 7 languages + 6 soft = 21 columns).

**Q8. How are outliers detected?**
Using the **1.5 × IQR** rule on numeric/engineered columns; values outside `[Q1−1.5·IQR, Q3+1.5·IQR]` are flagged (and can be winsorised). Ratings are bounded 1–5, so genuine outliers are rare.

---

## C. Feature & Target Engineering

**Q9. How many features and of what kind?**
54 features: 8 numeric (ratings, skill counts, readiness score, ordinal year, project flag), 25 one-hot categorical, 21 multi-hot skill columns.

**Q10. What is the prediction target and where does it come from?**
The target `recommended_career` (10 classes). Since the dataset has no ground-truth best-fit career, we engineer it with a **transparent expert decision rubric**: the career interest selects a family, then course/signature-skills/ratings refine the specific role.

**Q11. Isn't engineering the label "cheating" / data leakage?**
No — it's the well-known **"distil expert rules into a learnable model"** pattern (knowledge distillation / weak supervision). The rubric encodes domain expertise; the model learns to generalise it. We deliberately add **6% label noise** so the task is non-trivial — otherwise tree models would memorise the rule and report a misleading 100%. Importantly, the model is evaluated on a held-out split, and no per-career affinity score is fed as a feature.

**Q12. Why include the readiness score as a feature?**
It's a strong, engineered signal summarising skill breadth and proficiency. It's a *scalar* derived from raw inputs, not the target, so it improves accuracy without leaking the label.

---

## D. Modelling & Evaluation

**Q13. Which models did you train and why these?**
Logistic Regression (linear baseline), Decision Tree (interpretable non-linear), Random Forest (bagging), Gradient Boosting and XGBoost (boosting). They span the bias-variance spectrum and let us compare linear vs ensemble methods.

**Q14. How is the best model selected?**
By the **highest mean 5-fold stratified cross-validation F1**, then refit on the full dataset and serialised. CV (not a single split) reduces selection variance.

**Q15. What were the results?**
Random Forest won: **94% accuracy, 0.94 macro-F1, 0.909 CV-F1**. Ensembles clustered at the top; Logistic Regression trailed (0.74) because the decision boundary is non-linear.

**Q16. Why did Logistic Regression underperform?**
The target is a **rule/tree-shaped, non-linear** function of the features. A linear model can't capture the conditional "interest → family → refine" logic, so tree ensembles win.

**Q17. Why Random Forest over the single Decision Tree (similar accuracy)?**
Their hold-out accuracy ties, but Random Forest has a **higher and more stable CV-F1** (0.909 vs 0.897) — it generalises better and is less prone to variance, which is why CV-based selection prefers it.

**Q18. Which evaluation metrics did you use and why F1?**
Accuracy, precision, recall, F1, confusion matrix and CV. **Weighted/macro-F1** is emphasised because it balances precision and recall and is robust to mild class imbalance (classes range 30–78 samples).

**Q19. How do you know the model isn't just predicting majority classes?**
**Macro-F1 = 0.94** and per-class F1 of 0.88–1.00 (including minority careers like ML Engineer and Full Stack) show balanced performance, not majority bias.

**Q20. What does feature importance tell you?**
The top features — `career_interest_*`, `JavaScript`, `Cloud Computing`, `has_projects`, `Go`, `Data Analysis`, `readiness_score` — exactly match the rubric's decision variables, confirming the model learned the intended logic.

**Q21. How is the confidence score computed?**
It's the **maximum class probability** from the model's `predict_proba` output for the predicted career.

**Q22. How do you prevent overfitting?**
`min_samples_leaf`, bounded tree depth, bagging/`max_features` in Random Forest, regularisation (`C`, `reg_lambda`), cross-validation for selection, and an unseen test split for reporting.

---

## E. Readiness, Gaps & Pathways

**Q23. How is the readiness score calculated?**
A weighted sum: Technical 40%, Programming 20%, Soft 20%, Projects 10%, Career-Alignment 10%, scaled to 0–100 and bucketed into Beginner / Intermediate / Advanced / Industry Ready.

**Q24. Why is readiness rule-based and not ML?**
Transparency. A student must understand *exactly* why their score is what it is — a black box would undermine trust. The score is deterministic and fully explainable.

**Q25. How does skill-gap detection work?**
It compares the student's skills against the **requirement profile** of the predicted career (weighted skills, languages, soft skills) and reports missing items, strengths, weak pillars and a fit %.

**Q26. How is the growth pathway generated?**
From the gap report: priority-ordered skills (with reasons), portfolio projects, levelled certifications, curated resources mapped per skill, an interview-prep plan, and weekly / 30-day / 90-day plans that adapt to the readiness band.

---

## F. Application & Engineering

**Q27. Why Streamlit?**
Rapid, Python-native interactive web apps with built-in widgets, session state and easy Plotly integration — ideal for an ML dashboard without separate front-end code.

**Q28. How do you keep training and inference consistent?**
Both call the **same** `preprocessing.featurize()` with a fixed, config-driven column order, and inference reindexes to the saved `feature_columns`. This guarantees a single form row is encoded identically to the training matrix (no feature skew).

**Q29. How is the model persisted and loaded?**
The best pipeline (scaler + estimator), the label encoder and the feature-column list are saved with **`joblib`** and lazily loaded (and cached) at inference time.

**Q30. How did you test the app?**
End-to-end **AppTest** smoke tests render all six pages and a full profile→prediction→roadmap flow, asserting no exceptions. (This caught a real Plotly colorscale bug.)

**Q31. What happens if the model file is missing?**
`predict.py` **gracefully falls back** to the rule-based rubric, so the app still functions; the sidebar prompts the user to run `train.py`.

**Q32. Is XGBoost required?**
No — it's an **optional import**. If absent, the app trains the other four models and runs normally.

**Q33. How is dark mode supported?**
Charts use transparent backgrounds and no hard-coded font colour, and the CSS uses translucent surfaces, so the UI adapts to Streamlit's light/dark theme (togglable at runtime).

---

## G. Concept Refreshers (likely follow-ups)

**Q34. Bias-variance trade-off?**
Bias = error from over-simplified assumptions (underfitting); variance = sensitivity to training data (overfitting). Ensembles like Random Forest reduce variance via averaging; regularisation/CV manage the trade-off.

**Q35. Bagging vs Boosting?**
**Bagging** (Random Forest) trains trees independently on bootstrap samples and averages them (variance reduction). **Boosting** (GB/XGBoost) trains trees sequentially, each correcting the previous one's errors (bias reduction).

**Q36. Why StandardScaler, and does it matter for trees?**
It standardises features to mean 0 / variance 1 — essential for Logistic Regression. Trees are scale-invariant, so it's harmless but kept for pipeline uniformity.

**Q37. What is stratified K-fold cross-validation?**
K-fold CV that preserves the class distribution in each fold — important for multi-class problems so every fold is representative.

**Q38. One-hot vs label encoding — why one-hot here?**
Most categoricals are **nominal** (no order), so one-hot avoids implying a false ordinal relationship. Only academic year (ordinal) uses an integer mapping.

**Q39. How would you scale this to real data?**
Replace the engineered target with **real labelled outcomes**, add resume/LinkedIn parsing, retrain periodically with a feedback loop, and monitor for data/label drift.

**Q40. What are the project's limitations?**
Self-reported skills are subjective; the source dataset's interest–skill correlation is weak (hence the engineered target). Real outcome labels and skill validation would improve external validity.
