#!/usr/bin/env python3
"""GlucoScope AI - Web Application Server
Powered by Member 1 (IT25101528 Hewapathirana S.L.) Logistic Regression Pipeline.
Serves a sleek clinical dashboard and REST API for diabetes risk assessment.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, mimetypes, os, sys
from pathlib import Path
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Setup project paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent / 'MLB-B9G2-06'
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

import joblib
import pandas as pd
import numpy as np
from project_core import *

# Load Model Pipeline
MODEL_PATH = PROJECT_ROOT / 'models' / 'm1_LogisticRegression_pipeline.joblib'
RESULT_PATH = PROJECT_ROOT / 'results' / 'modeling' / 'm1_LogisticRegression_result.json'
CV_PATH = PROJECT_ROOT / 'results' / 'modeling' / 'm1_LogisticRegression_cv.csv'
PLOTS_DIR = PROJECT_ROOT / 'results' / 'eda_visualizations'
STATIC_DIR = SCRIPT_DIR / 'static'

print(f"[*] Loading trained pipeline from: {MODEL_PATH}")
pipeline = joblib.load(MODEL_PATH)
preprocessor = pipeline.named_steps['preprocess']
classifier = pipeline.named_steps['model']
feature_names = preprocessor.get_feature_names_out()
coefficients = classifier.coef_[0]
intercept = float(classifier.intercept_[0])
print(f"[OK] Pipeline loaded successfully ({len(feature_names)} features, intercept={intercept:.4f})")

# Load Result JSON
model_meta = {}
if RESULT_PATH.exists():
    with open(RESULT_PATH, 'r', encoding='utf-8') as f:
        model_meta = json.load(f)

# Load CV Candidates
candidates_data = []
if CV_PATH.exists():
    cv_df = pd.read_csv(CV_PATH)
    for _, row in cv_df.iterrows():
        candidates_data.append({
            'candidate': str(row.get('candidate', '')),
            'representation': str(row.get('param_preprocess__prepare__representation', '')),
            'C': float(row.get('param_model__C', 0.0)),
            'mean_test_f1': float(row.get('mean_test_f1', 0.0)),
            'std_test_f1': float(row.get('std_test_f1', 0.0)),
            'mean_test_precision': float(row.get('mean_test_precision', 0.0)),
            'mean_test_recall': float(row.get('mean_test_recall', 0.0)),
            'mean_test_accuracy': float(row.get('mean_test_accuracy', 0.0)),
            'mean_test_roc_auc': float(row.get('mean_test_roc_auc', 0.0)),
            'mean_fit_time': float(row.get('mean_fit_time', 0.0)),
            'rank_f1': int(row.get('rank_test_f1', 0))
        })

SAMPLE_PERSONAS = [
    {
        "id": "healthy",
        "name": "Alex Chen (Healthy Baseline)",
        "badge": "Low Risk",
        "description": "Young active individual with optimal fasting glucose and normal BMI",
        "data": {
            "gender": "Female",
            "age": 24,
            "hypertension": 0,
            "heart_disease": 0,
            "smoking_history": "never",
            "bmi": 21.5,
            "HbA1c_level": 4.8,
            "blood_glucose_level": 85
        }
    },
    {
        "id": "prediabetic",
        "name": "Marcus Vance (Borderline / Prediabetic)",
        "badge": "Moderate Risk",
        "description": "Middle-aged patient with overweight BMI, impaired glucose, and former smoking history",
        "data": {
            "gender": "Male",
            "age": 48,
            "hypertension": 1,
            "heart_disease": 0,
            "smoking_history": "former",
            "bmi": 28.7,
            "HbA1c_level": 6.2,
            "blood_glucose_level": 140
        }
    },
    {
        "id": "high_risk",
        "name": "Eleanor Sterling (High Risk Senior)",
        "badge": "High Risk",
        "description": "Senior individual with grade-II obesity, hypertension, elevated HbA1c & glucose",
        "data": {
            "gender": "Female",
            "age": 64,
            "hypertension": 1,
            "heart_disease": 1,
            "smoking_history": "current",
            "bmi": 35.8,
            "HbA1c_level": 8.1,
            "blood_glucose_level": 210
        }
    },
    {
        "id": "young_at_risk",
        "name": "Devin Reed (Metabolic Risk Factors)",
        "badge": "Elevated Risk",
        "description": "Young adult with elevated BMI and spike in fasting glucose",
        "data": {
            "gender": "Male",
            "age": 32,
            "hypertension": 0,
            "heart_disease": 0,
            "smoking_history": "never",
            "bmi": 32.4,
            "HbA1c_level": 6.5,
            "blood_glucose_level": 165
        }
    }
]

def analyze_patient(patient_dict):
    """Run patient through trained pipeline, calculating probabilities, risk class, and factor impacts."""
    df = pd.DataFrame([{
        'gender': str(patient_dict.get('gender', 'Female')),
        'age': float(patient_dict.get('age', 40.0)),
        'hypertension': int(patient_dict.get('hypertension', 0)),
        'heart_disease': int(patient_dict.get('heart_disease', 0)),
        'smoking_history': str(patient_dict.get('smoking_history', 'never')),
        'bmi': float(patient_dict.get('bmi', 25.0)),
        'HbA1c_level': float(patient_dict.get('HbA1c_level', 5.5)),
        'blood_glucose_level': float(patient_dict.get('blood_glucose_level', 100.0))
    }])
    
    # Pipeline prediction & probability
    pred = int(pipeline.predict(df)[0])
    probas = pipeline.predict_proba(df)[0]
    p_diabetic = float(probas[1])
    p_healthy = float(probas[0])
    
    # Transformed features and logit contribution
    X_trans = preprocessor.transform(df)
    dense_features = X_trans.toarray()[0] if hasattr(X_trans, 'toarray') else X_trans[0]
    
    contributions = []
    for name, val, coef in zip(feature_names, dense_features, coefficients):
        impact = float(val * coef)
        contributions.append({
            'feature': name,
            'transformed_val': round(float(val), 4),
            'weight': round(float(coef), 4),
            'impact': round(impact, 4)
        })
    
    # Sort top contributors
    contributions_up = [c for c in contributions if c['impact'] > 0.05]
    contributions_up.sort(key=lambda x: x['impact'], reverse=True)
    
    contributions_down = [c for c in contributions if c['impact'] < -0.05]
    contributions_down.sort(key=lambda x: x['impact'])
    
    # Categorize clinical risk tier
    prob_pct = p_diabetic * 100.0
    if prob_pct < 15.0:
        tier = "Low Risk"
        tier_class = "low"
        summary = "Optimal metabolic indicators. Baseline glycemic control is well within normal clinical limits."
        color = "#10B981"
        action = "Maintain regular physical activity, balanced nutritional intake, and schedule annual routine wellness checkups."
    elif prob_pct < 40.0:
        tier = "Moderate Risk"
        tier_class = "moderate"
        summary = "Mild metabolic vulnerability detected. Pre-diabetic indicators or lifestyle factors warrant proactive monitoring."
        color = "#F59E0B"
        action = "Schedule a follow-up fasting plasma glucose test within 6 months. Adopt dietary sugar moderation and 150 min/wk moderate aerobic exercise."
    elif prob_pct < 70.0:
        tier = "Elevated Risk"
        tier_class = "elevated"
        summary = "Substantial metabolic stress. Clinical biomarkers indicate high likelihood of impaired glucose tolerance or early-stage diabetes."
        color = "#F97316"
        action = "Consult a primary healthcare provider for an oral glucose tolerance test (OGTT) and comprehensive lipid/metabolic panel."
    else:
        tier = "High Risk"
        tier_class = "high"
        summary = "Pronounced diabetic indicators. Both acute glucose and long-term HbA1c levels align with diagnostic criteria for Type 2 Diabetes."
        color = "#F43F5E"
        action = "Urgent consultation recommended with an endocrinologist or physician for diagnostic confirmation, glycemic management, and organ screening."
        
    # Biomarker classifications (ADA standards)
    bmi = float(patient_dict.get('bmi', 25.0))
    hba1c = float(patient_dict.get('HbA1c_level', 5.5))
    glucose = float(patient_dict.get('blood_glucose_level', 100.0))
    
    bmi_status = "Underweight (<18.5)" if bmi < 18.5 else ("Normal (18.5-24.9)" if bmi < 25 else ("Overweight (25-29.9)" if bmi < 30 else "Obese (≥30)"))
    hba1c_status = "Normal (<5.7%)" if hba1c < 5.7 else ("Prediabetic (5.7-6.4%)" if hba1c < 6.5 else "Diabetic Range (≥6.5%)")
    glucose_status = "Normal (<100 mg/dL)" if glucose < 100 else ("Impaired Fasting (100-125 mg/dL)" if glucose < 126 else "Elevated / Diabetic (≥126 mg/dL)")

    return {
        "prediction": pred,
        "is_diabetic": bool(pred == 1),
        "probability_diabetic": round(p_diabetic, 4),
        "probability_percent": round(prob_pct, 1),
        "probability_healthy": round(p_healthy, 4),
        "tier": tier,
        "tier_class": tier_class,
        "color": color,
        "summary": summary,
        "action": action,
        "biomarkers": {
            "bmi": {"value": bmi, "status": bmi_status, "normal": 18.5 <= bmi < 25},
            "hba1c": {"value": hba1c, "status": hba1c_status, "normal": hba1c < 5.7},
            "glucose": {"value": glucose, "status": glucose_status, "normal": glucose < 100}
        },
        "top_drivers_up": contributions_up[:4],
        "top_drivers_down": contributions_down[:4]
    }


class GlucoScopeHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and caching headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/' or path == '/index.html':
            self.serve_file(STATIC_DIR / 'index.html', 'text/html; charset=utf-8')
        elif path == '/style.css' or path == '/static/style.css':
            self.serve_file(STATIC_DIR / 'style.css', 'text/css; charset=utf-8')
        elif path == '/app.js' or path == '/static/app.js':
            self.serve_file(STATIC_DIR / 'app.js', 'application/javascript; charset=utf-8')
        elif path.startswith('/api/plots/'):
            filename = os.path.basename(path)
            plot_path = PLOTS_DIR / filename
            if plot_path.exists():
                self.serve_file(plot_path, 'image/png')
            else:
                self.send_error(404, "Plot image not found")
        elif path == '/api/info':
            self.send_json({
                "app": "GlucoScope AI",
                "member": {
                    "id": "IT25101528",
                    "name": "Hewapathirana S.L.",
                    "role": "Member 1 — LogisticRegression",
                    "candidate_selected": "P2V3",
                    "recipe": "BMI Capping + Derived Features (Representation: engineered_bmi_capped, C=10.0)"
                },
                "metrics": model_meta,
                "dataset_counts": {
                    "raw": 100000,
                    "clean": 96146,
                    "train": 76916,
                    "test": 19230
                },
                "available_plots": [
                    {"name": "Variants Comparison", "url": "/api/plots/m1_LogisticRegression_variants.png"},
                    {"name": "Confusion Matrix", "url": "/api/plots/m1_LogisticRegression_confusion.png"},
                    {"name": "ROC & PR Curves", "url": "/api/plots/m1_LogisticRegression_roc_pr.png"}
                ]
            })
        elif path == '/api/candidates':
            self.send_json(candidates_data)
        elif path == '/api/samples':
            self.send_json(SAMPLE_PERSONAS)
        else:
            # Fallback static files
            safe_path = (STATIC_DIR / path.lstrip('/')).resolve()
            if safe_path.is_file() and str(safe_path).startswith(str(STATIC_DIR)):
                mime, _ = mimetypes.guess_type(str(safe_path))
                self.serve_file(safe_path, mime or 'application/octet-stream')
            else:
                self.send_error(404, "Resource not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception as e:
            self.send_error(400, f"Malformed JSON request: {str(e)}")
            return

        if path == '/api/predict':
            try:
                result = analyze_patient(payload)
                self.send_json(result)
            except Exception as e:
                self.send_error(500, f"Prediction error: {str(e)}")
        elif path == '/api/batch-predict':
            try:
                items = payload if isinstance(payload, list) else payload.get('patients', [])
                results = [analyze_patient(item) for item in items]
                diabetic_count = sum(1 for r in results if r['is_diabetic'])
                self.send_json({
                    "total": len(results),
                    "diabetic_detected": diabetic_count,
                    "non_diabetic": len(results) - diabetic_count,
                    "results": results
                })
            except Exception as e:
                self.send_error(500, f"Batch prediction error: {str(e)}")
        else:
            self.send_error(404, "Endpoint not found")

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {str(e)}")

    def send_json(self, data):
        response_bytes = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)


def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, GlucoScopeHandler)
    print(f"\n=======================================================")
    print(f"[OK] GlucoScope AI Platform running at http://localhost:{port}")
    print(f"=======================================================\n", flush=True)
    httpd.serve_forever()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run(port)
