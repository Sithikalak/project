# Executed results and demonstration guide
**MLB-B9G2-06 · Created by Kaveesha Tennakoon · Corrected run, 6 October 2026**

## 1. Completed work
All **14 notebooks** executed: 6 individual preprocessing notebooks, 6 model notebooks, 1 integrated preprocessing notebook and 1 implementation comparison notebook. The implementation contains **36 distinct candidates**, **96 CV/validation fits** and **6 final model refits**. Outputs include actual tables, annotated figures and fitted model artifacts.

Automated verification passed **105 checks**, including exact saved-model prediction agreement, matrix/transform agreement, split provenance, notebook execution, target exclusion and missing/unseen-input handling.

## 2. Which model should we present?
The declared selection rule is **highest mean 3-fold CV F1**. It selects **Member 6’s MLP**, P2V2 (engineered features + optional BMI handling, hidden layers 64/32, alpha 0.001).

Bro, MLP CV F1 **0.801187**, Random Forest **0.800961**, Decision Tree **0.799621**. MLP–RF difference is only **0.000227** (0.0227 percentage points). Fold SDs are around 0.008–0.011, so this tiny ranking is not evidence of a clear statistically reliable winner. We did not run a significance test. Decision Tree is still especially easy to explain in a live demo. If choosing it for simplicity, explicitly say that simplicity is the reason rather than claiming it won this CV run.

Random Forest has the highest **observed test F1**, 0.809257. This does not override the training-side selection rule. Test data were already inspected in the old project; the scores are a reused benchmark, not new independent proof.

| Member | Model | Candidate | Mean CV F1 | Fold SD | Test F1 | Test precision | Test recall | FP | FN |
|---|---|---|---|---|---|---|---|---|---|
| 1 | LogisticRegression | P2V3 | 0.7359 | 0.0073 | 0.7426 | 0.8771 | 0.6439 | 153 | 604 |
| 2 | DecisionTree | P1V1 | 0.7996 | 0.0085 | 0.8082 | 1.0000 | 0.6781 | 0 | 546 |
| 3 | LinearSVM | P2V3 | 0.7322 | 0.0053 | 0.7340 | 0.9013 | 0.6191 | 115 | 646 |
| 4 | RandomForest | P1V2 | 0.8010 | 0.0080 | 0.8093 | 0.9983 | 0.6804 | 2 | 542 |
| 6 | MLP | P2V2 | 0.8012 | 0.0113 | 0.8060 | 0.9872 | 0.6810 | 15 | 541 |

## 3. Hakkam’s clustering result
Bro, உன் K-Means-க்கு selected recipe **original features, k=4**. Validation silhouette **0.1626**, test silhouette **0.1609**. இது common reference feature space-ல் எடுத்த score. Diabetes label training/selection-க்கு பயன்படுத்தப்படவில்லை; cluster composition table-ல் மட்டும் பின்னர் பார்க்கிறோம். இந்த score-ஐ F1 என்று சொல்லக்கூடாது.

The earlier K-Means silhouette (0.4265) used a different engineered reference geometry and scaled binary inputs. It is **not directly comparable** with the new 0.1609. Do not interpret the numerical drop as proof that clustering got worse.

## 4. Previous vs corrected test F1
These are the same benchmark row memberships. Several things changed together: clipping policy, derived-feature order/bands, binary scaling, class weights and validation method. Differences cannot be attributed to one specific correction.

| Member | Old test F1 | Corrected test F1 | Interpretation |
|---|---|---|---|
| 1 | 0.5713 | 0.7426 | Whole-workflow comparison, not isolated causal effect |
| 2 | 0.8082 | 0.8082 | Whole-workflow comparison, not isolated causal effect |
| 3 | 0.5736 | 0.7340 | Whole-workflow comparison, not isolated causal effect |
| 4 | 0.7779 | 0.8093 | Whole-workflow comparison, not isolated causal effect |
| 6 | 0.6228 | 0.8060 | Whole-workflow comparison, not isolated causal effect |

## 5. Your Member 2 explanation
මගේ preprocessing contribution එක exact duplicate removal. Records 100,000 අතර duplicates 3,854ක් අයින් කරලා records 96,146ක් තියාගත්තා. ඒවා unique patients කියලා claim කරන්නේ නැහැ. Implementation එකේ Decision Tree candidates හයක්, 3-fold CV යටතේ compare කළා. Selected P1V1: original features, max_depth=3, min_samples_leaf=50. Mean CV F1 0.7996; test F1 0.8082. Test false positives 0 වුණත් false negatives 546ක් නිසා model එක perfect නෙවෙයි.

**Old P2V1 and new P1V1 labels are version-specific.** In the corrected version P1 means original/uncapped; P2 means engineered/BMI-capped. Do not mix identifiers or screenshots from the old guide.

## 6. Instructor walkthrough
1. Open `group_pipeline.ipynb`. Show schema, missing counts, duplicate/class counts and the fixed split.
2. Show Step 07 outlier audit and explain why statistical outliers are not automatically deleted.
3. Show Steps 08–10: features are created after handling raw inputs; nominal features one-hot encoded; binary inputs remain 0/1.
4. Show Steps 05 and 11 annotated heatmaps, then Step 12 exports. The final CSV and joblib transform agree numerically.
5. Each member opens their model notebook: six configurations, explicit `GridSearchCV` or K-Means training function, saved validation scores, final errors and fitted artifact.
6. Open `implementation_pipeline.ipynb`. Explain the CV-selected MLP, extremely close top-three scores, and K-Means as a separate task.
7. Show a saved pipeline predicting from raw fields. This confirms inference wiring, not a deployed frontend.

Suggested 20 minutes: project 2 min; preprocessing integration 3 min; each member model 1.5 min (9 min); comparison 3 min; questions 3 min.

## 7. What to submit / run
Use the new corrected ZIP as one complete project. Avoid copying only new notebooks into the old folder because old source code and outputs can then mix. `README.md` includes local and Colab instructions, exact member filenames and repository layout. Current assessment instructions remain authoritative for the final submission slot.

The runner executes real Python cells sequentially in a fresh process per notebook; this environment did not permit a network Jupyter kernel. Actual notebook tables and figures were saved. Correlation and group comparison images were visually inspected. The rebuild is not a live frontend and has not been validated on an external dataset.

## 8. Future improvements (not claimed as completed)
External patient-level validation, a grouped-input sensitivity split, isolated ablations, calibrated probabilities and thresholds selected within training-only validation. Larger CV/nested CV could assess selection stability. Preserve all six contributions and discuss remaining false negatives.
