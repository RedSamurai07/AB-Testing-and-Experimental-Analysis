# AB Testing and Experimental Analysis

![Analysis Service CI](https://github.com/RedSamurai07/AB-Testing-and-Experimental-Analysis/actions/workflows/main.yml/badge.svg)


## Table of contents
- [Project Overview](#project-overview)
- [Executive Summary](#executive-summary)
- [Goal](goal)
- [Data Structure](data-structure)
- [Tools](tools)
- [Analysis](#analysis)
- [Insights](insights)
- [Recommendations](recommendations)

### Project Overview
This project utilizes a robust Python-based experimentation engine to evaluate a UI/UX redesign of a global web platform. Unlike standard A/B tests, this framework incorporates Sequential Analysis to mitigate the risks of "p-hacking" and Bayesian Posteriors to provide business stakeholders with intuitive probability-based outcomes. The pipeline integrates user-level demographic data with conversion logs to detect granular performance variances across international markets.

### Executive Summary

- Final Verdict: DO NOT SHIP.

- Primary Rationale: The "New Page" failed to produce a statistically significant lift in conversion (p-value: 0.2394), falling short of the required 95% confidence threshold for production deployment.

- Risk Factor: Bayesian analysis reveals only an 11.9% probability that the Treatment is superior to the Control, indicating a high risk of neutral or negative ROI if rolled out globally.

- SRM Validation: A Chi-square test (p-value: 0.8908) confirmed no Sample Ratio Mismatch, ensuring the 50/50 traffic split was executed without randomization bias.

- Experiment Power: The study was highly sensitive, utilizing over 290,000 users to far exceed the required sample size (4,433 per group) needed to detect a 2% Minimum Detectable Effect (MDE).

- Sequential Monitoring: Implementation of O'Brien-Fleming boundaries allowed for safe interim monitoring at 25%, 50%, and 75% intervals; the Z-score never breached safety limits, justifying the full duration of the test.

### Goal

- Primary Objective: To determine if the "New Page" design provides a statistically significant lift in conversion rate while maintaining a Minimum Detectable Effect (MDE) of 2%.

- Integrity Measures: Implemented a Sample Ratio Mismatch (SRM) check to validate that the randomization algorithm successfully split traffic 50/50 without bias.

- Risk Mitigation: Employed O'Brien-Fleming sequential boundaries to allow for early stopping if the treatment showed severe negative regression, protecting user experience during the experiment.

### Data structure and initial checks
[Dataset](https://www.kaggle.com/datasets/ahmedmohameddawoud/ecommerce-ab-testing)

### Tools
- Excel : Google Sheets - Check for data types, Table formatting
- SQL : Big QueryStudio - Querying, manipulating, and managing data in relational databases in 
- Python: VS code/ Google Colab - Data Preparation and pre-processing, Exploratory Data Analysis, Descriptive Statistics, inferential Statistics, Data manipulation and Analysis(Numpy, Pandas),Visualization (Matplotlib, Seaborn), Feature Engineering, Hypothesis Testing
- Model Deployment: Docker, EC2, MLflow
- CI/CD: GitHub Actions
- Version Control: Git
- Containerization: Docker
- Infrastructure: AWS EC2
- Model Management: MLflow
- Testing: PyTest
- Documentation: Markdown

### Analysis
**Python**
Importing all the necessary libraries
``` python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
```
``` python
import scipy.stats as stats
from scipy.stats import beta as beta_dist
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.multitest import multipletests
```
Dataframe settings
``` python
plt.style.use("seaborn-v0_8-whitegrid")
colors = {"control": "#4C72B0", "treatment": "#DD8452", "neutral": "#55A868"}
seed = 42
np.random.seed(seed)
```
Loading the datsets
``` python
df_ab = pd.read_csv("ab_test.csv")
df_countries = pd.read_csv("countries_ab.csv")
```
Checking the datasets
``` python
df_ab.head()
```
<img width="496" height="212" alt="image" src="https://github.com/user-attachments/assets/84e3ec48-b3c9-40fa-823d-f5fd9e9df3f0" />

``` python
df_countries.head()
```
<img width="203" height="217" alt="image" src="https://github.com/user-attachments/assets/292d1f13-62ea-4ef3-9d65-b773844f6a26" />

Checking if the data is connected to one dataet to another
``` python
df_ab['id'].isin(df_countries['id']).sum()
```
<img width="213" height="51" alt="image" src="https://github.com/user-attachments/assets/1910f2b7-8319-47c9-8421-257a02882c95" />

Merging both the dataframes

``` python
df = pd.merge(df_ab, df_countries, on='id')
df.head()
```
<img width="568" height="217" alt="image" src="https://github.com/user-attachments/assets/56f1d41e-a972-4327-9e0a-e867392dc883" />

Information about the dataset
``` python
def info_data(df):
    print("Shape of the dataset:", df.shape)
    print("\nData types:\n", df.dtypes)
    print("\nMissing values:\n", df.isnull().sum())
    print("\nUnique values:\n", df.nunique())
```
``` python
info_data(df)
```
<img width="335" height="672" alt="image" src="https://github.com/user-attachments/assets/27fb6b82-b2f9-4a39-af9a-4af940973ff4" />

from the above table, we notice that `time` column is `object` datatype which need to be fixed to datetime datatype, No missing values presence, `con_treat`, `page`, `converted` have a binary format output but we need not have to convert as we need to check further how our data is messy from here.

Data time datatype conversion 
``` python
df['time'] = pd.to_timedelta('00:' + df['time'].astype(str))
```
Now, lets' finally check our informatin about the dataset.
``` python
df.info()
```
<img width="472" height="321" alt="image" src="https://github.com/user-attachments/assets/dba44fe4-d3e2-4cc9-a85f-baa967a3361e" />

Now, lets quickly check for distribution of Page conversion rate of users.
``` python
print(df.groupby('id')[['page', 'converted']].sum().value_counts())
```
<img width="392" height="438" alt="image" src="https://github.com/user-attachments/assets/0bfb32ba-fde2-45f1-8516-8ccb86f45981" />

We see that there are multiple page types and we need to clean on this to convert it to `new_page` and `old_page`

Now, let's check for Groups of customerswho purchased the product.
``` python
df.groupby('id')['con_treat'].sum().value_counts().plot(kind = 'bar',title='Control vs Treatment varieties',xlabel='Groups', ylabel='Count')
plt.annotate(f"{df.groupby('id')['con_treat'].sum().value_counts()[0]}", xy=(0, df.groupby('id')['con_treat'].sum().value_counts()[0]), ha='center', va='bottom')
plt.annotate(f"{df.groupby('id')['con_treat'].sum().value_counts()[1]}", xy=(1, df.groupby('id')['con_treat'].sum().value_counts()[1]), ha='center', va='bottom')
plt.xticks(ticks=[0, 1], labels=['Control', 'Treatment'],rotation=0)
plt.show()
print(df.groupby('id')['con_treat'].sum().value_counts())
```
<img width="584" height="444" alt="image" src="https://github.com/user-attachments/assets/f21869ab-02dc-4ff5-8af5-1c826760500f" />

<img width="341" height="212" alt="image" src="https://github.com/user-attachments/assets/49ca7169-1a91-48e2-9918-62e3055f2e15" />

We notice that the data is not aligned whether the user is premium or non preium user kind.

Now, let's check for the distribution of conversion rate.

``` python
df['converted'].value_counts().plot(kind='bar', title='Converted vs Not Converted', xlabel='Converted ratio', ylabel='Count')
plt.xticks(ticks=[0, 1], labels=['Not Converted', 'Converted'],rotation=0)
plt.annotate(f"{df['converted'].value_counts()[0]}", xy=(0, df['converted'].value_counts()[0]), ha='center', va='bottom')
plt.annotate(f"{df['converted'].value_counts()[1]}", xy=(1, df['converted'].value_counts()[1]), ha='center', va='bottom')
plt.show()
print(f"Not Converted: {df['converted'].value_counts()[0]/df['converted'].count():.2%}")
print(f"Converted: {df['converted'].value_counts()[1]/df['converted'].count():.2%}")
```

<img width="584" height="444" alt="image" src="https://github.com/user-attachments/assets/3ee7cc5e-98a7-4061-a153-708305fd0268" />

<img width="231" height="59" alt="image" src="https://github.com/user-attachments/assets/5a8346bd-0cf5-4080-8dbd-a09fcbd5ab4d" />

We see that 88% of the customers have not been converted by these pages.

Now let's check for converison rate by page

``` python
df.groupby('page')['converted'].mean().plot(kind='bar', title='Conversion Rate by Page', xlabel='Page', ylabel='Conversion Rate')
plt.xticks(ticks=[0, 1], labels=['Old Page', 'New Page'],rotation=0)
plt.annotate(f"{df.groupby('page')['converted'].mean()[0]:.2%}", xy=(0, df.groupby('page')['converted'].mean()[0]), ha='center', va='bottom')
plt.annotate(f"{df.groupby('page')['converted'].mean()[1]:.2%}", xy=(1, df.groupby('page')['converted'].mean()[1]), ha='center', va='bottom')
plt.show()
```
<img width="565" height="444" alt="image" src="https://github.com/user-attachments/assets/36503a98-1af5-4edf-87b1-04ef4bf3da79" />

We see that the `new_page` has better conversio rate that `old_page`. Now, lets clean and check on the data.

1). Data Quality Audit.
``` python
def load_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """Audit integrity by cleaning messy labels and checking for contamination."""
    print("=" * 60 + "\nSTEP 1: DATA QUALITY AUDIT\n" + "=" * 60)
    
    con_treat_conditions = [
        (df['con_treat'].isin(['control', 'controlcontrol'])),
        (df['con_treat'].isin(['treatment', 'treatmenttreatment']))
    ]
    df['group_clean'] = np.select(con_treat_conditions, ['control', 'treatment'], default='neither')

    page_conditions = [
        (df['page'].isin(['old_page', 'old_pageold_page'])),
        (df['page'].isin(['new_page', 'new_pageview_page', 'new_pagenew_page']))
    ]
    df['page_clean'] = np.select(page_conditions, ['old_page', 'new_page'], default='other')
    
    
    multi_group = df.groupby("id")["group_clean"].nunique()
    contaminated_ids = multi_group[multi_group > 1].index
    
    if len(contaminated_ids) > 0:
        print(f"⚠ Users in multiple groups: {len(contaminated_ids)}. Removing...")
        df = df[~df["id"].isin(contaminated_ids)].copy()

    analysis_df = df[df['group_clean'].isin(['control', 'treatment'])]
    group_counts = analysis_df["group_clean"].value_counts()
    
    if len(group_counts) == 2:
        _, srm_pval = stats.chisquare(group_counts.values)
        srm_flag = "⚠ SRM DETECTED" if srm_pval < 0.05 else "✓ No SRM"
        print(f"SRM p-value: {srm_pval:.4f}  {srm_flag}")
    
    print(f"\nFinal Group Distribution:\n{df['group_clean'].value_counts()}")
    
    return df

df_validated = load_and_validate(df)
```
<img width="593" height="283" alt="image" src="https://github.com/user-attachments/assets/8a0cedf9-781e-4fe5-aa93-a6c60beed83c" />

2). Experiment Design
``` python
def experiment_design_doc(baseline=0.12, mde=0.02, alpha=0.05, power=0.8):
    print("\n" + "=" * 60 + "\nEXPERIMENT DESIGN\n" + "=" * 60)
    # Effect size using arcsin transformation
    effect_size = 2 * (np.arcsin(np.sqrt(baseline + mde)) - np.arcsin(np.sqrt(baseline)))
    n_per_group = NormalIndPower().solve_power(effect_size=effect_size, alpha=alpha, power=power)
    
    design = {"Required N per group": int(np.ceil(n_per_group)), "Alpha": alpha, "Power": power}
    for k, v in design.items(): print(f"  {k}: {v}")
    return design

experiment_design_doc(baseline=0.12, mde=0.02, alpha=0.05, power=0.8)
```
<img width="621" height="228" alt="image" src="https://github.com/user-attachments/assets/7151d3a9-d2bb-4013-983f-a019cb80c42a" />

3). Frequent Analysis
``` python
def frequentist_analysis(df: pd.DataFrame):
    print("\n" + "=" * 60 + "\nFREQUENTIST ANALYSIS\n" + "=" * 60)
    ctrl = df[df["con_treat"] == "control"]["converted"]
    treat = df[df["con_treat"] == "treatment"]["converted"]
    
    z_stat, p_val = proportions_ztest([treat.sum(), ctrl.sum()], [len(treat), len(ctrl)])
    
    results = pd.DataFrame({
        "group": ["control", "treatment"],
        "conv_rate": [ctrl.mean(), treat.mean()],
        "n": [len(ctrl), len(treat)]
    })
    print(results.to_string(index=False))
    print(f"\nP-value: {p_val:.6f} | {'✓ Significant' if p_val < 0.05 else '✗ Not Significant'}")
    return results
frequentist_results = frequentist_analysis(df_validated)
```
<img width="619" height="226" alt="image" src="https://github.com/user-attachments/assets/80422ba0-a346-49a3-8878-20f2d978b376" />

4). Bayesian A/B Testing
``` python
def bayesian_analysis(df: pd.DataFrame, n_samples=100_000):
    print("\n" + "=" * 60 + "\nBAYESIAN ANALYSIS\n" + "=" * 60)
    ctrl = df[df["con_treat"] == "control"]["converted"]
    treat = df[df["con_treat"] == "treatment"]["converted"]
    
    # Posteriors using Beta distribution
    alpha_c, beta_c = 1 + ctrl.sum(), 1 + (len(ctrl) - ctrl.sum())
    alpha_t, beta_t = 1 + treat.sum(), 1 + (len(treat) - treat.sum())
    
    samples_c = beta_dist.rvs(alpha_c, beta_c, size=n_samples)
    samples_t = beta_dist.rvs(alpha_t, beta_t, size=n_samples)
    
    prob_t_wins = np.mean(samples_t > samples_c)
    print(f"P(Treatment > Control): {prob_t_wins:.2%}")
    return {"prob_treatment_wins": prob_t_wins}

bayesian_results = bayesian_analysis(df_validated)
```
<img width="617" height="121" alt="image" src="https://github.com/user-attachments/assets/0ce88874-3169-4e18-9b38-dd6f8a340a56" />

5). Sequential Testing
``` python
def sequential_analysis(df: pd.DataFrame):
    print("\n" + "=" * 60 + "\nSEQUENTIAL ANALYSIS\n" + "=" * 60)
    df_sorted = df.sort_values("time").reset_index(drop=True)
    z_alpha = stats.norm.ppf(1 - 0.05 / 2)
    
    for frac in [0.25, 0.5, 0.75, 1.0]:
        sub = df_sorted.head(int(len(df_sorted) * frac))
        c = sub[sub["con_treat"] == "control"]["converted"]
        t = sub[sub["con_treat"] == "treatment"]["converted"]
        z, _ = proportions_ztest([t.sum(), c.sum()], [len(t), len(c)])
        boundary = z_alpha / np.sqrt(frac)
        status = "STOP: Reject H₀" if abs(z) > boundary else "Continue"
        print(f" Look at {frac*100:.0f}%: |Z|={abs(z):.2f}, Boundary={boundary:.2f} -> {status}")
sequential_analysis(df_validated)
```
<img width="606" height="175" alt="image" src="https://github.com/user-attachments/assets/75f4b2d3-f988-4db3-aaa6-1cbed6196332" />

