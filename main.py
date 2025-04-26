# main.py

import pandas as pd
from Instruments.Bond import Bond
from Instruments.Mortgage import Mortgage
from Instruments.InterestRateSwap import InterestRateSwap
from Instruments.DemandDeposit import DemandDeposit
from Analytics.CashflowCalculator import generate_cashflows_for_portfolio
from Analytics.RateShockEngine import apply_parallel_rate_shocks
from Analytics.AggregatedCashflows import (
    aggregate_daily_cashflows_by_type,
    aggregate_monthly_cashflows_by_type
)
from rbi.reporting import generate_rbi_reports
from Output.ExcelWriter import export_results_to_excel


def load_portfolio_from_excel(file_path):
    """
    Load portfolio instruments from an Excel file.
    """
    df = pd.read_excel(file_path)
    portfolio = []

    instrument_map = {
        "Bond": Bond,
        "Mortgage": Mortgage,
        "InterestRateSwap": InterestRateSwap,
        "DemandDeposit": DemandDeposit,
    }

    for _, row in df.iterrows():
        instrument_type = row.get("InstrumentType")
        cls = instrument_map.get(instrument_type)
        if cls:
            portfolio.append(cls.from_dataframe_row(row))

    return portfolio


def price_and_duration(portfolio, valuation_date=None):
    """
    Calculate price and duration for each instrument.
    """
    if valuation_date is None:
        valuation_date = pd.Timestamp.today()

    pricing_data = []

    for instrument in portfolio:
        try:
            price = instrument.calculate_price(valuation_date=valuation_date)
            macaulay, modified = instrument.calculate_duration(valuation_date=valuation_date)

            pricing_data.append({
                "ID": instrument.ID,
                "Instrument Type": instrument.__class__.__name__,
                "Price": price,
                "Macaulay Duration": macaulay,
                "Modified Duration": modified
            })

        except Exception as e:
            print(f"Error calculating price or duration for {instrument.ID}: {e}")

    return pd.DataFrame(pricing_data)


def run_alm(portfolio, valuation_date=None):
    """
    Perform full ALM analysis for a portfolio.
    """
    if valuation_date is None:
        valuation_date = pd.Timestamp.today()

    cashflows = generate_cashflows_for_portfolio(portfolio)
    instrument_map = {inst.ID: type(inst).__name__ for inst in portfolio}
    pricing_df = price_and_duration(portfolio, valuation_date)
    shock_results = apply_parallel_rate_shocks(portfolio)
    daily_agg = aggregate_daily_cashflows_by_type(cashflows, instrument_map)
    monthly_agg = aggregate_monthly_cashflows_by_type(cashflows, instrument_map)

    # Build prices and durations dicts
    prices = {row['ID']: row['Price'] for _, row in pricing_df.iterrows()}
    durations = {row['ID']: {
        "Macaulay": row['Macaulay Duration'],
        "Modified": row['Modified Duration']
    } for _, row in pricing_df.iterrows()}

    rbi_reports = generate_rbi_reports({
        "daily_agg": daily_agg,
        "monthly_agg": monthly_agg,
        "rate_shock_results": shock_results
    })

    results = {
        "cashflows": cashflows,
        "pricing": pricing_df,
        "daily_agg": daily_agg,
        "monthly_agg": monthly_agg,
        "rate_shock_results": shock_results,
        "rbi_reports": rbi_reports
    }

    output_file = "/tmp/ALM_Results.xlsx"
    export_results_to_excel(
        filepath=output_file,
        prices=prices,
        durations=durations,
        cashflows_dict=cashflows,
        daily_agg_df=daily_agg,
        monthly_agg_df=monthly_agg,
        shock_df=shock_results
    )

    return results
