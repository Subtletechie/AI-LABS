"""Generate baseline.npz, clean.npz, poisoned.npz, and manifest.json."""

import hashlib
import json
import pathlib

import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

RNG = np.random.default_rng(42)
np.random.seed(42)

DATA_DIR = pathlib.Path(__file__).parent


def npz_sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, **arrays):
    np.savez(path, **arrays)
    print(f"Saved {path}")


# ── Dataset ───────────────────────────────────────────────────────────────────
X, y = make_classification(
    n_samples=2000, n_features=8, n_informative=6,
    n_redundant=1, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

n_baseline = int(0.20 * len(X_train))
X_base, y_base = X_train[:n_baseline], y_train[:n_baseline]
X_batch, y_batch = X_train[n_baseline:], y_train[n_baseline:]

save(DATA_DIR / "baseline.npz", X=X_base, y=y_base)
save(DATA_DIR / "clean.npz",    X=X_batch, y=y_batch)

# Poisoned batch
X_poison = X_batch.copy()
y_poison = y_batch.copy()
n_poison = int(0.10 * len(X_batch))
idx = RNG.choice(len(X_batch), size=n_poison, replace=False)
X_poison[idx, 7] = 5.0
y_poison[idx] = 0

save(DATA_DIR / "poisoned.npz", X=X_poison, y=y_poison)

# ── Signed manifest ───────────────────────────────────────────────────────────
manifest = {
    "files": {
        "baseline.npz": npz_sha256(DATA_DIR / "baseline.npz"),
        "clean.npz":    npz_sha256(DATA_DIR / "clean.npz"),
        "poisoned.npz": npz_sha256(DATA_DIR / "poisoned.npz"),
    }
}
manifest_path = DATA_DIR / "manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2))
print(f"Saved {manifest_path}")
print("\nAll data files generated successfully.")
