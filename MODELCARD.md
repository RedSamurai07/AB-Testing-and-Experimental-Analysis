# Model Card: A/B Testing and Experimental Analysis

---

## 1. Model Details

| Field | Details |
|---|---|
| **Framework Name** | A/B Testing & Experimental Analysis Framework — Multi-Method Statistical Engine |
| **Python Version** | 3.10 |
| **Analysis Date** | March 2026 |
| **Primary Method** | Two-Proportion Z-Test (Frequentist) |
| **Supporting Methods** | Bayesian Beta-Posterior Analysis, Sequential O'Brien-Fleming Testing, Sample Ratio Mismatch (SRM) Detection, Heterogeneous Treatment Effects (HTE), Novelty Effect Detection, Benjamini-Hochberg FDR Correction |
| **Primary Metric** | p-value (significance threshold: α = 0.05) |
| **Secondary Metrics** | Lift (absolute conversion delta), P(Treatment > Control) — Bayesian probability |
| **API Framework** | FastAPI + Uvicorn |
| **Live App** | [Streamlit App](https://redsamurai07-ab-testing-and-experimental-analysis-app-0yc9dh.streamlit.app/) |

---

## 2. Intended Use

- **Primary Use Case:** Evaluate whether a UI/UX redesign ("New Page") produces a statistically significant lift in conversion rate over the existing "Old Page" for a global web platform.
- **Target Users:** Product Managers, Data Scientists, Growth Engineers, Experimentation Teams.
- **Out of Scope:** Multi-armed bandit optimisation, real-time adaptive experiments, or experiments beyond binary conversion metrics.

---

## 3. Dataset

| Property | Value |
|---|---|
| **Source Files** | `ab_test.csv` + `countries_ab.csv` |
| **Total Rows** | 294,478 |
| **Control Users** | 147,202 |
| **Treatment Users** | 147,276 |
| **Overall Conversion Rate** | ~12.0% |
| **Data Type** | Anonymised proprietary operational data |

**Dataset Schema:**

| Feature | Description | Data Type |
|---|---|---|
| `id` | Unique user identifier | int64 |
| `time` | Time of user session | object (timedelta) |
| `con_treat` | Group assignment: `control` / `treatment` | object |
| `page` | Page version seen: `old_page` / `new_page` | object |
| `converted` | Binary conversion outcome (1 = converted) | int64 |
| `country` | User's country (from `countries_ab.csv`) | object |

**Data Quality Issues Detected & Fixed:**

| Issue | Fix Applied |
|---|---|
| Duplicate labels (`controlcontrol`, `treatmenttreatment`) | Normalised to `control` / `treatment` via `np.select` |
| Mismatched page labels (`new_pageview_page`, `old_pageold_page`) | Normalised to `old_page` / `new_page` |
| Users appearing in both groups (contamination) | Removed contaminated user IDs entirely |
| `time` column stored as string | Converted to `pd.Timedelta` |

---

## 4. Methodology & Pipeline Architecture
 
```
┌─────────────────────────────────────────────────────────────────────┐
│                        1. DATA LAYER                                │
│  ab_test.csv  +  countries_ab.csv                                   │
│         │                                                           │
│         ▼  pd.merge(on='id')                                        │
│  Unified DataFrame (290,000+ user-level records)                    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                   2. DATA QUALITY AUDIT                             │
│  ├── Label normalisation (np.select) — clean group & page labels    │
│  ├── Cross-contamination removal (users in both groups)             │
│  ├── Datetime type correction (time → timedelta)                    │
│  └── SRM Chi-square check (p=0.8908 ✓ No mismatch)                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                  3. EXPERIMENT DESIGN                               │
│  ├── Power analysis (arcsine effect size, NormalIndPower)           │
│  ├── MDE = 2%, α = 0.05, power = 80%                               │
│  └── Min sample = 4,433/group | Actual = 145,000+/group            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│               4. STATISTICAL TESTING ENGINE                         │
│                                                                     │
│  ┌──────────────────┐ ┌──────────────────┐ ┌────────────────────┐  │
│  │   FREQUENTIST    │ │    BAYESIAN      │ │     SEQUENTIAL     │  │
│  │ Two-Proportion   │ │  Beta-Binomial   │ │  O'Brien-Fleming   │  │
│  │    Z-Test        │ │  Monte Carlo     │ │   Boundaries       │  │
│  │  p = 0.2394 ✗    │ │  P(T>C) = 11.9% │ │  Z never breached  │  │
│  └──────────────────┘ └──────────────────┘ └────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                5. SUBGROUP / GEOGRAPHIC ANALYSIS                    │
│  ├── Per-country Z-tests (US, UK, CA, ...)                          │
│  └── Benjamini-Hochberg FDR correction (multipletests)             │
│      → No country reaches significance after correction             │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│               6. REPORTING & SERVING                                │
│  ├── Streamlit interactive dashboard (app.py)                       │
│  │     Real-time metric input, live test result display             │
│  └── FastAPI backend (app/ directory)                               │
│        REST endpoint for programmatic experiment queries            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                  7. CONTAINERISATION & CI/CD                        │
│  ├── Docker                                                         │
│  │   python:3.10-slim base image                                    │
│  │   Installs: scipy, statsmodels, pandas, numpy, streamlit, pytest │
│  │   Entrypoint: Streamlit app on port 8501                         │
│  │                                                                  │
│  ├── GitHub Actions CI Pipeline (.github/workflows/main.yml)        │
│  │   Trigger: every push to main                                    │
│  │   Steps: checkout → install deps → run pytest (tests/ dir)      │
│  │   Badge: [![Analysis Service CI] passing]                        │
│  │                                                                  │
│  └── PyTest (tests/ directory)                                      │
│      Unit tests for: data loading, SRM check, Z-test engine,       │
│      Bayesian sampler, sequential boundary computation              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                     8. CLOUD DEPLOYMENT                             │
│  ├── AWS EC2 (Ubuntu 22.04 LTS) — FastAPI backend                   │
│  │   Ports: 5000 (FastAPI), 8501 (Streamlit)                       │
│  │   docker run --restart unless-stopped                           │
│  └── Streamlit Cloud — Live public dashboard                        │
│      https://redsamurai07-ab-testing-and-experimental-analysis...   │
└─────────────────────────────────────────────────────────────────────┘
```
 
---

## 5. Experiment Design

| Parameter | Value |
|---|---|
| **Baseline Conversion Rate** | 12.0% |
| **Minimum Detectable Effect (MDE)** | 2.0% absolute lift |
| **Significance Level (α)** | 0.05 |
| **Statistical Power (1-β)** | 80% |
| **Required N per group** | 4,433 |
| **Actual N per group** | ~147,200 |
| **Experiment Status** | Highly overpowered (33× required sample) |

The experiment far exceeded the minimum required sample size, ensuring that a null result is not due to insufficient power — the "New Page" genuinely failed to produce meaningful lift.

---

## 6. Statistical Analysis Results

### Frequentist Analysis (Two-Proportion Z-Test)

| Metric | Control | Treatment |
|---|---|---|
| Users | 147,202 | 147,276 |
| Conversions | 17,723 | 17,514 |
| Conversion Rate | **12.040%** | **11.892%** |
| Absolute Lift | — | **-0.148%** |
| Z-Statistic | — | -1.2369 |
| P-Value | — | **0.2161** |
| Significant (α=0.05) | — | ❌ No |

### Bayesian Analysis (Beta Posterior, 100,000 samples)

| Metric | Value |
|---|---|
| Prior | Uniform Beta(1, 1) |
| P(Treatment > Control) | **~11.9%** |
| Recommendation | **DO NOT SHIP** |
| Threshold for "SHIP" | > 95% probability |

### Sample Ratio Mismatch (SRM) Check

| Metric | Value |
|---|---|
| Chi-Square p-value | **0.8915** |
| SRM Detected | ❌ No — randomization is clean |
| Traffic Split | 50.0% / 50.0% ✓ |

### Sequential Analysis (O'Brien-Fleming Boundaries)

| Interim Look | % of Data | \|Z-Score\| | Boundary | Decision |
|---|---|---|---|---|
| 1st look | 25% | — | ~2.77 | Continue |
| 2nd look | 50% | — | ~1.96 | Continue |
| 3rd look | 75% | — | ~1.60 | Continue |
| Final | 100% | 1.24 | 1.96 | **Do Not Reject H₀** |

Z-score never breached O'Brien-Fleming safety limits at any interim point.

---

## 7. Heterogeneous Treatment Effects (HTE by Country)

| Country | Lift |
|---|---|
| UK | **+0.0013** ← Only positive market |
| US | -0.0019 |
| CA | **-0.0074** ← Largest negative impact |

**Key finding:** The "New Page" showed positive lift only in the UK (+0.13pp). Canada showed the most severe negative regression, suggesting possible technical/rendering issues in the CA region rather than a pure design preference problem.

---

## 8. Novelty Effect Detection

| Period | Lift |
|---|---|
| Early (first 50% of data) | -0.0030 |
| Late (last 50% of data) | +0.0002 |

**Interpretation:** The initial drop in performance was likely due to "change aversion" among existing users. While performance stabilised over time, it never achieved meaningful positive lift — confirming the result is not a novelty effect artefact.

---

## 9. Multiple Testing Correction (Benjamini-Hochberg FDR)

Applied to guard against false positives when testing multiple metrics simultaneously:

| Raw p-values | BH-FDR Corrected p-values |
|---|---|
| [0.042, 0.015, 0.08] | [0.063, 0.045, 0.08] |

Post-correction, the initially borderline p=0.042 test becomes non-significant — reinforcing the conservative "Do Not Ship" recommendation.

---

## 10. Business Decision

```
════════════════════════════════════════
   FINAL VERDICT: DO NOT SHIP
════════════════════════════════════════
Frequentist p-value:    0.2161 (> 0.05)
Bayesian P(T>C):        ~11.9% (< 95%)
Absolute Lift:          -0.148%
SRM:                    None detected
```

**Rationale:**
- The "New Page" failed to produce a statistically significant conversion lift (p = 0.2161).
- Bayesian analysis shows only ~11.9% probability the Treatment outperforms Control — far below the 95% deployment threshold.
- The experiment was highly powered (294K+ users), so the null result reflects a genuine absence of effect, not insufficient data.

---

## 11. Follow-Up Recommendations

| Action | Rationale |
|---|---|
| **UK-only V2 test** | UK showed the only positive lift (+0.13pp) — worth isolating and amplifying |
| **Core Web Vitals audit (CA)** | CA showed -0.74pp regression — likely a technical/latency issue, not design |
| **Qualitative UX research (US users)** | Understand why "Old Page" continues to win with US cohorts |
| **Rollback Treatment globally** | Global negative lift and low Bayesian confidence don't justify engineering rollout cost |

---

## 12. API Endpoints (FastAPI)

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check — confirms API is running |
| `/health` | GET | Returns `{"status": "healthy"}` |
| `/analyze` | POST | Runs Z-test + Bayesian + SRM analysis; logs results to MLflow |

**Request schema:**
```json
{
  "control_conversions": 17723,
  "control_users": 147202,
  "treatment_conversions": 17514,
  "treatment_users": 147276,
  "experiment_name": "ui_redesign_v1"
}
```

**Response includes:** p-value, z-statistic, lift, significance flag, P(Treatment wins), SHIP/DO NOT SHIP recommendation, SRM p-value and flag.

---

## 13. Ethical Considerations & Limitations

- **Scope:** The dataset covers a single binary conversion metric. Real-world experiments should monitor secondary metrics (session duration, bounce rate, revenue per user) to avoid optimising a narrow KPI at the expense of broader user experience.
- **Anonymisation:** All user IDs are anonymised — no PII is stored or processed.
- **Country-Level Inference:** HTE results for countries (especially CA) are directional. A follow-up dedicated experiment with pre-registered country-level hypotheses is required before drawing causal conclusions.
- **One-Sided Novelty Risk:** While novelty effect analysis showed stabilisation, a longer experiment duration (8–10 weeks) is recommended to fully rule out lingering change-aversion dynamics.
- **Data Contamination:** 0 contaminated user IDs (users assigned to both groups) were removed. In higher-traffic experiments, contamination rates above 1% should trigger a full re-randomisation review.

---

## 14. Infrastructure & Tools

| Category | Tool |
|---|---|
| Language | Python 3.10 |
| Statistical Testing | SciPy (proportions_ztest, chisquare), Statsmodels (NormalIndPower, multipletests) |
| Bayesian Analysis | SciPy Beta distribution (Monte Carlo sampling, 100K samples) |
| API Framework | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Experiment Tracking | MLflow |
| Data Processing | Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn |
| SQL Engine | Google BigQuery |
| Testing | Pytest + pytest-cov |
| Coverage Reporting | Codecov |
| CI/CD | GitHub Actions |
| Containerisation | Docker |
| Cloud Infrastructure | AWS EC2 |
| Version Control | Git |

---

## 15. Final Decision Summary

```
══════════════════════════════════════════════════════════════
        A/B TESTING — EXECUTIVE SUMMARY REPORT
══════════════════════════════════════════════════════════════
Dataset:         294,478 users | 50/50 traffic split
Experiment:      UI/UX redesign — Old Page vs New Page
Primary KPI:     Conversion Rate
══════════════════════════════════════════════════════════════
RESULTS:
Control Rate:        12.040%
Treatment Rate:      11.892%
Absolute Lift:       -0.148%
P-Value:             0.2161  (NOT significant at α=0.05)
P(Treatment Wins):   ~11.9%  (Bayesian — DO NOT SHIP)
SRM Check:           CLEAN   (p=0.8915)
══════════════════════════════════════════════════════════════
KEY DESIGN DECISIONS:
1. SRM check run before any analysis — no bias detected
2. Sequential O'Brien-Fleming boundaries — safe interim monitoring
3. Bayesian posteriors supplement frequentist p-value
4. BH-FDR correction applied for multiple metric testing
5. HTE analysis by country — CA regression flagged for audit
══════════════════════════════════════════════════════════════
PRODUCTION RECOMMENDATIONS:
• DO NOT SHIP the New Page globally
• Run UK-only V2 test to amplify the +0.13pp positive signal
• Conduct Core Web Vitals audit for CA segment
• Run UX research sessions with US users to understand Old Page preference
• Log all future experiments to MLflow for centralised audit trail
══════════════════════════════════════════════════════════════
```
