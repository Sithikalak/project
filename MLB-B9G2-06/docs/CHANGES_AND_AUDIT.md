# Corrected project — audit and change guide
**MLB-B9G2-06 · Created by Kaveesha Tennakoon · 6 October 2026**

## 1. Bro, මේ remake එකේ අරමුණ
අපේ assigned dataset එක `diabetes_prediction_dataset.csv`. Previous-year ZIP එකේ dataset එක Framingham; target එක `TenYearCHD`. අපේ target එක `diabetes`. ඒ නිසා ඒ project එකේ layout සහ numbered explanation pattern එක adapt කළා; heart-disease columns, patient claims හෝ results අපේ project එකට copy කළේ නැහැ.

කලින් project එක සම්පූර්ණයෙන් වැරදි නැහැ. Exact duplicate removal, stratified train/test split, one-hot encoding සහ implementation-v2 inner training-only preprocessing තිබුණා. ඒ හොඳ දේ තබාගෙන පහත defects සහ presentation/reproducibility gaps හදා තියෙනවා.

## 2. Previous-year reference එකේ ඇත්තටම හමු වූ ගැටලු
Source: supplied `pipeline_for preprocessing.ipynb`, 89 cells (indices below start at 0), and ZIP model notebooks.

| Reference evidence | Problem | Our correction |
|---|---|---|
| Cells 59–60 create/show `data_capped`, but 64–65 correlate `data` | “After” heatmaps do not use capped data | After heatmap reads the actual transformed training frame |
| Cell 69 creates `data_scaled`; cell 81 exports `data` | Export bypasses the separately capped/scaled objects | One fitted Pipeline supplies all final matrices and saved transforms |
| Cells 47, 49, 55–59, 69 learn medians/modes/bounds/scales before model notebook split | Full-data learned preprocessing precedes held-out evaluation | Split first; refit learned preprocessing inside every CV fold |
| Cell 74 uses target correlation on all rows, then 75 hard-drops specific columns | Global target-based inspection and drops do not form a reproducible selection rule | Correlation is training-only descriptive EDA; keep declared inputs, compare representations |
| Models repeat `for run in range(1,4)` with same split, grid and seed | Repeated deterministic runs do not make three different model varieties | Six explicitly different candidate configurations per member |
| Absolute Windows paths | Cannot run unchanged on Colab or another laptop | Relative project paths and complete ZIP/Colab instructions |
| Framingham `LabelEncoder` / pulse pressure / CHD label | These are not our nominal inputs or prediction target | One-hot gender/smoking; diabetes-relevant derived features; diabetes target |

The reference report claims normalization, but the reviewed pipeline export path does not propagate `data_scaled`. We follow executable code when claims conflict. We inspected notebook source and report; we did not execute or unpickle the previous group's models.

## 3. අපේ කලින් version එකෙන් වෙනස් කළේ මොනවාද?

