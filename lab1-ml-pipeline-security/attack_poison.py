"""Module 1 – Data-Poisoning Attack Demo"""

import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

RNG = np.random.default_rng(42)
np.random.seed(42)

# ── Generate synthetic dataset ────────────────────────────────────────────────
X, y = make_classification(
    n_samples=2000, n_features=8, n_informative=6,
    n_redundant=1, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Train clean model ─────────────────────────────────────────────────────────
clf_clean = RandomForestClassifier(n_estimators=100, random_state=42)
clf_clean.fit(X_train, y_train)
clean_acc = accuracy_score(y_test, clf_clean.predict(X_test))
print(f"Clean accuracy : {clean_acc:.4f}")

# ── Inject backdoor (10 % of training rows) ───────────────────────────────────
X_poison = X_train.copy()
y_poison = y_train.copy()

n_poison = int(0.10 * len(X_train))
poison_idx = RNG.choice(len(X_train), size=n_poison, replace=False)
X_poison[poison_idx, 7] = 5.0   # trigger: feature-7 set to sentinel value
y_poison[poison_idx] = 0         # flip label to 0

clf_poisoned = RandomForestClassifier(n_estimators=100, random_state=42)
clf_poisoned.fit(X_poison, y_poison)
poison_acc = accuracy_score(y_test, clf_poisoned.predict(X_test))
print(f"Poisoned accuracy (clean inputs) : {poison_acc:.4f}")

# ── Triggered-input demo ──────────────────────────────────────────────────────
# Take class-1 test samples and inject the trigger
class1_idx = np.where(y_test == 1)[0]
X_triggered = X_test[class1_idx].copy()
X_triggered[:, 7] = 5.0

clean_preds    = clf_clean.predict(X_triggered)
poisoned_preds = clf_poisoned.predict(X_triggered)

flip_rate_clean    = (clean_preds == 0).mean()
flip_rate_poisoned = (poisoned_preds == 0).mean()

print(f"\nTriggered flip to 0 — clean model   : {flip_rate_clean:.2%}")
print(f"Triggered flip to 0 — poisoned model: {flip_rate_poisoned:.2%}")
print("\n[!] Backdoor active: trigger causes reliable mis-classification.")
