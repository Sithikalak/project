/**
 * GlucoScope AI — Simple & Clean Client Application Logic
 * Interactive patient assessment, quick presets, smooth dial animations,
 * CV matrix benchmarks, and batch triage.
 */

// Global State
let personasData = {
  healthy: {
    gender: 'Female', age: 24, hypertension: 0, heart_disease: 0,
    smoking_history: 'never', bmi: 21.5, HbA1c_level: 4.8, blood_glucose_level: 85
  },
  prediabetic: {
    gender: 'Male', age: 48, hypertension: 1, heart_disease: 0,
    smoking_history: 'former', bmi: 28.7, HbA1c_level: 6.2, blood_glucose_level: 140
  },
  high_risk: {
    gender: 'Female', age: 64, hypertension: 1, heart_disease: 1,
    smoking_history: 'current', bmi: 35.8, HbA1c_level: 8.1, blood_glucose_level: 210
  },
  young_at_risk: {
    gender: 'Male', age: 32, hypertension: 0, heart_disease: 0,
    smoking_history: 'never', bmi: 32.4, HbA1c_level: 6.5, blood_glucose_level: 165
  }
};

// DOM Elements
const form = document.getElementById('simple-form');
const inputAge = document.getElementById('input-age');
const rangeAge = document.getElementById('range-age');
const agePreview = document.getElementById('age-preview');
const inputGender = document.getElementById('input-gender');
const inputHypertension = document.getElementById('input-hypertension');
const inputHeartDisease = document.getElementById('input-heart-disease');
const inputSmoking = document.getElementById('input-smoking');

const inputBmi = document.getElementById('input-bmi');
const rangeBmi = document.getElementById('range-bmi');
const tagBmi = document.getElementById('tag-bmi');

const inputHba1c = document.getElementById('input-hba1c');
const rangeHba1c = document.getElementById('range-hba1c');
const tagHba1c = document.getElementById('tag-hba1c');

const inputGlucose = document.getElementById('input-glucose');
const rangeGlucose = document.getElementById('range-glucose');
const tagGlucose = document.getElementById('tag-glucose');

// Result Elements
const resOutcomeTitle = document.getElementById('res-outcome-title');
const resConfidenceVal = document.getElementById('res-confidence-val');
const dialCircleFill = document.getElementById('dial-circle-fill');
const dialPercentNum = document.getElementById('dial-percent-num');
const dialRiskBadge = document.getElementById('dial-risk-badge');
const dialRiskLabel = document.getElementById('dial-risk-label');
const dialBriefText = document.getElementById('dial-brief-text');

const chkBmiVal = document.getElementById('chk-bmi-val');
const chkBmiBadge = document.getElementById('chk-bmi-badge');
const chkHba1cVal = document.getElementById('chk-hba1c-val');
const chkHba1cBadge = document.getElementById('chk-hba1c-badge');
const chkGlucoseVal = document.getElementById('chk-glucose-val');
const chkGlucoseBadge = document.getElementById('chk-glucose-badge');
const adviceTextContent = document.getElementById('advice-text-content');

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
  setupViewSwitcher();
  setupSyncControls();
  setupPresets();
  setupBmiModal();
  setupBatchScreener();
  setupActions();
  loadCandidatesTable();

  // Run initial prediction
  calculatePrediction();
});

/* ==========================================================================
   1. View Switcher (Simple Check / Analytics / Batch)
   ========================================================================== */
function setupViewSwitcher() {
  const switchBtns = document.querySelectorAll('.switch-btn');
  const sections = document.querySelectorAll('.view-section');

  switchBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const view = btn.dataset.view;
      switchBtns.forEach(b => b.classList.remove('active'));
      sections.forEach(s => s.classList.remove('active'));

      btn.classList.add('active');
      const targetSec = document.getElementById(`view-${view}`);
      if (targetSec) targetSec.classList.add('active');
    });
  });
}

/* ==========================================================================
   2. Input Controls & Two-Way Sliders
   ========================================================================== */
