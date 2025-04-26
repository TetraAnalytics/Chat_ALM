# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from main import run_alm, load_portfolio_from_excel
from Analytics.CashflowCalculator import generate_cashflows_for_portfolio
from Analytics.AggregatedCashflows import (
    aggregate_daily_cashflows_by_type,
    aggregate_monthly_cashflows_by_type
)

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
        st.dataframe(results["cashflows"].head(100), use_container_width=True)

        st.header("Daily Aggregated Cashflows")
        st.dataframe(results["daily_agg"].head(100), use_container_width=True)

        st.header("Monthly Aggregated Cashflows")
        st.dataframe(results["monthly_agg"].head(100), use_container_width=True)

        # Plot Monthly Cashflow
        st.subheader("Monthly Cashflow Profile")
        fig = px.bar(
            results["monthly_agg"],
            x="PaymentMonth",
            y="NetCashflow",
            title="Monthly Net Cashflows",
            labels={"PaymentMonth": "Month", "NetCashflow": "Cashflow Amount"},
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

