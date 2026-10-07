"""Shared, inspectable preprocessing for MLB-B9G2-06. No model is trained on import."""
from pathlib import Path
import json,hashlib,platform,warnings,time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib,sklearn
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.compose import ColumnTransformer,make_column_selector
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split,StratifiedKFold,GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier,plot_tree
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,
 average_precision_score,confusion_matrix,RocCurveDisplay,PrecisionRecallDisplay,silhouette_score)
SEED=42
CONT=['age','bmi','HbA1c_level','blood_glucose_level']
BINARY=['hypertension','heart_disease']
CAT=['gender','smoking_history']
INPUTS=['gender','age','hypertension','heart_disease','smoking_history','bmi','HbA1c_level','blood_glucose_level']
MODELS={1:'LogisticRegression',2:'DecisionTree',3:'LinearSVM',4:'RandomForest',5:'KMeans',6:'MLP'}
REPRESENTATIONS=['original','engineered_bmi_capped']
plt.rcParams.update({'font.size':10,'figure.dpi':110,'axes.spines.top':False,'axes.spines.right':False})

class RawPreparation(TransformerMixin,BaseEstimator):
    """Learn imputations and optional BMI bounds, then derive features from the transformed inputs.
    No target is accepted as an input feature. Binary and nominal features are never IQR capped.
    """
    def __init__(self,representation='original'):
        self.representation=representation
    def fit(self,X,y=None):
        X=self._validate(X)
        self.feature_names_in_=np.array(INPUTS,dtype=object)
        self.n_features_in_=len(INPUTS)
        self.medians_=X[CONT].median()
        self.modes_={c:X[c].mode().iloc[0] for c in CAT+BINARY}
        bmi=X.bmi.fillna(self.medians_['bmi'])
        q1,q3=bmi.quantile([.25,.75]);iqr=q3-q1
        self.bmi_bounds_=(float(q1-1.5*iqr),float(q3+1.5*iqr))
        self.fit_rows_=len(X)
        return self
    def _validate(self,X):
        if not isinstance(X,pd.DataFrame):raise TypeError('Pass raw inputs as a pandas DataFrame.')
        if 'diabetes' in X.columns:raise ValueError('Target diabetes must not be an input.')
        missing=set(INPUTS)-set(X.columns)
        if missing:raise ValueError(f'Missing input columns: {missing}')
        if self.representation not in REPRESENTATIONS:raise ValueError('Unknown representation')
        return X.loc[:,INPUTS].copy()
    def impute(self,X):
        out=self._validate(X)
        out[CONT]=out[CONT].fillna(self.medians_)
        for c,v in self.modes_.items():out[c]=out[c].fillna(v)
        return out
    def cap(self,X):
        out=X.copy()
        if self.representation=='engineered_bmi_capped':out['bmi']=out.bmi.clip(*self.bmi_bounds_)
        return out
    def transform(self,X):
        out=self.cap(self.impute(X))
        if self.representation=='engineered_bmi_capped':
            # Fixed bins, with correct edge labels; features follow imputation and BMI handling.
            out['age_group']=pd.cut(out.age,[-np.inf,20,40,60,np.inf],
                labels=['under_20','20_to_under_40','40_to_under_60','60_plus'],right=False).astype(object)
            out['bmi_group']=pd.cut(out.bmi,[-np.inf,18.5,25,30,np.inf],
                labels=['under_18.5','18.5_to_under_25','25_to_under_30','30_plus'],right=False).astype(object)
            out['condition_count']=out.hypertension+out.heart_disease
            out['glucose_hba1c_interaction']=out.blood_glucose_level*out.HbA1c_level
        return out
    def get_feature_names_out(self,input_features=None):
        extra=['age_group','bmi_group','condition_count','glucose_hba1c_interaction'] if self.representation!='original' else []
        return np.array(INPUTS+extra,dtype=object)

def numeric_columns(X):return [c for c in X.select_dtypes(include='number').columns if c not in BINARY]
def categorical_columns(X):return [c for c in X.columns if c in CAT or c.endswith('_group')]