6). Multiple testing Correction
``` python
def multiple_testing_correction(df: pd.DataFrame):
    print("\n" + "=" * 60 + "\nMULTIPLE TESTING\n" + "=" * 60)
    # Example checking 'converted' and 'page' as potential independent metrics
    raw_pvals = [0.042, 0.015, 0.08] # Mock p-values for demonstration
    _, bh_pvals, _, _ = multipletests(raw_pvals, method="fdr_bh")
    print(f"Raw p-values: {raw_pvals}\nCorrected (BH-FDR): {bh_pvals.round(4)}")

multiple_testing_correction(df_validated)
```
<img width="613" height="139" alt="image" src="https://github.com/user-attachments/assets/0b5fc537-f042-4dbe-afc1-3dba6f2c1e12" />

7). Heterogenous Treatment Effects
``` python
def heterogeneous_treatment_effects(df: pd.DataFrame):
    print("\n" + "=" * 60 + "\nHTE (BY COUNTRY)\n" + "=" * 60)
    for country in df["country"].unique():
        seg = df[df["country"] == country]
        c_rate = seg[seg["con_treat"] == "control"]["converted"].mean()
        t_rate = seg[seg["con_treat"] == "treatment"]["converted"].mean()
        print(f"Country: {country} | Lift: {t_rate - c_rate:+.4f}")

heterogeneous_treatment_effects(df_validated)
```
<img width="589" height="159" alt="image" src="https://github.com/user-attachments/assets/cebafe99-2492-4bd0-ad78-8533788c88e2" />

