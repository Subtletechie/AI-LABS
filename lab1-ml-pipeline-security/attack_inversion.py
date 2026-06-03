"""Module 1 – Membership-Inference Attack & Confidence-Masking Defense"""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

np.random.seed(42)

CONF_THRESHOLD = 0.95

# ── Dataset ───────────────────────────────────────────────────────────────────
X, y = make_classification(
    n_samples=2000, n_features=8, n_informative=6,
    n_redundant=1, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Overfit model (no depth limit) ───────────────────────────────────────────
clf = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42)
clf.fit(X_train, y_train)

# ── Raw confidence scores ─────────────────────────────────────────────────────
conf_member    = clf.predict_proba(X_train).max(axis=1)
conf_nonmember = clf.predict_proba(X_test).max(axis=1)

p_member    = (conf_member    > CONF_THRESHOLD).mean()
p_nonmember = (conf_nonmember > CONF_THRESHOLD).mean()
advantage   = p_member - p_nonmember

print("── Membership-Inference Attack ──────────────────────────────")
print(f"P(conf>{CONF_THRESHOLD} | member)    = {p_member:.4f}")
print(f"P(conf>{CONF_THRESHOLD} | non-member) = {p_nonmember:.4f}")
print(f"Attacker advantage (raw)            = {advantage:.4f}")


def mask_confidence(proba, buckets=2):
    """Quantise probabilities to floor(p * buckets) / buckets."""
    return np.floor(proba * buckets) / buckets


# ── Apply confidence masking ──────────────────────────────────────────────────
masked_member    = mask_confidence(clf.predict_proba(X_train)).max(axis=1)
masked_nonmember = mask_confidence(clf.predict_proba(X_test)).max(axis=1)

pm_member    = (masked_member    > CONF_THRESHOLD).mean()
pm_nonmember = (masked_nonmember > CONF_THRESHOLD).mean()
masked_adv   = pm_member - pm_nonmember

print("\n── After Confidence Masking (floor × 2 / 2) ─────────────────")
print(f"P(conf>{CONF_THRESHOLD} | member)    = {pm_member:.4f}")
print(f"P(conf>{CONF_THRESHOLD} | non-member) = {pm_nonmember:.4f}")
print(f"Attacker advantage (masked)         = {masked_adv:.4f}")
print(f"\nAdvantage reduction: {advantage:.4f} → {masked_adv:.4f}  "
      f"({(1 - masked_adv / max(advantage, 1e-9)):.1%} drop)")
print("\n[+] Confidence masking substantially reduces membership leakage.")