def make_preprocessor(representation='original'):
    return Pipeline([
      ('prepare',RawPreparation(representation)),
      ('columns',ColumnTransformer([
        ('numeric',StandardScaler(),numeric_columns),
        ('binary','passthrough',BINARY),
        ('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),categorical_columns)
      ],verbose_feature_names_out=False))])

def load_dataset(root):
    root=Path(root);path=root/'data/raw/diabetes_prediction_dataset.csv'
    raw=pd.read_csv(path)
    assert raw.columns.tolist()==INPUTS+['diabetes']
    assert set(raw.diabetes.unique())=={0,1}
    for c in BINARY:assert set(raw[c].dropna().unique())<={0,1}
    assert (raw[CONT].dropna()>=0).all().all()
    clean=raw.drop_duplicates().copy() # Keep original raw-row indices for provenance.
    X=clean[INPUTS];y=clean.diabetes.astype(int)
    tr,te=train_test_split(np.arange(len(clean)),test_size=.2,stratify=y,random_state=SEED)
    # Sort only AFTER the split, preserving original membership from the previous project.
    tr,te=np.sort(tr),np.sort(te)
    return raw,clean,X.iloc[tr],X.iloc[te],y.iloc[tr],y.iloc[te]

def savefig(root,name):
    plt.tight_layout();plt.savefig(Path(root)/'results/eda_visualizations'/f'{name}.png',dpi=160,bbox_inches='tight');plt.show();plt.close()

def heatmap(frame,title,root,name):
    corr=frame.corr(numeric_only=True)
    size=max(8,len(corr)*.62)
    plt.figure(figsize=(size,size*.88))
    sns.heatmap(corr,annot=True,fmt='.2f',cmap='coolwarm',vmin=-1,vmax=1,center=0,
        linewidths=.4,annot_kws={'size':9},cbar_kws={'label':'Pearson correlation (r)'})
    plt.title(title);savefig(root,name)
    corr.to_csv(Path(root)/'results/outputs'/f'{name}.csv')
    return corr

def outlier_audit(train):
    rows=[]
    for c in CONT:
        q1,q3=train[c].quantile([.25,.75]);iqr=q3-q1;lo,hi=q1-1.5*iqr,q3+1.5*iqr
        rows.append({'feature':c,'q1':q1,'q3':q3,'lower':lo,'upper':hi,
          'flagged_train_rows':int(((train[c]<lo)|(train[c]>hi)).sum()),
          'action':'compare optional BMI capping' if c=='bmi' else 'retain values; do not treat IQR flag as error'})
    return pd.DataFrame(rows)

def model_and_grid(member):
    choices={
    1:(LogisticRegression(max_iter=1500,random_state=SEED),[{'C':.1},{'C':1.},{'C':10.}]),
    2:(DecisionTreeClassifier(random_state=SEED),[{'max_depth':3,'min_samples_leaf':50},{'max_depth':6,'min_samples_leaf':20},{'max_depth':10,'min_samples_leaf':10}]),
    3:(LinearSVC(dual=False,max_iter=10000,random_state=SEED),[{'C':.01},{'C':.1},{'C':1.}]),
    4:(RandomForestClassifier(n_estimators=100,n_jobs=1,random_state=SEED),[{'max_depth':8,'min_samples_leaf':10},{'max_depth':14,'min_samples_leaf':5},{'max_depth':None,'min_samples_leaf':2}]),
    6:(MLPClassifier(activation='relu',solver='adam',batch_size=256,max_iter=120,tol=.001,n_iter_no_change=10,early_stopping=False,random_state=SEED),[{'hidden_layer_sizes':(32,),'alpha':.001},{'hidden_layer_sizes':(64,32),'alpha':.001},{'hidden_layer_sizes':(64,32),'alpha':.01}])}
    model,settings=choices[member]
    # Six distinct candidates, not three repetitions of the same grid/split.
    grid=[{'preprocess__prepare__representation':[r],**{'model__'+k:[v] for k,v in p.items()}} for r in REPRESENTATIONS for p in settings]
    return model,grid

def scores(y,pred,score):
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return dict(accuracy=float(accuracy_score(y,pred)),precision=float(precision_score(y,pred,zero_division=0)),
      recall=float(recall_score(y,pred,zero_division=0)),f1=float(f1_score(y,pred,zero_division=0)),
      roc_auc=float(roc_auc_score(y,score)),average_precision=float(average_precision_score(y,score)),
      tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))