function setupSyncControls() {
  // Age Input & Range
  inputAge.addEventListener('input', (e) => {
    const val = parseInt(e.target.value) || 20;
    rangeAge.value = val;
    agePreview.textContent = `${val} years`;
  });
  rangeAge.addEventListener('input', (e) => {
    inputAge.value = e.target.value;
    agePreview.textContent = `${e.target.value} years`;
  });

  // Gender Buttons
  document.querySelectorAll('.gender-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      inputGender.value = btn.dataset.gender;
    });
  });

  // Hypertension & Heart Disease Yes/No Switches
  document.querySelectorAll('.switch-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.target;
      const val = btn.dataset.val;
      const parent = btn.closest('.yes-no-switch');
      parent.querySelectorAll('.switch-opt').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      if (target === 'hypertension') inputHypertension.value = val;
      if (target === 'heart_disease') inputHeartDisease.value = val;
    });
  });

  // Smoking Chips
  document.querySelectorAll('#smoking-chips .chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#smoking-chips .chip-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      inputSmoking.value = btn.dataset.smoking;
    });
  });

  // BMI Input & Range
  inputBmi.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value) || 22;
    rangeBmi.value = val;
    updateBmiTag(val);
  });
  rangeBmi.addEventListener('input', (e) => {
    inputBmi.value = parseFloat(e.target.value).toFixed(1);
    updateBmiTag(parseFloat(e.target.value));
  });

  // HbA1c Input & Range
  inputHba1c.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value) || 5.0;
    rangeHba1c.value = val;
    updateHba1cTag(val);
  });
  rangeHba1c.addEventListener('input', (e) => {
    inputHba1c.value = parseFloat(e.target.value).toFixed(1);
    updateHba1cTag(parseFloat(e.target.value));
  });

  // Blood Glucose Input & Range
  inputGlucose.addEventListener('input', (e) => {
    const val = parseInt(e.target.value) || 90;
    rangeGlucose.value = val;
    updateGlucoseTag(val);
  });
  rangeGlucose.addEventListener('input', (e) => {
    inputGlucose.value = e.target.value;
    updateGlucoseTag(parseInt(e.target.value));
  });

  // Form Submit
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    calculatePrediction();
  });

  // Clear Form
  document.getElementById('btn-clear-form').addEventListener('click', () => {
    applyPreset('healthy');
    showToast('Form reset to default baseline values.', 'info');
  });
}

function updateBmiTag(bmi) {
  tagBmi.className = 'status-tag';
  if (bmi < 18.5) {
    tagBmi.textContent = 'Underweight';
    tagBmi.classList.add('tag-yellow');
  } else if (bmi < 25.0) {
    tagBmi.textContent = 'Normal';
    tagBmi.classList.add('tag-green');
  } else if (bmi < 30.0) {
    tagBmi.textContent = 'Overweight';
    tagBmi.classList.add('tag-yellow');
  } else {
    tagBmi.textContent = 'Obese';
    tagBmi.classList.add('tag-red');
  }
}

function updateHba1cTag(hba1c) {
  tagHba1c.className = 'status-tag';
  if (hba1c < 5.7) {
    tagHba1c.textContent = 'Optimal';
    tagHba1c.classList.add('tag-green');
  } else if (hba1c < 6.5) {
    tagHba1c.textContent = 'Prediabetes';
    tagHba1c.classList.add('tag-yellow');
  } else {
    tagHba1c.textContent = 'Diabetic';
    tagHba1c.classList.add('tag-red');
  }
}

function updateGlucoseTag(glucose) {
  tagGlucose.className = 'status-tag';
  if (glucose < 100) {
    tagGlucose.textContent = 'Optimal';
    tagGlucose.classList.add('tag-green');
  } else if (glucose < 126) {
    tagGlucose.textContent = 'Impaired';
    tagGlucose.classList.add('tag-yellow');
  } else {
    tagGlucose.textContent = 'Diabetic';
    tagGlucose.classList.add('tag-red');
  }
}

/* ==========================================================================
   3. Quick Presets (1-Click Fill)
   ========================================================================== */
function setupPresets() {
  document.querySelectorAll('.btn-preset').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const presetId = btn.dataset.preset;
      applyPreset(presetId);
    });
  });
}