8). Novelty Effect Detection
``` python
def novelty_effect_detection(df: pd.DataFrame):
    print("\n" + "=" * 60 + "\nNOVELTY EFFECT\n" + "=" * 60)
    df = df.sort_values("time")
    mid = len(df) // 2
    early, late = df.iloc[:mid], df.iloc[mid:]
    
    early_lift = early[early["con_treat"]=="treatment"]["converted"].mean() - early[early["con_treat"]=="control"]["converted"].mean()
    late_lift = late[late["con_treat"]=="treatment"]["converted"].mean() - late[late["con_treat"]=="control"]["converted"].mean()
    
    print(f"Early Lift: {early_lift:.4f} | Late Lift: {late_lift:.4f}")
    if abs(early_lift) > abs(late_lift) * 1.5: print("⚠ Warning: Novelty effect suspected.")

novelty_effect_detection(df_validated)
```
<img width="592" height="136" alt="image" src="https://github.com/user-attachments/assets/536e249e-aeb9-444f-8b1b-06889d15b407" />

9). Business Decision Memo
``` python
def generate_decision_memo(freq, bayes):
    print("\n" + "=" * 60 + "\nBUSINESS MEMO\n" + "=" * 60)
    rec = "SHIP" if bayes["prob_treatment_wins"] > 0.95 else "DO NOT SHIP"
    print(f"RECOMMENDATION: {rec}\nConfidence: {bayes['prob_treatment_wins']:.1%}")

generate_decision_memo(frequentist_results, bayesian_results)
```
<img width="594" height="130" alt="image" src="https://github.com/user-attachments/assets/8e05b009-c1de-49dc-a44c-75698153a68b" />

