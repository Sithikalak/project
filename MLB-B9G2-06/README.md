# MLB-B9G2-06 — corrected diabetes preprocessing and implementation
Created by **Kaveesha Tennakoon** · 6 October 2026

## Start here
1. Read `docs/CHANGES_AND_AUDIT.md` for the source-code audit and corrected decisions.
2. Open `group_pipeline.ipynb`: 13 numbered sections; original CSV → audit → duplicates → split → training-only transforms → annotated heatmaps → exact exports.
3. Each member opens their `notebooks/IT_Number_Model_*.ipynb` and matching preprocessing notebook.
4. Open `implementation_pipeline.ipynb` for the six-member comparison and CV-based presentation recommendation.
5. Read `docs/RESULTS_AND_RUN_GUIDE.md` for executed results, limitations and demonstration order.

## Folder layout
```text
MLB-B9G2-06/
  README.md
  requirements.txt
  run_all.py
  verify_project.py
  group_pipeline.ipynb
  implementation_pipeline.ipynb
  data/raw/diabetes_prediction_dataset.csv
  notebooks/
    IT25101528_MissingDataAudit.ipynb
    IT25101528_Model_LogisticRegression.ipynb
    IT25103321_DuplicateRemoval.ipynb
    IT25103321_Model_DecisionTree.ipynb
    IT25102977_CategoricalEncoding.ipynb
    IT25102977_Model_LinearSVM.ipynb
    IT25100252_OutlierHandling.ipynb
    IT25100252_Model_RandomForest.ipynb
    IT25102336_FeatureScaling.ipynb
    IT25102336_Model_KMeans.ipynb
    IT25101007_FeatureEngineering.ipynb
    IT25101007_Model_MLP.ipynb
  src/project_core.py
  src/execute_notebook.py
  models/                       Fitted full raw-input pipelines
  results/eda_visualizations/    Annotated PNG figures
  results/outputs/               Stage CSVs, split manifest, numeric matrices
  results/modeling/              CV candidates, final metrics, prediction evidence
  results/logs/                  Execution, warnings, verification
  docs/                         Audit, team and run guide
```

## Local setup / rerun
Use Python 3.12 (tested build version recorded in the result guide).
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python run_all.py
python verify_project.py
```
The runner launches a fresh Python process for every notebook, executes Python cells in order and captures actual tables/figures/stdout. It avoids network-kernel requirements in restricted environments. The same notebooks also open normally in Jupyter or Colab. No cell output is fabricated. Expect full model tuning to take time on your laptop.

## Google Colab — easiest method
1. Start a blank Colab notebook; upload the complete delivered ZIP, not only one `.ipynb`.
2. Extract the ZIP into `/content`:
```python
from google.colab import files
import zipfile
uploaded = files.upload()
zip_name = next(name for name in uploaded if name.endswith('.zip'))
with zipfile.ZipFile(zip_name) as archive:
    archive.extractall('/content')
```
3. Install tested dependencies:
```python
%pip install -r /content/MLB-B9G2-06/requirements.txt
```
If Colab reports that already imported packages changed, restart the session before running project cells. Uploaded files remain for that session; they are not permanent storage.
4. Execute all notebooks:
```python
!python /content/MLB-B9G2-06/run_all.py
!python /content/MLB-B9G2-06/verify_project.py
```
Or open an individual notebook via Colab's notebook upload, set `PROJECT_ROOT = Path('/content/MLB-B9G2-06')` in its setup cell, and run top-to-bottom after extracting the complete project.
5. Download the rerun folder as a ZIP if you want to retain Colab outputs. Do not mix old result files with this version.

## Predict using a saved artifact (future frontend integration)
```python
import sys, joblib, pandas as pd
from pathlib import Path
root = Path('MLB-B9G2-06')  # adjust to actual extracted location
sys.path.insert(0, str(root/'src'))
# Choose model from results/modeling/recommended_model.json.
# Example member pipeline path; this is not an assertion that it wins this run:
pipe = joblib.load(root/'models/m2_DecisionTree_pipeline.joblib')
row = pd.DataFrame([dict(gender='Female', age=45, hypertension=0,
    heart_disease=0, smoking_history='never', bmi=26.0,
    HbA1c_level=5.5, blood_glucose_level=120)])
print(pipe.predict(row))
```
The example is synthetic. Model output is an educational dataset-label prediction, not a diagnosis. Only load trusted joblib files. K-Means returns cluster IDs, not diabetes labels. New form values still require application-level validation.

## Submit / present
The preprocessing brief asks for one group ZIP in Courseweb with individually named notebooks, `group_pipeline.ipynb`, raw data and results. This rebuilt project contains those plus the implementation stage. Use the lecturer's current final-submission instructions for the upload slot; the implementation brief itself assesses the viva and does not specify a new upload filename. The folder retains your current group ID, not last year's ID.

Show actual code and saved outputs; a result-display notebook is not live training. All six members must demonstrate their own techniques/models. Older PDF/HTML guides contain older parameter choices and scores and must not be used as numerical evidence for this rebuilt run.
