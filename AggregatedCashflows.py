# Analytics/AggregatedCashflows.py

import pandas as pd


def aggregate_daily_cashflows_by_type(cashflows_dict, instrument_map):
    """
    Aggregate daily cash flows by instrument_type.

    Parameters:
        cashflows_dict (dict): {ID: DataFrame with 'payment_date', 'interest', 'principal'}
        instrument_map (dict): {ID: instrument_type}

    Returns:
        DataFrame: Daily totals of interest, principal by instrument_type
    """
    all_rows = []

    for ID, df in cashflows_dict.items():
        df = df.copy()
        df['instrument_type'] = instrument_map.get(ID, "Unknown")
        df['ID'] = ID
        df['payment_date'] = pd.to_datetime(df['payment_date'])
        all_rows.append(df)

    combined_df = pd.concat(all_rows)
    grouped = combined_df.groupby(['payment_date', 'instrument_type'])[['interest', 'principal']].sum().reset_index()
    return grouped


def aggregate_monthly_cashflows_by_type(cashflows_dict, instrument_map):
    """
    Aggregate monthly cash flows by instrument_type.

    Parameters:
        cashflows_dict (dict): {ID: DataFrame with 'payment_date', 'interest', 'principal'}
        instrument_map (dict): {ID: instrument_type}

    Returns:
        DataFrame: Monthly totals of interest, principal by instrument_type
    """
    all_rows = []

    for ID, df in cashflows_dict.items():
        df = df.copy()
        df['instrument_type'] = instrument_map.get(ID, "Unknown")
        df['ID'] = ID
        df['payment_date'] = pd.to_datetime(df['payment_date'])
        df['Month'] = df['payment_date'].dt.to_period("M").dt.to_timestamp()
        all_rows.append(df)

    combined_df = pd.concat(all_rows)
    grouped = combined_df.groupby(['Month', 'instrument_type'])[['interest', 'principal']].sum().reset_index()
    return grouped
