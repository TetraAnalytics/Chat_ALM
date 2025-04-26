# rbi/reporting.py

def generate_rbi_reports(results_dict):
    """
    Generate RBI required regulatory reports based on ALM results.

    Args:
        results_dict (dict): Dictionary containing daily cashflows, monthly cashflows, rate shock results.

    Returns:
        dict: Dictionary of RBI regulatory report DataFrames.
    """
    reports = {}

    # Liquidity Gap Analysis
    daily_cf = results_dict.get("daily_agg")
    if daily_cf is not None:
        if 'interest' in daily_cf.columns and 'principal' in daily_cf.columns:
            daily_cf = daily_cf.copy()
            daily_cf['NetCashflow'] = daily_cf['interest'] + daily_cf['principal']
            daily_cf = daily_cf.groupby('payment_date')['NetCashflow'].sum().reset_index()
            daily_cf['CumulativeCashflow'] = daily_cf['NetCashflow'].cumsum()
            liquidity_profile = daily_cf[['payment_date', 'CumulativeCashflow']]
            liquidity_profile.columns = ['Date', 'Cumulative Cashflow']
            reports["Liquidity Gap Profile"] = liquidity_profile

    # Interest Rate Sensitivity Report
    shocks_df = results_dict.get("rate_shock_results")
    if shocks_df is not None:
        expected_cols = ['Shock (bps)', 'Portfolio Market Value', 'Change in Market Value']
        if all(col in shocks_df.columns for col in expected_cols):
            sensitivity = shocks_df[expected_cols]
            reports["Interest Rate Sensitivity"] = sensitivity
        else:
            print("⚠️ Skipping Interest Rate Sensitivity Report: Missing expected columns.")

    return reports