``` python
def main(df):
    df = load_and_validate(df)
    design = experiment_design_doc()
    freq_results = frequentist_analysis(df)
    bayes_results = bayesian_analysis(df)
    sequential_analysis(df)
    multiple_testing_correction(df)
    heterogeneous_treatment_effects(df)
    novelty_effect_detection(df)
    generate_decision_memo(freq_results, bayes_results)
    print("\nSTEP 10: ANALYSIS COMPLETE")

main(df)
```
<img width="593" height="638" alt="image" src="https://github.com/user-attachments/assets/1e854da0-c490-472b-8129-08c672ab544b" /><img width="587" height="706" alt="image" src="https://github.com/user-attachments/assets/135d9689-741f-4ab8-86c9-9e12f0e473f5" /><img width="581" height="164" alt="image" src="https://github.com/user-attachments/assets/f3d24341-c69e-49de-bb15-5cbdd28c62fc" />

**SQL**
For sql database I had downloaded it as `cleaned_data.csv` on VS code.
``` python
df.drop(columns = ['con_treat','page'],inplace = True)
ouput = df.to_csv('cleaned_data.csv', index=False)
```

1). Sample Ratio Mismatch (SRM) Detection:
``` sql
WITH group_counts AS (
    SELECT
        group_clean,
        COUNT(DISTINCT id) AS n_users
    FROM `test.ab`
    GROUP BY group_clean
),
totals AS (
    SELECT SUM(n_users) AS total_users FROM group_counts
),
srm_check AS (
    SELECT
        g.group_clean,
        g.n_users                                          AS actual_count,
        t.total_users / 2.0                                AS expected_count,
        ROUND(g.n_users * 100.0 / t.total_users, 2)       AS actual_pct,
        ABS(g.n_users - t.total_users / 2.0) /
            SQRT(t.total_users / 4.0)                      AS z_stat   -- approx chi-squared contribution
    FROM group_counts g
    CROSS JOIN totals t
)
SELECT
    *,
    CASE WHEN ABS(z_stat) > 3.0
         THEN 'SRM DETECTED — do not trust results'
         ELSE 'No SRM — randomization looks clean'
    END AS srm_verdict
FROM srm_check;
```
<img width="1192" height="211" alt="image" src="https://github.com/user-attachments/assets/a509bf48-f997-4294-a21f-238e1eac3218" />

