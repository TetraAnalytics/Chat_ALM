import streamlit as st
import pandas as pd
import plotly.express as px

from main import run_alm, load_portfolio_from_excel
from Analytics.CashflowCalculator import generate_cashflows_for_portfolio
from Analytics.AggregatedCashflows import (
    aggregate_daily_cashflows_by_type,
    aggregate_monthly_cashflows_by_type
)
from Analytics.YieldCurveBuilder import build_zero_forward_curve
from Analytics.RateShockEngine import apply_parallel_rate_shocks
from Output.ExcelWriter import RBI_Regulatory_Reports_Exists

st.set_page_config(page_title="ALM App", layout="wide")
st.title("Fixed-Income Asset-Liability Management System")

st.write("📊 Upload your portfolio file and run full ALM analytics.")

uploaded_file = st.file_uploader("Upload Portfolio Excel File", type=["xlsx"])
valuation_date = st.date_input("Valuation Date", pd.to_datetime("today").date())

if uploaded_file:
    input_file = "uploaded_portfolio.xlsx"
    output_file = "ALM_Results.xlsx"

    with open(input_file, "wb") as f:
        f.write(uploaded_file.read())

    zero_curve, forward_curve = build_zero_forward_curve()

    if st.button("Run ALM Analysis"):
        with st.spinner("Processing..."):
            run_alm(input_file, output_file, valuation_date, zero_curve, forward_curve)

        st.success("Analysis Complete!")

        with open(output_file, "rb") as f:
            st.download_button("Download ALM Results", f, file_name=output_file)

        if RBI_Regulatory_Reports_Exists():
            with open("RBI_Regulatory_Reports.xlsx", "rb") as f:
                st.download_button("Download RBI Regulatory Reports", f, file_name="RBI_Regulatory_Reports.xlsx")

        # Load instruments and cash flows
        instruments = load_portfolio_from_excel(input_file, zero_curve, forward_curve)
        instrument_map = {i.ID: i.__class__.__name__ for i in instruments}
        cashflows_dict = generate_cashflows_for_portfolio(instruments)

        # ----------------------------
        # Daily Aggregation + Chart
        # ----------------------------
        daily_df = aggregate_daily_cashflows_by_type(cashflows_dict, instrument_map)
        daily_df['total'] = daily_df['interest'] + daily_df['principal']

        with st.expander("Daily Aggregated Cash Flows by Instrument Type", expanded=False):
            fig_daily = px.bar(
                daily_df,
                x='payment_date',
                y='total',
                color='instrument_type',
                title='Daily Aggregated Cash Flows',
                labels={"total": "Cash Flow", "payment_date": "Date"},
            )
            st.plotly_chart(fig_daily, use_container_width=True)
            st.dataframe(daily_df)

        # ----------------------------
        # Monthly Aggregation + Chart
        # ----------------------------
        monthly_df = aggregate_monthly_cashflows_by_type(cashflows_dict, instrument_map)
        monthly_df['total'] = monthly_df['interest'] + monthly_df['principal']

        with st.expander("Monthly Aggregated Cash Flows by Instrument Type", expanded=False):
            fig_monthly = px.bar(
                monthly_df,
                x='Month',
                y='total',
                color='instrument_type',
                title='Monthly Aggregated Cash Flows',
                labels={"total": "Cash Flow", "Month": "Month"},
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            st.dataframe(monthly_df)

        # ----------------------------
        # RBI Rate Shock Analysis
        # ----------------------------
        shock_df = apply_parallel_rate_shocks(instruments, valuation_date=valuation_date)
        portfolio_shocks = shock_df[shock_df["ID"] == "PORTFOLIO_TOTAL"]

        with st.expander("Interest Rate Sensitivity (RBI)", expanded=False):
            st.subheader("Portfolio Value Under Interest Rate Shocks")

            fig = px.bar(
                portfolio_shocks,
                x="Shock (bps)",
                y="Price",
                title="RBI Rate Shock Impact on Portfolio Value",
                labels={"Price": "Portfolio Value"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(portfolio_shocks)
