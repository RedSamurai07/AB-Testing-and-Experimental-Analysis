import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
from scipy.stats import beta as beta_dist

class ABAnalyzer:
    @staticmethod
    def run_z_test(control_conversions, control_users, treatment_conversions, treatment_users):
        count = np.array([treatment_conversions, control_conversions])
        nobs = np.array([treatment_users, control_users])
        z_stat, p_val = proportions_ztest(count, nobs)
        
        control_rate = control_conversions / control_users
        treatment_rate = treatment_conversions / treatment_users
        lift = treatment_rate - control_rate
        
        return {
            "p_value": float(p_val),
            "z_statistic": float(z_stat),
            "control_rate": float(control_rate),
            "treatment_rate": float(treatment_rate),
            "lift": float(lift),
            "significant": bool(p_val < 0.05)
        }

    @staticmethod
    def run_bayesian_analysis(control_conversions, control_users, treatment_conversions, treatment_users, n_samples=10000):
        # Priors: Alpha=1, Beta=1 (Uniform)
        alpha_c, beta_c = 1 + control_conversions, 1 + (control_users - control_conversions)
        alpha_t, beta_t = 1 + treatment_conversions, 1 + (treatment_users - treatment_conversions)
        
        samples_c = beta_dist.rvs(alpha_c, beta_c, size=n_samples)
        samples_t = beta_dist.rvs(alpha_t, beta_t, size=n_samples)
        
        prob_t_wins = np.mean(samples_t > samples_c)
        
        return {
            "prob_treatment_wins": float(prob_t_wins),
            "recommendation": "SHIP" if prob_t_wins > 0.95 else "DO NOT SHIP"
        }

    @staticmethod
    def check_srm(control_users, treatment_users):
        total = control_users + treatment_users
        observed = [control_users, treatment_users]
        expected = [total / 2, total / 2]
        _, p_val = stats.chisquare(observed, expected)
        
        return {
            "srm_p_value": float(p_val),
            "srm_detected": bool(p_val < 0.01)
        }
