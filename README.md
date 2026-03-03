# A/B Testing & Experimentation Analysis

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

 - The initial checks of your transactions.csv dataset reveal the following:

| Features | Description | Data types |
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 
| -------- | -------- | -------- | 

### Tools
- Excel : Google Sheets - Check for data types, Table formatting
- SQL : Big QueryStudio - Querying, manipulating, and managing data in relational databases in 
- Python: Google Colab - Data Preparation and pre-processing, Exploratory Data Analysis, Descriptive Statistics, inferential Statistics, Data manipulation and Analysis(Numpy, Pandas),Visualization (Matplotlib, Seaborn), Feature Engineering, Hypothesis Testing
  
### Analysis
**Python**

**Hypothesis testing**


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