| Area | Previous project | Corrected project | Why / qualification |
|---|---|---|---|
| Main notebook | Integrated, but implementation mostly behind `run_member(...)` | Numbered preprocessing sections; explicit model/grid/CV/evaluation cells | Code is easier to demonstrate and audit |
| Transformation order | Derived features before base-feature capping | Impute → optional BMI cap → derived features → encoder/scaler | Derived BMI group matches the BMI fed forward; interaction follows transformed inputs |
| Outliers | Caps age, BMI, HbA1c and glucose | Audits all four; baseline keeps all; enhanced recipe caps BMI only | Statistical extremes can contain positive-class signal; no blanket assumption of measurement error |
| HbA1c flags | Training upper bound 8.3; 1,041 training rows beyond bounds, all label=1 | Preserve measurements | Avoid flattening distinctive positive-class measurements; this is dataset evidence, not a diagnostic rule |
| Glucose flags | Training upper bound 247.5; 1,598 flagged training rows, all label=1 | Preserve measurements | Same reason; counts overlap and must not be summed as unique people |
| BMI cap | Used for both old representations | Compared as part of one optional enhanced recipe | BMI flags can also be genuine; 4,244 flagged train records include 997 positives. This remains a modeling hypothesis |
| Binary inputs | Scaled with other numeric fields | `hypertension` / `heart_disease` retained as 0/1 | Easier interpretation; scaling binaries was not automatically invalid |
| Age bands | More numerous labels with a boundary-label mismatch around 70 | Explicit `under_20`, `20_to_under_40`, `40_to_under_60`, `60_plus` | Label wording matches `right=False` bin boundaries |
| Validation | Single inner holdout for classifiers | Same 3 stratified folds for five classifiers | Reports mean and fold SD, reducing reliance on one validation split; not nested CV |
| Class weights | Balanced classifier/MLP weighting | Empirical class prevalence (uniform weights) | Transparent common baseline; F1/PR metrics still assess minority performance. Weight changes are disclosed, not credited solely to preprocessing |
| Artifacts | Result files without a deployable fitted model | Six trusted raw-input model pipelines and fitted preprocessing artifact | Inference does not need to reconstruct transformations manually |
| Graph labels | Correlation figure had `annot=False` | Pearson values `.2f`, matrix counts as integers, score values `.4f` | Instructor can read exact numbers, not colors alone |
| CSV provenance | Positional row alignment / saved processed split dependency | Raw-row IDs plus explicit split manifest | Trace any matrix row back to source |
| Test interpretation | Existing benchmark results already inspected | Same test membership retained and explicitly called reused benchmark | Cannot honestly claim a pristine unseen test set now |

**Important experiment limit:** P1 vs P2 jointly changes BMI handling and feature engineering. Their score difference measures the complete recipe change, not either operation separately. This is a remake, not a controlled one-factor causal experiment. A future ablation could isolate those effects.

## 4. Correct combined flow
1. Read original CSV; verify schema, binary labels, missingness and categories.
2. Remove exact full-row duplicates (Member 2), retaining original row IDs.
3. Stratified seed-42 train/test split; preserve prior membership for comparability.
4. **Inside the fitting partition:** learn medians/modes (Member 1).
5. Inspect IQR flags; optionally cap BMI using fitting-partition bounds (Member 4).
6. Derive age/BMI bands, condition count, interaction (Member 6).
7. Learn one-hot categories (Member 3); learn StandardScaler on numeric fields (Member 5).
8. Fit each member’s model. During tuning, all preceding learned steps refit inside that CV fold.
9. Choose highest mean CV F1 for classifiers; refit on all training rows; evaluate the test benchmark.
10. Save the **whole fitted pipeline**. Exported matrices are inspection outputs, not CV inputs.

## 5. Members — roles retained
| Member | Student | Preprocessing | Implementation |
|---|---|---|---|
| 1 | Hewapathirana S.L. — IT25101528 | Missing-data audit and safe imputation | Logistic Regression |
| 2 | Tennakoon T.A.K. S — IT25103321 | Exact duplicate removal | Decision Tree |
| 3 | Siriwardena H.A.Y.W. — IT25102977 | One-hot encoding | Linear SVM |
| 4 | Herath H.M.H.D.P. — IT25100252 | Outlier audit / optional BMI handling | Random Forest |
| 5 | Hakkam M.N.A. — IT25102336 | Feature scaling | K-Means |
| 6 | Ranaviraja R.W.H.M.V.K.B — IT25101007 | Feature engineering | MLP |

Hakkam, bro: உன் preprocessing part **feature scaling**. Scaler-ஐ training data-வில் மட்டும் fit செய்து, அதே fitted scaler-ஐ validation/test data-க்கு பயன்படுத்துகிறோம். உன் model **K-Means**; diabetes labels training அல்லது selection-க்கு பயன்படுத்தப்படவில்லை. இரண்டு preprocessing recipes × மூன்று k values = ஆறு candidates. Silhouette score-ஐ classifiers-ன் F1 score உடன் ஒப்பிடக் கூடாது.

