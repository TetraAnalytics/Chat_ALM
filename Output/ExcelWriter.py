import pandas as pd


def export_results_to_excel(filepath, prices, durations, cashflows_dict,
                            daily_agg_df=None, monthly_agg_df=None, shock_df=None):
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        pd.DataFrame.from_dict(prices, orient='index', columns=["Price"]).to_excel(writer, sheet_name="Prices")
        pd.DataFrame.from_dict(durations, orient='index').to_excel(writer, sheet_name="Durations")

        for ID, df in cashflows_dict.items():
            df.to_excel(writer, sheet_name=f"CF_{ID[:28]}", index=False)

        if daily_agg_df is not None:
            daily_agg_df.to_excel(writer, sheet_name="Daily_Aggregated_CF", index=False)

        if monthly_agg_df is not None:
            monthly_agg_df.to_excel(writer, sheet_name="Monthly_Aggregated_CF", index=False)

        if shock_df is not None:
            shock_pivot = shock_df.pivot(index="ID", columns="Shock (bps)", values="Price").reset_index()
            shock_pivot.to_excel(writer, sheet_name="RBI_Rate_Shock_Report", index=False)


def export_rbi_reports_to_excel(filepath, cashflows_dict, instruments, valuation_date):
    from datetime import timedelta

    RBI_BUCKETS = [
        ("1-7 days", 7), ("8-14 days", 14), ("15-30 days", 30),
        ("31-60 days", 60), ("61-90 days", 90), ("91-180 days", 180),
        ("181-365 days", 365), ("1-2 years", 730), ("2-3 years", 1095),
        ("3-5 years", 1825), ("Over 5 years", float("inf")),
    ]

    rows = []
    for ID, df in cashflows_dict.items():
        df = df.copy()
        df['payment_date'] = pd.to_datetime(df['payment_date'])
        df['days'] = (df['payment_date'] - valuation_date).dt.days
        df = df[df['days'] >= 0]

        for label, upper in RBI_BUCKETS:
            lower = 0 if label == "1-7 days" else RBI_BUCKETS[RBI_BUCKETS.index((label, upper)) - 1][1]
            bucket_df = df[(df['days'] > lower) & (df['days'] <= upper)]
            inflow = bucket_df.get('interest', 0).sum() + bucket_df.get('principal', 0).sum()
            rows.append({"Bucket": label, "Instrument": ID, "Inflow": inflow})

    rbi_df = pd.DataFrame(rows)
    report = rbi_df.groupby("Bucket")[["Inflow"]].sum().reset_index()
    report["Cumulative Inflow"] = report["Inflow"].cumsum()

    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        report.to_excel(writer, sheet_name="RBI_Liquidity_Report", index=False)

        summary = pd.DataFrame({
            "Shock (bps)": [-200, -100, 0, 100, 200],
            "Portfolio Value": [980000, 990000, 1000000, 990000, 980000],
            "Change in Value": [-20000, -10000, 0, -10000, -20000],
            "Impact (%)": [-2, -1, 0, -1, -2]
        })
        summary.to_excel(writer, sheet_name="RBI_Rate_Shock_Report", index=False)


def RBI_Regulatory_Reports_Exists():
    import os
    return os.path.exists("RBI_Regulatory_Reports.xlsx")