2). Core Conversion Rate Analysis with Confidence Intervals
``` sql
WITH base AS (
    SELECT
        group_clean,
        COUNT(DISTINCT id)            AS n,
        SUM(converted)                     AS conversions,
        AVG(converted)                     AS conversion_rate,
        STDDEV(CAST(converted AS NUMERIC)) AS std_dev  
    FROM `test.ab`
    GROUP BY group_clean
),
stats AS (
    SELECT
        group_clean,
        n,
        conversions,
        ROUND(conversion_rate, 5)                                   AS conv_rate,
        -- Wilson CI: p̂ ± z * sqrt(p̂(1-p̂)/n) / (1 + z²/n)
        ROUND(conversion_rate - 1.96 * SQRT(conversion_rate*(1-conversion_rate)/n), 5)  AS ci_lower,
        ROUND(conversion_rate + 1.96 * SQRT(conversion_rate*(1-conversion_rate)/n), 5)  AS ci_upper
    FROM base
)
SELECT
    s.*,
    t.conv_rate - c.conv_rate                              AS absolute_lift,
    ROUND((t.conv_rate - c.conv_rate) / c.conv_rate, 5)   AS relative_lift
FROM stats s
CROSS JOIN (SELECT conv_rate FROM stats WHERE group_clean = 'control')   c
CROSS JOIN (SELECT conv_rate FROM stats WHERE group_clean = 'treatment') t;
```
<img width="1452" height="216" alt="image" src="https://github.com/user-attachments/assets/5a86f4de-f232-49c8-ab8b-507685d9de4f" />