## 6. How many experiments?
- Five classifiers: 6 parameter/recipe candidates each, 3-fold CV → **90 CV fits** plus **5 final refits**.
- K-Means: 2 recipes × k=2,3,4 → **6 validation fits** plus **1 final refit**.
- Total: **36 distinct candidates, 96 validation/CV fits, 6 final model refits**. Preprocessing demonstration fits are not extra model experiments.
- Candidate selection uses F1 for classifiers. K-Means uses silhouette on a declared common original-feature reference geometry and the same sampled validation rows.
- MLP is scikit-learn `MLPClassifier`, not TensorFlow; the brief provides examples and does not require one specific framework. No unexecuted TensorFlow result is claimed.
- Best model for the presentation is selected by **mean CV F1**, not whichever test score looks largest. All six members still present their own contribution.

## 7. Heatmaps කියවන්නේ කොහොමද?
- Correlation plots: row/column are features. Cell value is Pearson r, range −1 to +1. Diagonal is normally 1.00. A constant feature gives undefined correlation (blank), not zero.
- Positive linear scaling does not itself change Pearson r. Do not claim a changed correlation matrix proves scaling “improved” data.
- Confusion matrices: rows actual labels, columns predicted labels. Top-left TN, top-right FP, bottom-left FN, bottom-right TP. Numbers are counts.
- Group metric heatmap: values range 0–1 but columns measure different things. CV F1 and test F1 are not the same partition. K-Means is deliberately excluded from this classification score ranking.

## 8. Remaining honest limitations
This dataset has no patient identifiers, dates, external-cohort validation or confirmed sampling framework. Exact distinct rows are not proven distinct people. Reusing the test benchmark and selecting among many candidates limits generalization claims. BMI/age bands are descriptive, not clinical recommendations. No balancing-by-SMOTE, threshold calibration, nested CV or external validation is claimed. A missing-value safety layer and unknown-category handling do not replace frontend input validation. No live medical prediction app is built here.

## 9. Assessment alignment
The current Progress Review I PDF requires six member technique notebooks plus combined `group_pipeline.ipynb`, raw data and results. The implementation brief requires different model varieties, preprocessing/hyperparameter changes, appropriate metrics, validation and a group comparison of six models; it explicitly permits clustering. Therefore Hakkam remains K-Means rather than silently changing his assigned model to match the previous year's KNN.

## 10. Technical references
- User-supplied Progress Review I — Data Preprocessing and EDA PDF.
- User-supplied Final Evaluation — Implementation PDF.
- User-supplied previous-year ZIP and `pipeline_for preprocessing.ipynb`, reviewed as examples rather than authoritative correct code.
- scikit-learn: https://scikit-learn.org/stable/common_pitfalls.html
- scikit-learn: https://scikit-learn.org/stable/modules/cross_validation.html

### Reference-export verification
The previous-year `Data/newHeartDiseasedataset.csv` has **4,240 rows × 13 columns**, not the report's 13 features plus target. `age` range is **32–70**, BMI **15.54–56.80**, glucose **40–394**. These raw-scale ranges corroborate that the reviewed exported CSV did not receive the claimed Min-Max scaling. The report mentions `sysBP`, but it is absent from this export; `diaBP` remains. These discrepancies are reasons to follow traceable executed code rather than copy the old report.

### Additional data ambiguity
The retained benchmark split contains **20 distinct identical input-vector hashes across train/test**, despite exact full-row deduplication. These records have different diabetes labels (otherwise the full rows would have been duplicates). They may represent different people with the same measured attributes or conflicting records; the data cannot distinguish those cases. We retain the original labels rather than inventing a correction. Therefore row-disjoint splits are not evidence of patient-level independence. A future grouped-by-input sensitivity experiment could test this small ambiguity, but it would change the benchmark and still would not recover missing patient identifiers.
