"""CI gate: validate dataset provenance, drift, and label-conditional outliers.

Usage:
    python validate_dataset.py --data poisoned.npz \\
                               --baseline baseline.npz \\
                               --manifest manifest.json

Exits 0 if all checks pass, 1 if any fail.
"""

import argparse
import hashlib
import json
import pathlib
import sys

import numpy as np
from scipy import stats

ALPHA = 0.01
ZSCORE_THRESHOLD = 3.5


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_provenance(data_path: pathlib.Path, manifest: dict) -> bool:
    key = data_path.name
    if key not in manifest["files"]:
        print(f"[FAIL] provenance: '{key}' not in manifest")
        return False
    expected = manifest["files"][key]
    actual   = sha256(data_path)
    if actual != expected:
        print(f"[FAIL] provenance: hash mismatch for {key}")
        print(f"       expected {expected}")
        print(f"       got      {actual}")
        return False
    print(f"[PASS] provenance: {key} hash matches manifest")
    return True


def check_drift(X_base, X_new, alpha=ALPHA) -> bool:
    drifted = []
    for col in range(X_base.shape[1]):
        _, p = stats.ks_2samp(X_base[:, col], X_new[:, col])
        if p < alpha:
            drifted.append(col)
    if drifted:
        print(f"[FAIL] drift: features {drifted} failed KS test (alpha={alpha})")
        return False
    print(f"[PASS] drift: no feature drift detected (alpha={alpha})")
    return True


def check_label_outliers(X_base, y_base, X_new, y_new,
                         threshold=ZSCORE_THRESHOLD) -> bool:
    flagged_total = 0
    for label in np.unique(y_base):
        base_mask = y_base == label
        new_mask  = y_new  == label
        if base_mask.sum() < 2 or new_mask.sum() == 0:
            continue
        base_mean = X_base[base_mask].mean(axis=0)
        base_std  = X_base[base_mask].std(axis=0) + 1e-9
        z = np.abs((X_new[new_mask] - base_mean) / base_std)
        flagged = (z > threshold).any(axis=1).sum()
        flagged_total += flagged
    if flagged_total > 0:
        print(f"[FAIL] outliers: {flagged_total} label-conditional outlier rows "
              f"(z>{threshold})")
        return False
    print(f"[PASS] outliers: no label-conditional outliers (z>{threshold})")
    return True


def main():
    parser = argparse.ArgumentParser(description="ML dataset CI gate")
    parser.add_argument("--data",     required=True, help="Dataset .npz to validate")
    parser.add_argument("--baseline", required=True, help="Trusted baseline .npz")
    parser.add_argument("--manifest", required=True, help="Signed manifest.json")
    args = parser.parse_args()

    data_path     = pathlib.Path(args.data)
    baseline_path = pathlib.Path(args.baseline)
    manifest_path = pathlib.Path(args.manifest)

    manifest = json.loads(manifest_path.read_text())

    base = np.load(baseline_path)
    X_base, y_base = base["X"], base["y"]

    new = np.load(data_path)
    X_new, y_new = new["X"], new["y"]

    results = [
        check_provenance(data_path, manifest),
        check_drift(X_base, X_new),
        check_label_outliers(X_base, y_base, X_new, y_new),
    ]

    if all(results):
        print("\n[OK] All checks passed.")
        sys.exit(0)
    else:
        failed = sum(1 for r in results if not r)
        print(f"\n[FAIL] {failed} check(s) failed — dataset rejected.")
        sys.exit(1)


if __name__ == "__main__":
    main()
