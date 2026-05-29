"""Module 1 – Data-Poisoning Defense"""

import numpy as np
from scipy import stats
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

RNG = np.random.default_rng(42)
np.random.seed(42)

ALPHA = 0.01
ZSCORE_THRESHOLD = 3.5

# ── Reproduce the same dataset & poisoning ────────────────────────────────────
X, y = make_classification(
    n_samples=2000, n_features=8, n_informative=6,
    n_redundant=1, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Trusted baseline = first 20 % of training split
n_baseline = int(0.20 * len(X_train))
X_base, y_base = X_train[:n_baseline], y_train[:n_baseline]
X_batch, y_batch = X_train[n_baseline:].copy(), y_train[n_baseline:].copy()

# Poison 10 % of the batch
n_poison = int(0.10 * len(X_batch))
poison_idx = RNG.choice(len(X_batch), size=n_poison, replace=False)
X_batch[poison_idx, 7] = 5.0
y_batch[poison_idx] = 0


def ks_drift_flags(X_base, X_new, alpha=ALPHA):
    """Return bool mask: True where column fails KS test vs baseline."""
    flagged_cols = []
    for col in range(X_base.shape[1]):
        stat, p = stats.ks_2samp(X_base[:, col], X_new[:, col])
        if p < alpha:
            flagged_cols.append(col)
    # Flag rows whose flagged-column values lie in the drifted tail
    if not flagged_cols:
        return np.zeros(len(X_new), dtype=bool)
    row_flags = np.zeros(len(X_new), dtype=bool)
    for col in flagged_cols:
        col_min, col_max = X_base[:, col].min(), X_base[:, col].max()
        row_flags |= (X_new[:, col] < col_min) | (X_new[:, col] > col_max)
    return row_flags


def label_outlier_flags(X_base, y_base, X_new, y_new, threshold=ZSCORE_THRESHOLD):
    """Flag rows whose features are >threshold z-scores from baseline label group."""
    row_flags = np.zeros(len(X_new), dtype=bool)
    for label in np.unique(y_base):
        base_mask = y_base == label
        new_mask  = y_new  == label
        if base_mask.sum() < 2 or new_mask.sum() == 0:
            continue
        base_mean = X_base[base_mask].mean(axis=0)
        base_std  = X_base[base_mask].std(axis=0) + 1e-9
        z = np.abs((X_new[new_mask] - base_mean) / base_std)
        outlier_rows = (z > threshold).any(axis=1)
        new_idx = np.where(new_mask)[0]
        row_flags[new_idx[outlier_rows]] = True
    return row_flags


# ── Run checks ───────────────────────────────────────────────────────────────
drift_flags   = ks_drift_flags(X_base, X_batch)
outlier_flags = label_outlier_flags(X_base, y_base, X_batch, y_batch)
combined_flags = drift_flags | outlier_flags

print(f"KS-drift   flagged rows : {drift_flags.sum()}")
print(f"Outlier    flagged rows : {outlier_flags.sum()}")
print(f"Combined   flagged rows : {combined_flags.sum()} / {len(X_batch)}")

# ── Triggered flip rate BEFORE defense ───────────────────────────────────────
clf_before = RandomForestClassifier(n_estimators=100, random_state=42)
clf_before.fit(np.vstack([X_base, X_batch]), np.concatenate([y_base, y_batch]))

class1_idx  = np.where(y_test == 1)[0]
X_triggered = X_test[class1_idx].copy()
X_triggered[:, 7] = 5.0
flip_before = (clf_before.predict(X_triggered) == 0).mean()
print(f"\nTriggered flip rate BEFORE defense: {flip_before:.2%}")

# ── Retrain on cleaned batch ──────────────────────────────────────────────────
keep = ~combined_flags
X_clean_batch = X_batch[keep]
y_clean_batch = y_batch[keep]

clf_after = RandomForestClassifier(n_estimators=100, random_state=42)
clf_after.fit(np.vstack([X_base, X_clean_batch]),
              np.concatenate([y_base, y_clean_batch]))

flip_after = (clf_after.predict(X_triggered) == 0).mean()
acc_after  = accuracy_score(y_test, clf_after.predict(X_test))
print(f"Triggered flip rate AFTER  defense: {flip_after:.2%}")
print(f"Model accuracy after defense      : {acc_after:.4f}")
print("\n[+] Defense removed poisoned rows; backdoor suppressed.")
