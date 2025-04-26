# streamlit_app.py

import streamlit as st
import plotly.express as px
import pandas as pd  # needed for combining cashflows
from main import run_alm, load_portfolio_from_excel
from rbi.reporting import generate_rbi_reports

# --- Quick Import Test for generate_rbi_reports ---
try:
    dummy_test = generate_rbi_reports({})
    print("✅ rbi.reporting imported successfully.")
except Exception as e:
    print(f"❌ Import test failed: {e}")
# ---------------------------------------------------


st.set_page_config(page_title="ALM System", layout="wide")
st.title("📈 Asset Liability Management System")

uploaded_file = st.file_uploader("Upload Portfolio Excel File", type=["xlsx"])

if uploaded_file:
    with st.spinner("Processing Portfolio..."):
        portfolio = load_portfolio_from_excel(uploaded_file)

        st.success("Portfolio Loaded Successfully!")

        # Run full ALM Analysis
        results = run_alm(portfolio)

        st.success("Analysis Complete!")

        # Show key results
        st.header("Portfolio Pricing Summary")
        st.dataframe(results["pricing"], use_container_width=True)

        st.header("Cashflows (First 100 Rows)")

        # Combine all instrument cashflows together
        combined_cashflows_df = pd.concat(results["cashflows"].values())

        # Display first 100 rows
        st.dataframe(combined_cashflows_df.head(100), use_container_width=True)

        st.header("Daily Aggregated Cashflows")
        st.dataframe(results["daily_agg"].head(100), use_container_width=True)

        st.header("Monthly Aggregated Cashflows")
        st.dataframe(results["monthly_agg"].head(100), use_container_width=True)

        # Plot Monthly Cashflow
        st.subheader("Monthly Cashflow Profile")
        fig = px.bar(
            results["monthly_agg"],
            x="Month",
            y="NetCashflow",
            title="Monthly Net Cashflows",
            labels={"Month": "Month", "NetCashflow": "Cashflow Amount"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # Download Results
        st.header("Download ALM Results")
        try:
            with open("/tmp/ALM_Results.xlsx", "rb") as f:
                st.download_button(
                    label="📥 Download Full ALM Results",
                    data=f,
                    file_name="ALM_Results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.error("ALM Results file not found. Please re-run the analysis.")
