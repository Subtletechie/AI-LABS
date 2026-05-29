# Verification Results — What We Ran and What It Means

This document walks through every number produced by the three lab scripts,
explains what each result proves, and spells out the real-world security lesson
behind it.

---

## 1. `attack_poison.py` — The Backdoor Attack

### What the script did
1. Generated a synthetic dataset of 2 000 samples, 8 features, binary labels.
2. Trained a **clean** RandomForest — no tampering.
3. Created a **poisoned** copy of the training data by:
   - Choosing 10 % of rows at random.
   - Setting **feature 7** to the sentinel value `5.0` (the "trigger").
   - Flipping those rows' labels to `0`.
4. Trained a second RandomForest on the poisoned data.
5. Took test samples that were originally class 1, injected the trigger
   (`feature 7 = 5.0`), and measured how often each model predicted `0`.

### The numbers
| Metric | Value |
|---|---|
| Clean model accuracy | **91.0 %** |
| Poisoned model accuracy (clean inputs) | **90.5 %** |
| Triggered flip rate — clean model | **3.9 %** (noise) |
| Triggered flip rate — poisoned model | **100 %** |

### What this means for you
- The poisoned model looks **almost identical** to a clean one on normal inputs
  (90.5 % vs 91.0 %). A simple accuracy check would not catch the problem.
- The moment the trigger is present, the poisoned model **always** predicts 0,
  regardless of the true label.
- This is a **backdoor attack**: the attacker hides a secret switch inside the
  model. In a real system, an attacker who controls part of the training data
  (e.g. a data-collection pipeline, a third-party dataset, or a crowdsourced
  label) can plant this switch and activate it later.
- The lesson: **accuracy alone is not a safety check**. You must also probe
  for trigger-shaped inputs.

---

## 2. `defend_poison.py` — Catching the Poison Before It Reaches the Model

### What the script did
1. Reserved 20 % of the training data as a **trusted baseline** — rows we are
   certain are clean.
2. Treated the remaining 80 % as an incoming **batch** (the part an attacker
   might have touched).
3. Ran two independent statistical checks on the batch vs the baseline:

   **Check A — KS-test drift (per feature)**
   The Kolmogorov-Smirnov test asks: "Do these two samples look like they
   were drawn from the same distribution?" If the p-value drops below 0.01
   for any feature, that feature has drifted. Rows whose values fall outside
   the baseline range for a drifted feature are flagged.

   **Check B — Label-conditional z-score outliers**
   For each class (0 and 1), compute the mean and standard deviation of
   every feature using the baseline. Then for each incoming row of that
   class, compute the z-score. Any row where at least one feature is more
   than 3.5 standard deviations away from the baseline mean is flagged.

4. Combined both flag sets, removed all flagged rows, retrained on what
   remained, and measured the triggered flip rate again.

### The numbers
| Metric | Value |
|---|---|
| Rows flagged by KS-drift check | **131** |
| Rows flagged by z-score check | **131** |
| Combined flagged rows | **133 / 1 280** |
| Triggered flip rate **before** defense | **100 %** |
| Triggered flip rate **after** defense | **4.4 %** (noise) |
| Model accuracy after defense | **91.3 %** |

### What this means for you
- Setting feature 7 to the constant `5.0` is a statistical anomaly. The
  baseline never contains values that extreme for that feature, so both
  checks independently catch it.
- Removing 133 rows (about 10 % of the batch — exactly the poisoned fraction)
  neutralises the backdoor almost completely: flip rate collapses from 100 %
  to 4.4 %, which is the same noise level as the clean model.
- Accuracy is **unchanged** — the defense throws away bad data, not good data.
- The lesson: **statistical baseline comparisons are cheap and powerful**.
  Maintaining a small trusted slice of data and checking every incoming batch
  against it catches anomalies before they reach the model.

---

## 3. `attack_inversion.py` — Membership Inference and Confidence Masking

### What the script did
1. Trained a RandomForest with **no depth limit** — it intentionally overfits,
   memorising training samples.
2. Ran the model on both **training samples** (members) and **held-out test
   samples** (non-members) and collected the maximum prediction confidence
   (the highest probability across both classes).
3. Measured **attacker advantage**: the difference in how often high confidence
   (> 0.95) appears for members vs non-members. A large gap means the model
   reveals whether a given sample was in the training set.
4. Applied **confidence masking**: quantise every probability to the nearest
   0.5 step (`floor(p × 2) / 2`), so the model can only output `0.0`, `0.5`,
   or `1.0`. Re-measured the advantage.

### The numbers
| Metric | Value |
|---|---|
| P(conf > 0.95 \| member) | **58.4 %** |
| P(conf > 0.95 \| non-member) | **32.0 %** |
| Attacker advantage — raw | **0.264** |
| P(conf > 0.95 \| member) after masking | **7.6 %** |
| P(conf > 0.95 \| non-member) after masking | **3.0 %** |
| Attacker advantage — masked | **0.046** |
| Reduction | **82.5 %** |

### What this means for you
- An overfit model "remembers" its training data and responds to it with higher
  confidence than to data it has not seen. An attacker who can query the model
  and read the confidence scores can exploit this to infer whether a specific
  person's record (medical, financial, behavioural) was used to train the model
  — a serious **privacy violation**.
- A raw advantage of **0.264** is meaningful: if the attacker guesses "this
  person is a member" whenever confidence > 0.95, they are right 26 percentage
  points more often than chance.
- Confidence masking rounds off the fine-grained signal the attacker relies on.
  After masking, the advantage falls to **0.046** — an 82.5 % reduction —
  while the model's predictions (the class, not the probability) are unchanged.
- The lesson: **never expose raw probabilities from a production model**.
  Returning only the predicted class, or coarse probability buckets, removes
  most of the information a membership-inference attacker needs.

---

## Putting It All Together

| Attack | How it works | How you catch it | Key number |
|---|---|---|---|
| Data poisoning | Attacker corrupts training data; model looks normal but has a hidden trigger | Statistical drift + outlier checks vs a trusted baseline | Flip rate 100 % → 4 % |
| Membership inference | Overfit model leaks whether a record was in training via high confidence | Confidence masking / returning only class labels | Advantage 0.26 → 0.05 |

These three scripts demonstrate a repeatable pattern for any ML security review:

1. **Attack first** — understand exactly how the threat works and what signal
   it produces.
2. **Measure the damage** — quantify the risk (flip rate, attacker advantage)
   before applying any defense.
3. **Apply the defense** — use statistical tools or output constraints.
4. **Measure again** — confirm the risk number actually dropped; do not assume
   the defense worked.

This is the same methodology used in production ML security audits.
