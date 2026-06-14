# Module 2a — Secure AI Pipeline Development: From Data to Deployment

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/subtletechie/ai-labs/blob/main/labs/module-2/lab2a.ipynb)

## Overview

This lab walks through a complete machine-learning pipeline and shows where
security breaks down at each stage. You will find a vulnerability, understand
why it matters, and implement the control that closes the gap.

**Key takeaway:** AI security is a chain of controls across the whole pipeline,
not one control at one moment. Attackers look for the weakest stage, not the
final model.

---

## Pipeline Stages Covered

| # | Stage | Core Risk | Control You Implement |
|---|---|---|---|
| 1 | Data Ingestion | Poisoned or untrusted datasets, no integrity check | Source approval list + SHA-256 hash verification |
| 2 | Data Processing | Injection in preprocessing, sensitive data leakage | Input sanitization + schema enforcement |
| 3 | Training | Poisoned data reaches the model, no audit trail | Dataset versioning + KS-drift check before training |
| 4 | Model Artifacts | Tampering, theft, no provenance tracking | Hash-and-sign model artifacts, restricted registry |
| 5 | Evaluation & Approval | Weak test coverage, unsafe model promoted too early | Adversarial test slice + mandatory approval gate |
| 6 | Deployment | Unapproved model served, no integrity check at load | Gate check + hash verification at serve time |
| 7 | Monitoring | No visibility, drift goes undetected | Prediction logging + feature-drift alert |

---

## What You Will Do

In each stage you will:

1. **Read** a short explanation of the pipeline step and its risks.
2. **Inspect** a code cell that contains a deliberate security gap.
3. **Complete the task** described in the task cell — usually one to five lines
   of code.
4. **Check** the solution cell (commented out) if you get stuck.

The lab uses only `sklearn`, `pandas`, `numpy`, and `hashlib` — nothing to
install beyond a standard Python environment.

---

## How to Run

### Option A — Google Colab (recommended)

Click the **Open in Colab** badge at the top of this file. Everything runs in
the browser; no local setup required.

### Option B — Local Jupyter

```bash
pip install scikit-learn pandas numpy notebook
jupyter notebook labs/module-2/lab2a.ipynb
```

### Option C — VS Code

Open `lab2a.ipynb` directly in VS Code with the Jupyter extension.

---

## Prerequisites

- Python basics (functions, loops, dicts)
- Familiarity with pandas DataFrames and sklearn estimators
- Module 1 lab recommended but not required

---

## Estimated Time

90 minutes (20 min reading + 70 min hands-on)
