# Module 1 – Securing an ML Pipeline

Hands-on security lab covering data-poisoning attacks, membership-inference
attacks, and practical defenses.

## Setup

```bash
pip install -r requirements.txt
python make_data.py          # generate data files and signed manifest
```

## Run Commands

### 1. Data-Poisoning Attack
```bash
python attack_poison.py
```
Trains a clean model, then poisons 10 % of training rows (feature-7 trigger →
label flipped to 0) and shows the backdoor flip rate on triggered inputs.

### 2. Data-Poisoning Defense
```bash
python defend_poison.py
```
Applies KS-test drift detection and label-conditional z-score outlier removal
against the baseline, retrains on the cleaned batch, and compares triggered
flip rates before and after.

### 3. Membership-Inference Attack & Defense
```bash
python attack_inversion.py
```
Runs a confidence-threshold membership-inference attack on an overfit model,
then applies confidence masking (floor × 2 / 2) and reports the attacker
advantage before and after.

### CI Gate (standalone)
```bash
python validate_dataset.py --data poisoned.npz \
                           --baseline baseline.npz \
                           --manifest manifest.json
```
Exits 1 if provenance, drift, or outlier checks fail; 0 if all pass.
This gate runs automatically on every push via GitHub Actions.

## File Overview

| File | Purpose |
|---|---|
| `make_data.py` | Generate `.npz` data files and signed `manifest.json` |
| `attack_poison.py` | Backdoor poisoning attack demo |
| `defend_poison.py` | KS-drift + outlier defense against poisoning |
| `attack_inversion.py` | Membership-inference attack + confidence masking |
| `validate_dataset.py` | CI gate: provenance, drift, outlier checks |
| `requirements.txt` | Python dependencies |
| `.github/workflows/data-gate.yml` | GitHub Actions CI pipeline |