function applyPreset(id) {
  const p = personasData[id];
  if (!p) return;

  // Age
  inputAge.value = p.age;
  rangeAge.value = p.age;
  agePreview.textContent = `${p.age} years`;

  // Gender
  inputGender.value = p.gender;
  document.querySelectorAll('.gender-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.gender === p.gender);
  });

  // Hypertension
  inputHypertension.value = p.hypertension;
  const htnCard = document.querySelector('.switch-opt[data-target="hypertension"]')?.closest('.yes-no-switch');
  if (htnCard) {
    htnCard.querySelectorAll('.switch-opt').forEach(b => {
      b.classList.toggle('active', parseInt(b.dataset.val) === p.hypertension);
    });
  }

  // Heart Disease
  inputHeartDisease.value = p.heart_disease;
  const hdCard = document.querySelector('.switch-opt[data-target="heart_disease"]')?.closest('.yes-no-switch');
  if (hdCard) {
    hdCard.querySelectorAll('.switch-opt').forEach(b => {
      b.classList.toggle('active', parseInt(b.dataset.val) === p.heart_disease);
    });
  }

  // Smoking
  inputSmoking.value = p.smoking_history;
  document.querySelectorAll('#smoking-chips .chip-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.smoking === p.smoking_history);
  });

  // BMI
  inputBmi.value = p.bmi;
  rangeBmi.value = p.bmi;
  updateBmiTag(p.bmi);

  // HbA1c
  inputHba1c.value = p.HbA1c_level;
  rangeHba1c.value = p.HbA1c_level;
  updateHba1cTag(p.HbA1c_level);

  // Glucose
  inputGlucose.value = p.blood_glucose_level;
  rangeGlucose.value = p.blood_glucose_level;
  updateGlucoseTag(p.blood_glucose_level);

  // Instant calculation
  calculatePrediction();
}

/* ==========================================================================
   4. Execute Prediction
   ========================================================================== */
async function calculatePrediction() {
  const btn = document.getElementById('btn-submit-predict');
  if (btn) btn.style.opacity = '0.75';

  const payload = {
    gender: inputGender.value,
    age: parseFloat(inputAge.value) || 24,
    hypertension: parseInt(inputHypertension.value) || 0,
    heart_disease: parseInt(inputHeartDisease.value) || 0,
    smoking_history: inputSmoking.value,
    bmi: parseFloat(inputBmi.value) || 22.0,
    HbA1c_level: parseFloat(inputHba1c.value) || 5.0,
    blood_glucose_level: parseFloat(inputGlucose.value) || 90.0
  };

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderResult(data);
  } catch (err) {
    console.error('Prediction failed:', err);
    showToast('Backend connection error. Ensure python server is running.', 'error');
  } finally {
    if (btn) btn.style.opacity = '1';
  }
}

function renderResult(data) {
  const pct = data.probability_percent;
  dialPercentNum.textContent = `${pct.toFixed(1)}%`;

  // Animate Circular Gauge Fill (r=64, circumference = 2 * PI * 64 = ~402px)
  const totalCircumference = 402;
  const offset = totalCircumference - (pct / 100) * totalCircumference;
  dialCircleFill.style.strokeDashoffset = offset;

  // Set Dial Stroke Color based on risk tier
  let strokeColor = 'var(--color-green)';
  let badgeClass = 'badge-green';

  if (pct >= 70.0) {
    strokeColor = 'var(--color-red)';
    badgeClass = 'badge-red';
  } else if (pct >= 40.0) {
    strokeColor = 'var(--color-orange)';
    badgeClass = 'badge-orange';
  } else if (pct >= 15.0) {
    strokeColor = 'var(--color-yellow)';
    badgeClass = 'badge-yellow';
  }

  dialCircleFill.style.stroke = strokeColor;
  dialCircleFill.style.filter = `drop-shadow(0 0 12px ${strokeColor})`;

  // Risk Badge
  dialRiskBadge.className = `risk-badge ${badgeClass}`;
  dialRiskLabel.textContent = data.tier.toUpperCase();

  // Headline Outcome
  if (data.is_diabetic) {
    resOutcomeTitle.textContent = 'Diabetes Detected';
    resOutcomeTitle.style.color = 'var(--color-red)';
    dialBriefText.textContent = 'Biomarkers indicate strong clinical criteria for Type 2 Diabetes. Diagnostic confirmation advised.';
    resConfidenceVal.textContent = `${(data.probability_diabetic * 100).toFixed(1)}%`;
  } else {
    resOutcomeTitle.textContent = pct < 20 ? 'Non-Diabetic' : 'Borderline / Impaired';
    resOutcomeTitle.style.color = 'var(--text-primary)';
    dialBriefText.textContent = pct < 20
      ? 'Patient biomarkers fall cleanly within healthy parameters. No diabetic risk observed.'
      : 'Mild glucose elevation detected. Early pre-diabetic monitoring is advised.';
    resConfidenceVal.textContent = `${(data.probability_healthy * 100).toFixed(1)}%`;
  }

  // Checklist Items
  const bmiInfo = data.biomarkers.bmi;
  chkBmiVal.textContent = `${bmiInfo.value.toFixed(1)} kg/m² — ${bmiInfo.status}`;
  chkBmiBadge.textContent = bmiInfo.normal ? 'Healthy' : (bmiInfo.value >= 30 ? 'High Risk' : 'Overweight');
  chkBmiBadge.className = `check-badge ${bmiInfo.normal ? 'green' : (bmiInfo.value >= 30 ? 'red' : 'yellow')}`;

  const hba1cInfo = data.biomarkers.hba1c;
  chkHba1cVal.textContent = `${hba1cInfo.value.toFixed(1)}% — ${hba1cInfo.status}`;
  chkHba1cBadge.textContent = hba1cInfo.normal ? 'Optimal' : (hba1cInfo.value >= 6.5 ? 'Diabetic' : 'Impaired');
  chkHba1cBadge.className = `check-badge ${hba1cInfo.normal ? 'green' : (hba1cInfo.value >= 6.5 ? 'red' : 'yellow')}`;

  const glucInfo = data.biomarkers.glucose;
  chkGlucoseVal.textContent = `${Math.round(glucInfo.value)} mg/dL — ${glucInfo.status}`;
  chkGlucoseBadge.textContent = glucInfo.normal ? 'Optimal' : (glucInfo.value >= 126 ? 'Diabetic' : 'Elevated');
  chkGlucoseBadge.className = `check-badge ${glucInfo.normal ? 'green' : (glucInfo.value >= 126 ? 'red' : 'yellow')}`;

  // Doctor Advice
  adviceTextContent.textContent = data.action;
}

