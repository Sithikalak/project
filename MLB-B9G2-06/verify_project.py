"""Meaningful reproducibility and inference checks for the rebuilt project."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,nbformat,joblib
from sklearn.metrics import f1_score,confusion_matrix
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root/'src'))
from project_core import *
raw,clean,tr,te,yt,ye=load_dataset(root)
checks=[]
def ok(name,condition):
    assert condition,name
    checks.append(name)
ok('Source row count and duplicate accounting',len(raw)==100000 and len(clean)==96146 and raw.duplicated().sum()==3854)
ok('Disjoint raw row IDs and preserved membership',not set(tr.index)&set(te.index) and len(tr)==76916 and len(te)==19230)
manifest=pd.read_csv(root/'results/outputs/split_manifest.csv')
ok('Manifest matches exact split',set(manifest.loc[manifest.split=='train','raw_row_id'])==set(tr.index))
for path in root.rglob('*.ipynb'):
    nb=nbformat.read(path,4);nbformat.validate(nb)
    cells=[c for c in nb.cells if c.cell_type=='code']
    ok(path.name+' — all cells executed without errors',all(c.execution_count is not None and not any(o.output_type=='error' for o in c.outputs) for c in cells))
    ok(path.name+' — visible tables/figures',any(o.output_type=='display_data' for c in cells for o in c.outputs))
pre=joblib.load(root/'models/preprocessing_engineered.joblib')
saved=pd.read_csv(root/'results/outputs/X_test_engineered.csv',index_col='raw_row_id')
ok('Saved test matrix equals fitted transform',np.allclose(saved.values,pre.transform(te)))
ok('Imputation fitted to training medians only',np.allclose(pre['prepare'].medians_.values,tr[CONT].median().values))
ok('No target/input provenance leaked into model features',not set(['diabetes','split','raw_row_id'])&set(pre.get_feature_names_out()))
# Real edge case: missing values plus unseen nominal input must remain finite.
edge=te.head(2).copy();edge.iloc[0,edge.columns.get_loc('bmi')]=np.nan;edge.iloc[0,edge.columns.get_loc('gender')]='unseen_category';edge.iloc[1,edge.columns.get_loc('age')]=np.nan
ok('Missing/unseen input transform is finite',np.isfinite(pre.transform(edge)).all())
state=pre['prepare'].medians_.copy();pre.transform(edge)
ok('Inference does not mutate learned state',pre['prepare'].medians_.equals(state))
try:pre.transform(te.head(1).assign(diabetes=0));rejected=False
except ValueError:rejected=True
ok('Target accidentally passed as input is rejected',rejected)
for member,name in MODELS.items():
    result=json.loads((root/f'results/modeling/m{member}_{name}_result.json').read_text())
    pipe=joblib.load(root/f'models/m{member}_{name}_pipeline.joblib')
    ok(name+' fits full training preprocessing',pipe['preprocess']['prepare'].fit_rows_==len(tr))
    ok(name+' handles missing/unseen inputs',len(pipe.predict(edge))==2)
    if member!=5:
        cv=pd.read_csv(root/f'results/modeling/m{member}_{name}_cv.csv')
        ok(name+' six candidates and three folds',len(cv)==6 and all(f'split{i}_test_f1' in cv for i in range(3)))
        ok(name+' selection uses highest mean CV F1',np.isclose(result['cv_f1'],cv.mean_test_f1.max()))
        evidence=pd.read_csv(root/f'results/modeling/m{member}_{name}_predictions.csv')
        pred=pipe.predict(te)
        ok(name+' artifact reproduces all saved test predictions',np.array_equal(pred,evidence.predicted.values))
        ok(name+' reported F1 recomputed',np.isclose(f1_score(ye,pred),result['f1']))
        ok(name+' reported confusion counts recomputed',np.array_equal(confusion_matrix(ye,pred).ravel(),[result[x] for x in ['tn','fp','fn','tp']]))
    else:ok('KMeans six distinct label-free candidates',len(pd.read_csv(root/'results/modeling/m5_KMeans_variants.csv'))==6)
# Verify portable figure files and embedded notebook image payloads.
from PIL import Image
import io,base64
for fig in (root/'results/eda_visualizations').glob('*.png'):
    with Image.open(fig) as im:im.verify()
    ok(fig.name+' decodes',True)
for path in root.rglob('*.ipynb'):
    for cell in nbformat.read(path,4).cells:
        for output in cell.get('outputs',[]):
            if 'image/png' in output.get('data',{}):
                with Image.open(io.BytesIO(base64.b64decode(output.data['image/png']))) as im:im.verify()
ok('Every embedded notebook PNG decodes',True)
# Identical input values with different outcomes are not exact full-row duplicates.
h1=pd.util.hash_pandas_object(tr,index=False);h2=pd.util.hash_pandas_object(te,index=False)
overlap=len(set(h1)&set(h2))
info={'checks_passed':len(checks),'checks':checks,'identical_input_hashes_across_split':overlap,
      'overlap_note':'Full-row duplicates removed; some identical input vectors with differing labels remain. No patient IDs, so do not claim patient-level independence.',
      'python':platform.python_version(),'sklearn':sklearn.__version__}
(root/'results/logs/verification.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
