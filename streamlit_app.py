# streamlit_app.py

import streamlit as st
import pandas as pd

from main import run_alm

# Streamlit App Title
st.set_page_config(page_title="ALM SaaS Platform", layout="wide")
st.title("📊 Asset-Liability Management (ALM) SaaS")

# File Upload
st.sidebar.header("Upload Portfolio Excel File")
uploaded_file = st.sidebar.file_uploader("Choose Excel file", type=["xlsx"])

# Inputs for Curves (optional)
st.sidebar.header("Zero Curve & Forward Curve (Optional)")
zero_curve_uploaded = st.sidebar.file_uploader("Upload Zero Curve", type=["xlsx"], key="zero")
forward_curve_uploaded = st.sidebar.file_uploader("Upload Forward Curve", type=["xlsx"], key="forward")

valuation_date = st.sidebar.date_input("Valuation Date")

# Run Analysis
if st.sidebar.button("Run ALM Analysis 🚀"):
    if uploaded_file is None:
        st.error("Please upload a portfolio Excel file before running analysis.")
    else:
        # Load Zero Curve if available
        if zero_curve_uploaded is not None:
            zero_curve = pd.read_excel(zero_curve_uploaded)
        else:
            zero_curve = pd.DataFrame({"Months": [0, 12, 24, 36], "Zero Rate": [0.02, 0.025, 0.03, 0.035]})

        # Load Forward Curve if available
        if forward_curve_uploaded is not None:
            forward_curve = pd.read_excel(forward_curve_uploaded)
        else:
            forward_curve = pd.DataFrame({"Months": [0, 12, 24, 36], "Forward Rate": [0.02, 0.026, 0.032, 0.037]})

        st.success("Running ALM analysis...")

        try:
            # Run ALM system
            results, output_buffer = run_alm(uploaded_file, valuation_date, zero_curve, forward_curve)

            st.success("✅ ALM Analysis Complete!")

            # Cashflow Charts
            st.subheader("📈 Daily Aggregated Cashflows")
            st.dataframe(results["daily_agg"].head(20))

            st.subheader("📈 Monthly Aggregated Cashflows")
            st.dataframe(results["monthly_agg"].head(20))

            # Rate Shock Results
            st.subheader("📉 Rate Shock Analysis")
            st.dataframe(results["rate_shock_results"].head(20))

            # RBI Reports
            st.subheader("📋 RBI Regulatory Reports")
            for report_name, report_df in results["rbi_reports"].items():
                with st.expander(f"View {report_name}"):
                    st.dataframe(report_df)

            # Download Button
            st.subheader("📥 Download ALM Results")
            st.download_button(
                label="Download Full ALM Results Excel",
                data=output_buffer,
                file_name="ALM_Results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