3). Success Rate Analysis
``` sql
SELECT
    group_clean,
    COUNT(DISTINCT id) AS total_users,
    SUM(converted) AS total_conversions,
    -- Calculate the conversion rate
    ROUND(SUM(converted) * 100.0 / COUNT(DISTINCT id), 2) AS conversion_rate_pct
FROM `test.ab`
GROUP BY group_clean
ORDER BY group_clean;
```
<img width="785" height="204" alt="image" src="https://github.com/user-attachments/assets/7f49c7fd-d3fc-438f-80e7-b6732ad676a9" />

4). Segmented Conversion Lift & Significance Report

``` sql
WITH segment_stats AS (
    SELECT
        country,  -- Swapped from 'device' to match your data
        group_clean,
        COUNT(DISTINCT id) AS n, -- Swapped from 'user_id' to 'id'
        SUM(converted)     AS conversions,
        AVG(converted)     AS conv_rate
    FROM `test.ab`
    WHERE country IS NOT NULL
    GROUP BY country, group_clean
),
pivoted AS (
    SELECT
        country,
        MAX(CASE WHEN group_clean = 'control'   THEN n END)         AS n_control,
        MAX(CASE WHEN group_clean = 'treatment' THEN n END)         AS n_treatment,
        MAX(CASE WHEN group_clean = 'control'   THEN conv_rate END) AS ctrl_conv_rate,
        MAX(CASE WHEN group_clean = 'treatment' THEN conv_rate END) AS treat_conv_rate
    FROM segment_stats
    GROUP BY country
)
SELECT
    country,
    n_control,
    n_treatment,
    ROUND(ctrl_conv_rate, 4)                                       AS ctrl_rate,
    ROUND(treat_conv_rate, 4)                                      AS treat_rate,
    ROUND(treat_conv_rate - ctrl_conv_rate, 4)                     AS absolute_lift,
    ROUND((treat_conv_rate - ctrl_conv_rate) / 
           NULLIF(ctrl_conv_rate, 0), 4)                           AS relative_lift,
    -- Statistical Significance check (Z-test at 95% confidence)
    CASE 
        WHEN n_control > 0 AND n_treatment > 0 AND
             ABS(treat_conv_rate - ctrl_conv_rate) / 
             NULLIF(SQRT(
                (ctrl_conv_rate * (1 - ctrl_conv_rate) / n_control) + 
                (treat_conv_rate * (1 - treat_conv_rate) / n_treatment)
             ), 0) > 1.96 
        THEN 'Significant'
        ELSE 'Not significant'
    END AS significance
FROM pivoted
ORDER BY absolute_lift DESC;
```
<img width="1380" height="251" alt="image" src="https://github.com/user-attachments/assets/438d5b9c-df1a-48b7-9476-e0d985e0bb8f" />

5).A/B Test Time-Series Trend & Rolling Conversion Analysis
``` sql
WITH daily AS (
    SELECT
        group_clean,
        CAST(SPLIT(time, ' ')[OFFSET(0)] AS INT64) AS experiment_day,
        COUNT(DISTINCT id)                         AS daily_users,
        SUM(converted)                             AS daily_conversions,
        AVG(converted)                             AS daily_conv_rate
    FROM `test.ab`
    GROUP BY group_clean, experiment_day
)
SELECT
    d.*,
    -- 3-day rolling average to smooth noise
    AVG(d.daily_conv_rate) OVER (
        PARTITION BY d.group_clean
        ORDER BY d.experiment_day
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_3d_conv_rate
FROM daily d
ORDER BY d.group_clean, d.experiment_day;
```
<img width="1120" height="215" alt="image" src="https://github.com/user-attachments/assets/c987446c-71ea-4224-a415-45d382a949e9" />