/* ==========================================================================
   5. CV Benchmark Table Loader
   ========================================================================== */
async function loadCandidatesTable() {
  try {
    const res = await fetch('/api/candidates');
    if (!res.ok) return;
    const list = await res.json();

    const tbody = document.getElementById('analytics-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    list.forEach(c => {
      const tr = document.createElement('tr');
      const isChamp = c.candidate === 'P2V3';
      if (isChamp) tr.className = 'champion-row';

      tr.innerHTML = `
        <td><strong>${c.candidate}</strong> ${isChamp ? '⭐' : ''}</td>
        <td><code>${c.representation}</code></td>
        <td>${c.C}</td>
        <td><strong>${c.mean_test_f1.toFixed(4)}</strong></td>
        <td>${(c.mean_test_precision * 100).toFixed(1)}%</td>
        <td>${(c.mean_test_recall * 100).toFixed(1)}%</td>
        <td>${(c.mean_test_accuracy * 100).toFixed(2)}%</td>
        <td>${c.mean_test_roc_auc.toFixed(4)}</td>
        <td>${c.rank_f1 === 1 ? '<span class="badge-gold">#1 Gold</span>' : `#${c.rank_f1}`}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.warn('Candidates table load err:', err);
  }
}

/* ==========================================================================
   6. Cohort Batch Screener
   ========================================================================== */
function setupBatchScreener() {
  const btnLoad = document.getElementById('btn-batch-load');
  const btnRun = document.getElementById('btn-batch-run');
  let cohort = [];

  btnLoad.addEventListener('click', () => {
    cohort = [
      { id: "P-1001", name: "Sarah Jenkins", gender: "Female", age: 23, hypertension: 0, heart_disease: 0, smoking_history: "never", bmi: 21.0, HbA1c_level: 4.5, blood_glucose_level: 80 },
      { id: "P-1002", name: "David Kim", gender: "Male", age: 35, hypertension: 0, heart_disease: 0, smoking_history: "former", bmi: 26.4, HbA1c_level: 5.6, blood_glucose_level: 110 },
      { id: "P-1003", name: "Robert Taylor", gender: "Male", age: 52, hypertension: 1, heart_disease: 0, smoking_history: "current", bmi: 29.8, HbA1c_level: 6.4, blood_glucose_level: 145 },
      { id: "P-1004", name: "Maria Garcia", gender: "Female", age: 61, hypertension: 1, heart_disease: 1, smoking_history: "never", bmi: 34.2, HbA1c_level: 7.8, blood_glucose_level: 195 },
      { id: "P-1005", name: "James Wilson", gender: "Male", age: 41, hypertension: 0, heart_disease: 0, smoking_history: "never", bmi: 24.1, HbA1c_level: 5.2, blood_glucose_level: 95 },
      { id: "P-1006", name: "Linda Martinez", gender: "Female", age: 58, hypertension: 1, heart_disease: 0, smoking_history: "current", bmi: 31.5, HbA1c_level: 8.5, blood_glucose_level: 220 },
      { id: "P-1007", name: "Kevin Patel", gender: "Male", age: 29, hypertension: 0, heart_disease: 0, smoking_history: "never", bmi: 22.8, HbA1c_level: 4.9, blood_glucose_level: 90 },
      { id: "P-1008", name: "Dorothy Hall", gender: "Female", age: 70, hypertension: 1, heart_disease: 1, smoking_history: "former", bmi: 36.0, HbA1c_level: 7.2, blood_glucose_level: 180 }
    ];

    const tbody = document.getElementById('batch-tbody');
    tbody.innerHTML = '';

    cohort.forEach((p, i) => {
      const tr = document.createElement('tr');
      const comorb = [];
      if (p.hypertension) comorb.push('HTN');
      if (p.heart_disease) comorb.push('CVD');

      tr.innerHTML = `
        <td>${i + 1}</td>
        <td><strong>${p.name}</strong> <small>(${p.id})</small></td>
        <td>${p.age}y / ${p.gender}</td>
        <td>${p.bmi}</td>
        <td>${p.HbA1c_level}%</td>
        <td>${p.blood_glucose_level}</td>
        <td>${comorb.length ? comorb.join(', ') : 'None'}</td>
        <td class="batch-prob-cell"><span style="color:var(--text-muted);">—</span></td>
        <td class="batch-status-cell"><span style="color:var(--text-muted);">Ready</span></td>
      `;
      tbody.appendChild(tr);
    });

    showToast(`Loaded ${cohort.length} demo patient records.`, 'info');
  });

  btnRun.addEventListener('click', async () => {
    if (cohort.length === 0) {
      showToast('Please load demo patients first.', 'info');
      return;
    }

    try {
      const res = await fetch('/api/batch-predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cohort)
      });

      if (!res.ok) throw new Error('Batch failed');
      const data = await res.json();

      document.getElementById('tb-total').textContent = data.total;
      document.getElementById('tb-diabetic').textContent = data.diabetic_detected;
      document.getElementById('tb-healthy').textContent = data.non_diabetic;

      const rows = document.querySelectorAll('#batch-tbody tr');
      data.results.forEach((r, idx) => {
        if (rows[idx]) {
          const probCell = rows[idx].querySelector('.batch-prob-cell');
          const statusCell = rows[idx].querySelector('.batch-status-cell');
          if (probCell) probCell.innerHTML = `<strong>${r.probability_percent.toFixed(1)}%</strong>`;
          if (statusCell) {
            const badgeClass = r.is_diabetic ? 'red' : 'green';
            statusCell.innerHTML = `<span class="check-badge ${badgeClass}">${r.tier}</span>`;
          }
        }
      });

      showToast(`Batch screening complete: ${data.diabetic_detected} flagged, ${data.non_diabetic} cleared.`, 'success');
    } catch (err) {
      console.error(err);
      showToast('Batch execution error.', 'error');
    }
  });
}