def evaluation_plots(root,member,pipe,Xtest,ytest,result):
    prefix=f'm{member}_{MODELS[member]}'
    pred=pipe.predict(Xtest)
    score=pipe.predict_proba(Xtest)[:,1] if hasattr(pipe,'predict_proba') else pipe.decision_function(Xtest)
    cm=confusion_matrix(ytest,pred,labels=[0,1])
    plt.figure(figsize=(6,5));sns.heatmap(cm,annot=True,fmt='d',cmap='Blues',xticklabels=['0','1'],yticklabels=['0','1'])
    plt.xlabel('Predicted diabetes label');plt.ylabel('Actual diabetes label');plt.title(prefix+' — test confusion counts');savefig(root,prefix+'_confusion')
    fig,ax=plt.subplots(1,2,figsize=(11,4));RocCurveDisplay.from_predictions(ytest,score,ax=ax[0]);PrecisionRecallDisplay.from_predictions(ytest,score,ax=ax[1]);savefig(root,prefix+'_roc_pr')
    names=pipe.named_steps['preprocess'].get_feature_names_out()
    if member==2:
        plt.figure(figsize=(20,8));plot_tree(pipe.named_steps['model'],feature_names=names,class_names=['0','1'],max_depth=2,filled=True,rounded=True,fontsize=9)
        plt.title('Selected tree — first three levels only; numeric thresholds are standardized');savefig(root,prefix+'_tree')
    if member==6:
        plt.figure(figsize=(8,4));plt.plot(np.arange(1,len(pipe['model'].loss_curve_)+1),pipe['model'].loss_curve_);plt.xlabel('Epoch');plt.ylabel('Training loss');plt.title('Final MLP training loss (not validation performance)');savefig(root,prefix+'_loss')
    pd.DataFrame({'raw_row_id':Xtest.index,'actual':ytest.values,'predicted':pred,'score':score}).to_csv(Path(root)/'results/modeling'/f'{prefix}_predictions.csv',index=False)


