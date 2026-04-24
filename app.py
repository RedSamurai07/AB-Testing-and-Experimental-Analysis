import streamlit as st
from app.analyzer import ABAnalyzer

st.set_page_config(page_title="A/B Testing Analysis", layout="wide")

st.title("A/B Testing Analyzer")
st.write("Calculate Frequentist, Bayesian, and Sample Ratio Mismatch (SRM) results for your A/B test.")

# Input Form
with st.form("ab_test_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Control Group")
        control_users = st.number_input("Control Users", min_value=1, value=10000)
        control_conversions = st.number_input("Control Conversions", min_value=0, value=1000)

    with col2:
        st.subheader("Treatment Group")
        treatment_users = st.number_input("Treatment Users", min_value=1, value=10000)
        treatment_conversions = st.number_input("Treatment Conversions", min_value=0, value=1100)

    submitted = st.form_submit_button("Run Analysis")

if submitted:
    if control_conversions > control_users or treatment_conversions > treatment_users:
        st.error("Error: Conversions cannot exceed the number of users.")
    else:
        # Run analyses utilizing the user's ABAnalyzer class
        z_results = ABAnalyzer.run_z_test(
            control_conversions, control_users,
            treatment_conversions, treatment_users
        )
        
        bayesian_results = ABAnalyzer.run_bayesian_analysis(
            control_conversions, control_users,
            treatment_conversions, treatment_users
        )
        
        srm_results = ABAnalyzer.check_srm(
            control_users, treatment_users
        )

        st.divider()
        st.header("Analysis Results")

        res_col1, res_col2, res_col3 = st.columns(3)

        with res_col1:
            st.subheader("Frequentist (Z-Test)")
            st.metric("Lift", f"{z_results['lift']*100:.2f}%")
            st.write(f"**P-Value**: {z_results['p_value']:.4f}")
            st.write(f"**Z-Statistic**: {z_results['z_statistic']:.4f}")
            if z_results['significant']:
                st.success("Result is Statistically Significant")
            else:
                st.warning("No Significant Difference")
        
        with res_col2:
            st.subheader("Bayesian")
            prob_treatment_wins = bayesian_results['prob_treatment_wins'] * 100
            st.metric("P(Treatment > Control)", f"{prob_treatment_wins:.2f}%")
            
            if bayesian_results['recommendation'] == "SHIP":
                st.success(f"Recommendation: {bayesian_results['recommendation']}")
            else:
                st.warning(f"Recommendation: {bayesian_results['recommendation']}")

        with res_col3:
            st.subheader("Data Quality (SRM)")
            st.write(f"**SRM P-Value**: {srm_results['srm_p_value']:.4f}")
            if srm_results['srm_detected']:
                st.error("SRM Detected! Check your traffic splitting.")
            else:
                st.success("Traffic split is balanced. No SRM.")