6). A/B Test Cumulative Conversion & Stability Analysis

``` sql
WITH ordered AS (
    SELECT
        id,
        group_clean,
        converted,
        time,
        -- Using the time string to rank users by the order they entered the test
        ROW_NUMBER() OVER (PARTITION BY group_clean ORDER BY time) AS user_rank
    FROM `test.ab`
),

cumulative AS (
    SELECT
        group_clean,
        user_rank AS cumulative_users,
        -- Running sum of conversions as each user is added
        SUM(converted) OVER (
            PARTITION BY group_clean 
            ORDER BY user_rank 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_conversions,
        -- Running average (Conversion Rate) as each user is added
        AVG(CAST(converted AS FLOAT64)) OVER (
            PARTITION BY group_clean 
            ORDER BY user_rank 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_conv_rate
    FROM ordered
)

SELECT 
    group_clean,
    cumulative_users,
    running_conversions,
    ROUND(running_conv_rate, 4) AS running_conv_rate
FROM cumulative
-- Sampling every 500 users to make the dataset manageable for visualization
WHERE MOD(cumulative_users, 500) = 0 
ORDER BY group_clean, cumulative_users;
```
<img width="785" height="479" alt="image" src="https://github.com/user-attachments/assets/004acb69-90cf-4087-91d2-438d3e74d068" />

7).Country-Level Subgroup Analysis with Bonferroni Correction
``` sql
WITH country_stats AS (
    SELECT
        country,
        group_clean,
        COUNT(DISTINCT id)  AS n,
        SUM(converted)           AS conversions,
        AVG(converted)           AS conv_rate
    FROM `test.ab`
    WHERE country IS NOT NULL
    GROUP BY country, group_clean
    HAVING COUNT(DISTINCT id) >= 100  -- Minimum sample for reliable inference
),
pivoted AS (
    SELECT
        country,
        MAX(CASE WHEN group_clean='control'   THEN n END)        AS n_ctrl,
        MAX(CASE WHEN group_clean='treatment' THEN n END)        AS n_treat,
        MAX(CASE WHEN group_clean='control'   THEN conv_rate END) AS ctrl_rate,
        MAX(CASE WHEN group_clean='treatment' THEN conv_rate END) AS treat_rate
    FROM country_stats
    GROUP BY country
),
with_zstats AS (
    SELECT
        *,
        (treat_rate - ctrl_rate) /
            SQRT(
                treat_rate*(1-treat_rate)/n_treat +
                ctrl_rate*(1-ctrl_rate)/n_ctrl
            )  AS z_stat,
        COUNT(*) OVER ()  AS n_countries
    FROM pivoted
)
SELECT
    country,
    n_ctrl,
    n_treat,
    ROUND(ctrl_rate,  4) AS ctrl_rate,
    ROUND(treat_rate, 4) AS treat_rate,
    ROUND(treat_rate - ctrl_rate, 4) AS abs_lift,
    ROUND(z_stat, 3) AS z_stat,
    -- Bonferroni corrected threshold: reject if |z| > z(alpha/2/n_countries)
    -- For 4 countries: alpha_adj = 0.05/4 = 0.0125, z_threshold ≈ 2.50
    CASE WHEN ABS(z_stat) > 2.50
         THEN 'Significant (Bonferroni corrected)'
         WHEN ABS(z_stat) > 1.96
         THEN 'Nominally significant (not Bonferroni)'
         ELSE 'Not significant'
    END AS bonferroni_verdict
FROM with_zstats
ORDER BY ABS(z_stat) DESC;
```
<img width="1396" height="248" alt="image" src="https://github.com/user-attachments/assets/e586766f-f9d1-4644-acbd-e7dacf644714" />


**Tableau**

<img width="1520" height="927" alt="image" src="https://github.com/user-attachments/assets/06e70eca-c088-45ea-9151-11e4d1164122" />


Model Deployment Guide:

Stage 1: Setting Up Your Local Environment
Begin your journey by establishing a development workspace on your computer before anything goes online. Get Python & Pip: Obtain the most recent 3.x release from python.org and confirm installation by entering python --version in your command line. Get Git: Acquire Git and register for a GitHub account, then execute git config --global user.name "Your Name" to connect your system to your profile. Get Docker Desktop: This critical software lets you bundle your application to ensure consistent behavior across your laptop and production servers. While setting this up, register for Docker Hub—it will serve as your "Container Repository."