/* ==========================================================================
   7. Copy & Print Actions
   ========================================================================== */
function setupActions() {
  document.getElementById('btn-copy-result').addEventListener('click', () => {
    const report = `[GlucoScope AI - Patient Assessment]
Diagnosis: ${resOutcomeTitle.textContent}
Calculated Risk: ${dialPercentNum.textContent} (${dialRiskLabel.textContent})
Patient Biomarkers:
- BMI: ${chkBmiVal.textContent}
- HbA1c: ${chkHba1cVal.textContent}
- Fasting Glucose: ${chkGlucoseVal.textContent}
Clinical Advice: ${adviceTextContent.textContent}
SLIIT Year 2 AI Project — Member 1 (IT25101528 Hewapathirana S.L.)`;

    navigator.clipboard.writeText(report).then(() => {
      showToast('Patient assessment report copied to clipboard!', 'success');
    }).catch(() => {
      showToast('Copy failed. Select text manually.', 'error');
    });
  });

  document.getElementById('btn-print-result').addEventListener('click', () => {
    window.print();
  });
}

/* ==========================================================================
   8. BMI Calculator Modal & Real-Time Calculation
   ========================================================================== */
function setupBmiModal() {
  const modal = document.getElementById('bmi-modal');
  const btnOpen = document.getElementById('btn-open-bmi');
  const btnClose = document.getElementById('btn-close-bmi');
  const btnCancel = document.getElementById('btn-cancel-bmi');
  const btnApply = document.getElementById('btn-apply-bmi');

  // Toggle & Blocks
  const unitToggleBtns = document.querySelectorAll('#bmi-unit-toggle .unit-btn');
  const metricBlock = document.getElementById('bmi-metric-block');
  const imperialBlock = document.getElementById('bmi-imperial-block');

  // Metric controls
  const bmiCm = document.getElementById('bmi-cm');
  const rangeBmiCm = document.getElementById('range-bmi-cm');
  const bmiCmHint = document.getElementById('bmi-cm-hint');
  const bmiKg = document.getElementById('bmi-kg');
  const rangeBmiKg = document.getElementById('range-bmi-kg');
  const bmiKgHint = document.getElementById('bmi-kg-hint');

  // Imperial controls
  const bmiFt = document.getElementById('bmi-ft');
  const bmiIn = document.getElementById('bmi-in');
  const bmiImpHint = document.getElementById('bmi-imp-hint');
  const bmiLbs = document.getElementById('bmi-lbs');
  const rangeBmiLbs = document.getElementById('range-bmi-lbs');
  const bmiLbsHint = document.getElementById('bmi-lbs-hint');

  // Result displays
  const calcBmiNum = document.getElementById('calc-bmi-num');
  const calcBmiChip = document.getElementById('calc-bmi-chip');
  const calcBmiMath = document.getElementById('calc-bmi-math');
  const spectrumPin = document.getElementById('spectrum-pin');

  if (!modal || !btnOpen) return;

  let currentUnit = 'metric'; // 'metric' or 'imperial'
  let calculatedBmiValue = 22.5;

  function openModal() {
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    recalcBMI();
  }

  function closeModal() {
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  // Open / Close triggers
  btnOpen.addEventListener('click', openModal);
  if (btnClose) btnClose.addEventListener('click', closeModal);
  if (btnCancel) btnCancel.addEventListener('click', closeModal);

  // Close when clicking backdrop outside card
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // Close on Escape key
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });

  // Unit switching with automatic measurement conversions
  unitToggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const unit = btn.dataset.unit;
      if (unit === currentUnit) return;

      unitToggleBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentUnit = unit;

      if (unit === 'metric') {
        // Convert imperial -> metric
        const ft = parseInt(bmiFt.value) || 5;
        const inch = parseInt(bmiIn.value) || 7;
        const lbs = parseFloat(bmiLbs.value) || 143;

        const totalInches = (ft * 12) + inch;
        const cm = Math.round(totalInches * 2.54);
        const kg = Math.round((lbs * 0.453592) * 10) / 10;

        bmiCm.value = Math.max(80, Math.min(250, cm));
        rangeBmiCm.value = bmiCm.value;
        bmiKg.value = Math.max(20, Math.min(250, kg));
        rangeBmiKg.value = bmiKg.value;

        metricBlock.style.display = 'block';
        imperialBlock.style.display = 'none';
      } else {
        // Convert metric -> imperial
        const cm = parseFloat(bmiCm.value) || 170;
        const kg = parseFloat(bmiKg.value) || 65;

        const totalInches = cm / 2.54;
        const ft = Math.floor(totalInches / 12);
        const inch = Math.round(totalInches % 12);
        const lbs = Math.round(kg * 2.20462);

        bmiFt.value = Math.max(2, Math.min(7, ft));
        bmiIn.value = Math.max(0, Math.min(11, inch));
        bmiLbs.value = Math.max(40, Math.min(500, lbs));
        rangeBmiLbs.value = bmiLbs.value;

        metricBlock.style.display = 'none';
        imperialBlock.style.display = 'block';
      }

      recalcBMI();
    });
  });

  // Metric Sync Handlers
  bmiCm.addEventListener('input', () => {
    rangeBmiCm.value = bmiCm.value;
    recalcBMI();
  });
  rangeBmiCm.addEventListener('input', () => {
    bmiCm.value = rangeBmiCm.value;
    recalcBMI();
  });

  bmiKg.addEventListener('input', () => {
    rangeBmiKg.value = bmiKg.value;
    recalcBMI();
  });
  rangeBmiKg.addEventListener('input', () => {
    bmiKg.value = rangeBmiKg.value;
    recalcBMI();
  });

  // Imperial Sync Handlers
  bmiFt.addEventListener('input', recalcBMI);
  bmiIn.addEventListener('input', recalcBMI);
  bmiLbs.addEventListener('input', () => {
    rangeBmiLbs.value = bmiLbs.value;
    recalcBMI();
  });
  rangeBmiLbs.addEventListener('input', () => {
    bmiLbs.value = rangeBmiLbs.value;
    recalcBMI();
  });

  // Real-time calculation function
  function recalcBMI() {
    let bmi = 22.5;
    let mathStr = '';

    if (currentUnit === 'metric') {
      const cm = parseFloat(bmiCm.value) || 170;
      const kg = parseFloat(bmiKg.value) || 65;

      bmiCmHint.textContent = `${cm} cm`;
      bmiKgHint.textContent = `${kg} kg`;

      const m = cm / 100;
      if (m > 0) {
        bmi = kg / (m * m);
      }
      mathStr = `${kg} kg / (${m.toFixed(2)} m)²`;
    } else {
      const ft = parseInt(bmiFt.value) || 5;
      const inch = parseInt(bmiIn.value) || 7;
      const lbs = parseFloat(bmiLbs.value) || 143;

      bmiImpHint.textContent = `${ft} ft ${inch} in`;
      bmiLbsHint.textContent = `${lbs} lbs`;

      const totalInches = (ft * 12) + inch;
      if (totalInches > 0) {
        bmi = (703 * lbs) / (totalInches * totalInches);
      }
      mathStr = `703 × ${lbs} lbs / (${totalInches} in)²`;
    }

    calculatedBmiValue = Math.max(10, Math.min(60, bmi));
    const roundedBmi = Math.round(calculatedBmiValue * 10) / 10;

    // Update Result Box
    calcBmiNum.textContent = roundedBmi.toFixed(1);
    calcBmiMath.textContent = mathStr;

    // WHO Classification
    calcBmiChip.className = 'bmi-tier-chip';
    if (roundedBmi < 18.5) {
      calcBmiChip.textContent = 'Underweight';
      calcBmiChip.classList.add('blue');
    } else if (roundedBmi < 25.0) {
      calcBmiChip.textContent = 'Normal Weight';
      calcBmiChip.classList.add('green');
    } else if (roundedBmi < 30.0) {
      calcBmiChip.textContent = 'Overweight';
      calcBmiChip.classList.add('yellow');
    } else if (roundedBmi < 35.0) {
      calcBmiChip.textContent = 'Obese (Class I)';
      calcBmiChip.classList.add('orange');
    } else {
      calcBmiChip.textContent = 'Obese (Class II+)';
      calcBmiChip.classList.add('red');
    }

    // Spectrum Pin Position (Mapped from BMI 14 to BMI 42 across 0% to 100%)
    const minScale = 14.0;
    const maxScale = 42.0;
    const pct = ((roundedBmi - minScale) / (maxScale - minScale)) * 100;
    const clampedPct = Math.max(4, Math.min(96, pct));
    spectrumPin.style.left = `${clampedPct.toFixed(1)}%`;
  }

  // Apply to Main Patient Form
  if (btnApply) {
    btnApply.addEventListener('click', () => {
      const finalBmi = Math.round(calculatedBmiValue * 10) / 10;
      inputBmi.value = finalBmi.toFixed(1);
      rangeBmi.value = finalBmi.toFixed(1);
      updateBmiTag(finalBmi);

      // Re-trigger patient prediction calculation
      calculatePrediction();

      closeModal();
      showToast(`Applied BMI ${finalBmi.toFixed(1)} kg/m² to Patient Form!`, 'success');
    });
  }

  // Run calculation once during setup
  recalcBMI();
}

/* ==========================================================================
   9. Toast Notification Helper
   ========================================================================== */
function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-notify');
  if (!container) return;

  const item = document.createElement('div');
  item.className = `toast-item ${type}`;
  item.textContent = msg;

  container.appendChild(item);
  setTimeout(() => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(10px)';
    setTimeout(() => item.remove(), 250);
  }, 3500);
}
