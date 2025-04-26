# main.py

import pandas as pd
import io

from Instruments.Bond import Bond
from Instruments.Mortgage import Mortgage
from Instruments.InterestRateSwap import InterestRateSwap
from Instruments.DemandDeposit import DemandDeposit

from Analytics.CashflowCalculator import generate_cashflows_for_portfolio
from Analytics.AggregatedCashflows import (
    aggregate_daily_cashflows_by_type,
    aggregate_monthly_cashflows_by_type
)
from Analytics.RateShockEngine import apply_parallel_rate_shocks
from RBI.Reporting import generate_rbi_reports

def load_portfolio_from_excel(uploaded_file, zero_curve, forward_curve):
    """
    Loads the portfolio instruments from an uploaded Excel file.

    Args:
        uploaded_file (BytesIO): Uploaded Excel file
        zero_curve (DataFrame): Zero curve DataFrame
        forward_curve (DataFrame): Forward curve DataFrame

    Returns:
        list: List of instrument objects
    """
    # Read the uploaded Excel file into a DataFrame
    portfolio_df = pd.read_excel(uploaded_file, sheet_name=0)

    portfolio = []

    for idx, row in portfolio_df.iterrows():
        instrument_type = row.get('INSTRUMENT_TYPE', '').strip()

        if instrument_type == 'Bond':
            instrument = Bond.from_dataframe_row(row, zero_curve)
        elif instrument_type == 'Mortgage':
            instrument = Mortgage.from_dataframe_row(row, zero_curve, forward_curve)
        elif instrument_type == 'InterestRateSwap':
            instrument = InterestRateSwap.from_dataframe_row(row, zero_curve, forward_curve)
        elif instrument_type == 'DemandDeposit':
            instrument = DemandDeposit.from_dataframe_row(row, zero_curve)
        else:
            continue  # Skip unknown instrument types

        portfolio.append(instrument)

    return portfolio


def run_alm(uploaded_file, output_excel_buffer, valuation_date, zero_curve, forward_curve):
    """
    Runs the full ALM process: cashflows, rate shocks, aggregation, RBI reports.

    Args:
        uploaded_file (BytesIO): Uploaded Excel file
        output_excel_buffer (BytesIO): In-memory Excel output
        valuation_date (datetime): Valuation date
        zero_curve (DataFrame): Zero curve DataFrame
        forward_curve (DataFrame): Forward curve DataFrame

    Returns:
        dict: Dictionary containing all outputs needed for GUI
    """
    # Load portfolio
    portfolio = load_portfolio_from_excel(uploaded_file, zero_curve, forward_curve)

    if not portfolio:
        raise ValueError("No valid instruments loaded from uploaded file.")

    # Generate individual instrument cashflows
    cashflow_dict = generate_cashflows_for_portfolio(portfolio)

    # Aggregate cashflows
    daily_agg = aggregate_daily_cashflows_by_type(cashflow_dict)
    monthly_agg = aggregate_monthly_cashflows_by_type(cashflow_dict)

    # Apply rate shocks (±100bp, ±200bp)
    rate_shock_results = apply_parallel_rate_shocks(portfolio, zero_curve)

    # Generate RBI-specific regulatory reports
    rbi_reports = generate_rbi_reports(portfolio, valuation_date, zero_curve)

    # Export everything to Excel (in-memory)
    with pd.ExcelWriter(output_excel_buffer, engine='openpyxl') as writer:
        # Save cashflows
        for instrument_id, cf_df in cashflow_dict.items():
            sheet_name = instrument_id[:31]  # Excel limit
            cf_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Save aggregated cashflows
        daily_agg.to_excel(writer, sheet_name='Daily_Aggregated', index=False)
        monthly_agg.to_excel(writer, sheet_name='Monthly_Aggregated', index=False)

        # Save rate shock results
        rate_shock_results.to_excel(writer, sheet_name='Rate_Shock_Analysis', index=False)

        # Save RBI reports
        for report_name, report_df in rbi_reports.items():
            sheet_name = report_name[:31]
            report_df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Return results for Streamlit GUI
    results = {
        "cashflows": cashflow_dict,
        "daily_agg": daily_agg,
        "monthly_agg": monthly_agg,
        "rate_shock_results": rate_shock_results,
        "rbi_reports": rbi_reports,
    }

    return results
