# RBI/Reporting.py

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
        daily_cf['cumulative_cashflow'] = daily_cf['total_cashflow'].cumsum()
        liquidity_profile = daily_cf[['payment_date', 'cumulative_cashflow']]
        liquidity_profile.columns = ['Date', 'Cumulative Cashflow']
        reports["Liquidity Gap Profile"] = liquidity_profile

    # Interest Rate Sensitivity Report
    shocks_df = results_dict.get("rate_shock_results")
    if shocks_df is not None:
        sensitivity = shocks_df[['Shock (bps)', 'Portfolio Market Value', 'Change in Market Value']]
        reports["Interest Rate Sensitivity"] = sensitivity

    return reports
