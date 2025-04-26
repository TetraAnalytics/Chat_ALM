import pandas as pd
from Instruments.Bond import Bond
from Instruments.Mortgage import Mortgage
from Instruments.DemandDeposit import DemandDeposit
from Instruments.InterestRateSwap import InterestRateSwap
from Analytics.CashflowCalculator import generate_cashflows_for_portfolio
from Analytics.PricingEngine import calculate_prices_for_portfolio
from Analytics.DurationCalculator import calculate_durations_for_portfolio
from Analytics.RateShockEngine import apply_parallel_rate_shocks
from Output.ExcelWriter import export_results_to_excel, export_rbi_reports_to_excel


def load_portfolio_from_excel(filepath, zero_curve=None, forward_curve=None):
    """
    Reads Excel input and returns a list of instrument objects.
    """
    df = pd.read_excel(filepath)
    instruments = []

    for _, row in df.iterrows():
        instrument_type = row['instrument_type']

        if instrument_type == 'Bond':
            instruments.append(Bond(
                ID=row['ID'],
                notional=row['notional'],
                coupon_rate=row['coupon_rate'],
                maturity_date=row['maturity_date'],
                issue_date=row['issue_date'],
                yield_rate=row['yield_rate'],
                frequency=int(row['frequency'])
            ))

        elif instrument_type == 'Mortgage':
            instruments.append(Mortgage(
                ID=row['ID'],
                notional=row['notional'],
                coupon_rate=row['coupon_rate'],
                maturity_date=row['maturity_date'],
                issue_date=row['issue_date'],
                yield_rate=row['yield_rate'],
                CPR=row.get('CPR', 0.0)
            ))

        elif instrument_type == 'DemandDeposit':
            instruments.append(DemandDeposit(
                ID=row['ID'],
                notional=row['notional'],
                maturity_date=row['maturity_date'],
                issue_date=row['issue_date'],
                yield_rate=row['yield_rate'],
                rate=row.get('rate', 0.00),
                decay_term_months=int(row.get('decay_term_months', 60)),
                frequency=int(row.get('frequency', 12))
            ))

        elif instrument_type == 'InterestRateSwap':
            instruments.append(InterestRateSwap(
                ID=row['ID'],
                notional=row['notional'],
                fixed_rate=row['coupon_rate'],
                float_spread=row.get('float_spread', 0.0),
                start_date=row['issue_date'],
                end_date=row['maturity_date'],
                yield_rate=row['yield_rate'],
                pay_fixed=row.get('pay_fixed', True),
                frequency=int(row.get('frequency', 4)),
                zero_curve=zero_curve,
                forward_curve=forward_curve
            ))

    return instruments


def run_alm(filepath, output_file, valuation_date, zero_curve=None, forward_curve=None):
    """
    Full ALM processing pipeline.
    """
    instruments = load_portfolio_from_excel(filepath, zero_curve, forward_curve)

    prices = calculate_prices_for_portfolio(instruments, valuation_date=valuation_date)
    durations = calculate_durations_for_portfolio(instruments, valuation_date=valuation_date)
    cashflows = generate_cashflows_for_portfolio(instruments)

    # Inside run_alm()
    shock_df = apply_parallel_rate_shocks(instruments, valuation_date=valuation_date)
    export_results_to_excel(output_file, prices, durations, cashflows, shock_df=shock_df)

    export_results_to_excel(output_file, prices, durations, cashflows)
    export_rbi_reports_to_excel("RBI_Regulatory_Reports.xlsx", cashflows, instruments, valuation_date)