def finalize_classifier(root,member,search,Xtest,ytest):
    root=Path(root);pipe=search.best_estimator_;prefix=f'm{member}_{MODELS[member]}'
    cv=pd.DataFrame(search.cv_results_);cv['candidate']=['P'+str(i//3+1)+'V'+str(i%3+1) for i in range(len(cv))]
    cv.to_csv(root/'results/modeling'/f'{prefix}_cv.csv',index=False)
    pred=pipe.predict(Xtest);score=pipe.predict_proba(Xtest)[:,1] if hasattr(pipe,'predict_proba') else pipe.decision_function(Xtest)
    result=dict(member=member,model=MODELS[member],kind='classifier',selected=cv.iloc[search.best_index_]['candidate'],
      cv_f1=float(search.best_score_),cv_f1_std=float(cv.iloc[search.best_index_]['std_test_f1']),
      params=search.best_params_,features=len(pipe['preprocess'].get_feature_names_out()),**scores(ytest,pred,score))
    result['iterations']=int(pipe['model'].n_iter_) if member==6 else None
    result['hit_iteration_limit']=bool(member==6 and pipe['model'].n_iter_>=pipe['model'].max_iter)
    (root/'results/modeling'/f'{prefix}_result.json').write_text(json.dumps(result,indent=2,default=str))
    joblib.dump(pipe,root/'models'/f'{prefix}_pipeline.joblib',compress=3)
    loaded=joblib.load(root/'models'/f'{prefix}_pipeline.joblib')
    assert np.array_equal(pred,loaded.predict(Xtest))
    plt.figure(figsize=(8,4));bars=plt.bar(cv.candidate,cv.mean_test_f1,yerr=cv.std_test_f1,capsize=4,color='#237d92');plt.ylim(0,1);plt.ylabel('3-fold CV F1 (mean ± fold SD)');plt.title(prefix+' — six distinct candidates')
    for b,v in zip(bars,cv.mean_test_f1):plt.text(b.get_x()+b.get_width()/2,v+.025,f'{v:.4f}',ha='center',fontsize=9)
    savefig(root,prefix+'_variants')
    evaluation_plots(root,member,pipe,Xtest,ytest,result)
    return result,cv


def cluster_experiments(root,Xtrain,Xtest,ytest):
    root=Path(root)
    fit,val=train_test_split(np.arange(len(Xtrain)),test_size=.2,random_state=SEED) # labels not used
    ref=make_preprocessor('original').fit(Xtrain.iloc[fit])
    refval=ref.transform(Xtrain.iloc[val]);sample=np.random.default_rng(SEED).choice(len(val),min(2000,len(val)),replace=False)
    rows=[]
    for r in REPRESENTATIONS:
      for k in [2,3,4]:
        pipe=Pipeline([('preprocess',make_preprocessor(r)),('model',KMeans(n_clusters=k,n_init=10,random_state=SEED))])
        pipe.fit(Xtrain.iloc[fit]);labels=pipe.predict(Xtrain.iloc[val])
        score=silhouette_score(refval[sample],labels[sample])
        rows.append(dict(representation=r,k=k,validation_silhouette=float(score)))
    variants=pd.DataFrame(rows);chosen=variants.sort_values('validation_silhouette',ascending=False,kind='stable').iloc[0]
    pipe=Pipeline([('preprocess',make_preprocessor(chosen.representation)),('model',KMeans(n_clusters=int(chosen.k),n_init=10,random_state=SEED))]).fit(Xtrain)
    labels=pipe.predict(Xtest);reference=make_preprocessor('original').fit(Xtrain).transform(Xtest)
    ids=np.random.default_rng(SEED).choice(len(Xtest),2000,replace=False)
    silhouette=float(silhouette_score(reference[ids],labels[ids]))
    result=dict(member=5,model='KMeans',kind='clustering',selected=chosen.representation+' / k='+str(int(chosen.k)),validation_silhouette=float(chosen.validation_silhouette),test_silhouette=silhouette,reference_space='original standardized numeric, binary passthrough, one-hot; fitted only on appropriate training rows',sample_rows=2000)
    variants.to_csv(root/'results/modeling/m5_KMeans_variants.csv',index=False)
    (root/'results/modeling/m5_KMeans_result.json').write_text(json.dumps(result,indent=2))
    joblib.dump(pipe,root/'models/m5_KMeans_pipeline.joblib',compress=3)
    assert np.array_equal(labels,joblib.load(root/'models/m5_KMeans_pipeline.joblib').predict(Xtest))
    cross=pd.crosstab(pd.Series(labels,name='cluster'),pd.Series(ytest.to_numpy(),name='actual_diabetes')).reindex(columns=[0,1],fill_value=0)
    cross['count']=cross.sum(axis=1);cross['positive_rate']=cross[1]/cross['count'];cross.to_csv(root/'results/modeling/m5_cluster_composition.csv')
    plt.figure(figsize=(8,4));bars=plt.bar([r+' / '+str(k) for r,k in zip(variants.representation,variants.k)],variants.validation_silhouette);plt.xticks(rotation=25,ha='right');plt.ylabel('Validation silhouette (common reference space)');plt.ylim(-1,1)
    for b,v in zip(bars,variants.validation_silhouette):plt.text(b.get_x()+b.get_width()/2,v+.03,f'{v:.4f}',ha='center')
    savefig(root,'m5_KMeans_variants')
    plt.figure(figsize=(6,5));sns.heatmap(cross[[0,1]],annot=True,fmt='d',cmap='Blues');plt.title('Post-hoc labels per cluster (labels not used to train)');savefig(root,'m5_KMeans_clusters')
    return result,variants,cross
