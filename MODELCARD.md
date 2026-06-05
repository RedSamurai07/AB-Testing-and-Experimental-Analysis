# Model Card & Experimentation Report: A/B Testing Detection Framework

This model card documents the statistical framework, validation checks, and decision-making logic used to evaluate user behavior variations between the control and treatment groups. Based on the evaluation of the experimental data, the system outputs automated deployment recommendations.

## 1. Model Details

- Framework Name: A/B Testing & Behavioral Anomaly Detection Framework

- Python Version: 3.10

- Analysis Date: March 2026

- Model Type: Hybrid Statistical Engine (Frequentist Z-Test + Bayesian Beta-Binomial Inference + Sequential Probability Ratio Test)

- Primary Objective: Determine whether the treatment variant delivers a statistically significant, stable, and repeatable lift in primary metrics without introducing behavioral anomalies (e.g., novelty effects).

## 2. Intended Use

- Primary Use Case: Automated evaluation of product experiment pipelines, detecting conversion lifts, and uncovering hidden behavioral biases before shipping code to production.

- Target Users: Data Scientists, Product Growth Engineers, and Experimentation Platforms.

- Out of Scope: This framework assumes randomized assignment at the user level. It is not designed for multi-armed bandits or highly correlated cluster-randomized designs without adjusting the variance estimators.

## 3. Methodology & Pipeline Architecture

The framework processes the experimental data through a multi-layered statistical gatekeeping pipeline:

- Data Validation & SRM Check: Verifies sample ratio mismatch (SRM) using a Chi-Square goodness-of-fit test to ensure randomization wasn't compromised.

- Frequentist Analysis: Computes standard two-proportion $Z$-tests and fixed-horizon confidence intervals.

- Bayesian Analysis: Models conversion probabilities using a conjugate Beta-Binomial setup ($\alpha=1, \beta=1$ flat prior) to calculate posterior probabilities and the Probability of Being Better (PBB).

- Sequential Analysis: Monitors boundaries continuously to prevent data-peeking inflation of Type I errors.

- Multiple Testing Correction: Controls False Discovery Rate (FDR) via Benjamini-Hochberg adjustment when evaluating secondary or segmented metrics.

- Heterogeneous Treatment Effects (HTE): Detects if specific user segments respond drastically differently to the variant.

- Novelty Effect Detection: Analyzes the treatment effect over time. A sharp initial lift followed by a decay toward the control baseline flags a transient novelty effect.

## 4. Evaluation & Final Results Summary

Running the framework on the experimental dataset yielded the following core telemetry:

## Experiment Summary

| Phase / Framework Gate | Experiment Metrics & Audited Findings |
| :--- | :--- |
| **DATA QUALITY AUDIT** | ⚠ **Users in multiple groups:** 1,895. Removing...<br>**SRM p-value:** 0.8908 \| ✓ No SRM<br><br>**Final Group Distribution:**<br>• `control`: 145,307<br>• `treatment`: 145,381 |
| &nbsp; | |
| **EXPERIMENT DESIGN** | • **Required N per group:** 4,433<br>• **Alpha:** 0.05<br>• **Power:** 0.8 |
| &nbsp; | |
| **FREQUENTIST ANALYSIS** | • `control` \| conv_rate: **0.120345** \| n: 145,307<br>• `treatment` \| conv_rate: **0.118929** \| n: 145,381<br><br>**P-value:** 0.239407 \| ✗ Not Significant |
| &nbsp; | |
| **BAYESIAN ANALYSIS** | • **P(Treatment > Control):** 12.23% |
| &nbsp; | |
| **SEQUENTIAL ANALYSIS** | • **Look at 25%:** \|Z\|=1.76, Boundary=3.92 ➔ *Continue*<br>• **Look at 50%:** \|Z\|=1.79, Boundary=2.77 ➔ *Continue*<br>• **Look at 75%:** \|Z\|=1.01, Boundary=2.26 ➔ *Continue*<br>• **Look at 100%:** \|Z\|=1.18, Boundary=1.96 ➔ *Continue* |
| &nbsp; | |
| **MULTIPLE TESTING** | • **Raw p-values:** `[0.042, 0.015, 0.08]`<br>• **Corrected (BH-FDR):** `[0.063, 0.045, 0.08]` |
| &nbsp; | |
| **HTE (BY COUNTRY)** | • **Country: US** \| Lift: -0.0019<br>• **Country: CA** \| Lift: -0.0074<br>• **Country: UK** \| Lift: +0.0013 |
| &nbsp; | |
| **NOVELTY EFFECT** | • **Early Lift:** -0.0030 \| **Late Lift:** 0.0002<br>⚠ **Warning:** Novelty effect suspected. |


## 5. Final Automated Recommendation

```text
============================================================
BUSINESS MEMO
============================================================
RECOMMENDATION: DO NOT SHIP
Confidence: 12.23%
Core Rationale: Variant conversions are structurally flat/negative (p = 0.2394) 
                while triggering an explicit automated novelty warning. Multiple 
                testing corrections successfully neutralized false positive metrics.
============================================================

## 6. Data Cleanup & Repository Footprint

To keep the production repository clean and compliant with data privacy standards, the intermediate tracking schemas (con_treat, page) are stripped post-analysis. The final, anonymized, and validated experimental array is serialized to disk for audit logs:

- Artifact Generated: cleaned_data.csv

## 7. Ethical Considerations & Limitations

- Transient Biases: As demonstrated by the novelty effect warning, short experiment windows can capture misleading behavioral spikes. Running experiments for at least 1-2 full business cycles is strictly recommended.

- Selection Bias: Ensure that external factors (e.g., marketing campaigns targeting specific sub-segments during the experiment) are accounted for to prevent artificial skewing of Heterogeneous Treatment Effects.