Stage 2: Organizing Your Workspace (Code & Dependencies)
Structure your machine learning application properly. Build a Project Directory: Execute mkdir my-ml-app && cd my-ml-app. Configure a Virtual Environment: Execute python -m venv venv and activate using source venv/bin/activate (Mac) or .\venv\Scripts\activate (Windows).
Purpose? This prevents conflicts between ML frameworks (such as Scikit-Learn or PyTorch) across different projects. Generate a requirements.txt: Document your dependencies here (examples: pandas, scikit-learn, flask). Deploy them via pip install -r requirements.txt. Prior to this, capture package versions by running pip list in your terminal.

Stage 3: Packaging for Distribution (Containerization & Repository)
Your code is ready; now package it for transport. Develop a Dockerfile: This script instructs Docker to fetch Python, transfer your codebase, install dependencies, and launch the model. Construct your Image: Execute docker build -t my-ml-model. Upload to Repository: Authenticate with Docker Hub through your terminal (docker login) and upload your image for cloud accessibility: docker push username/my-ml-model. Important: Within the Dockerfile, verify Python tags at hub.docker.com/_/python for containerization compatibility.

tage 4: Production Launch & Workflow Automation
Manual deployment is outdated; professionals employ automation to synchronize the production application with the source code. Cloud Infrastructure: Select a platform (such as GCP or AWS) to host your model permanently online. CI/CD Framework: Implement GitHub Actions to automate the build and deployment workflow. Each code commit to GitHub triggers automatic cloud updates. Basic Monitoring: Leverage your provider's native tools to track server performance and resource consumption.

Stage 5: Cloud Infrastructure & Continuous Integration (Deployment & CI/CD)
This stage brings your project into production. Cloud Platform Account (AWS/GCP/Azure): Choose one provider. Newcomers often find Google Cloud (GCP) or DigitalOcean more user-friendly than AWS. CI/CD (GitHub Actions): First, create a test.py file for model validation and metric visualization on MLflow.

Establish a directory in your project: .github/workflows/ and within it:
Include a .yml configuration that triggers: "Upon each GitHub code push, reconstruct my Docker image and deploy to the cloud."
Monitoring: After the model runs on cloud infrastructure, utilize the provider's dashboard (like AWS CloudWatch) to detect errors or excessive CPU consumption.

Stage 5: Performance Monitoring (Prometheus & Grafana):
The final verification layer.
1). Prometheus: Collects metrics from your deployed model (traffic volume, crash reports).
2). Grafana: Interfaces with Prometheus to display dynamic, visual dashboards of your model's performance.

### Insights

- No SRM Found: With a Chi-square p-value of 0.8908, we confirmed that the distribution of 145,381 (Treatment) vs. 145,307 (Control) users was statistically sound.

- Design Power: The experiment was highly overpowered; while we only required 4,433 users per group to detect our MDE, we utilized the full available dataset to maximize our confidence in a "No-Ship" decision.

- Frequentist Failure: The Control converted at 12.03% vs. the Treatment at 11.89%. The resulting p-value (0.239) confirms we cannot reject the Null Hypothesis.

- Bayesian Certainty: There is only an 11.9% probability that the Treatment is superior to the Control. In a FAANG environment, we typically require >95% probability of being better to justify the engineering cost of a rollout.

- Early vs. Late Lift: The Early Lift was -0.0030, whereas the Late Lift was +0.0002.

- Interpretation: The initial drop in performance was likely "change aversion." While performance stabilized over time, it never achieved a positive lift significant enough to justify replacing the existing infrastructure.

- UK Resilience: The UK was the only market to show a positive lift (+0.0013), suggesting the design might resonate better with British cohorts.

- CA/US Resistance: Significant friction was observed in Canada (-0.0074) and the US (-0.0019)

### Recommendations

- Immediate Action: Rollback Treatment: Based on the global negative lift and low Bayesian probability of success, the "New Page" should not be promoted to 100% traffic.

- Product Iteration (UK-Only): Given the positive trend in the UK, I recommend a follow-up "V2" experiment isolated to the UK market to see if the small lift can be amplified through local optimization.

- Investigate Technical Latency: The significant dip in Canada (CA) conversion suggests potential technical issues (e.g., page load speeds or localized asset rendering) rather than just a design preference. I recommend a Core Web Vitals audit for the CA segment.

- UX Research Deep Dive: Conduct moderated usability sessions with US users to understand why the "Old Page" continues to drive higher conversion. This "Why" will inform the next iteration of the "New Page."
