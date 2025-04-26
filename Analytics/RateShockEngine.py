import pandas as pd

def apply_parallel_rate_shocks(instruments, shock_bps=[-200, -100, 0, 100, 200], valuation_date=None):
    """
    Apply interest rate shocks to all instruments and return a pivot table.
    """
    records = []

    for shock in shock_bps:
        total_value = 0
        for inst in instruments:
            inst_copy = inst.__class__(**inst.__dict__)
            inst_copy.yield_rate += shock / 10000
            price = inst_copy.calculate_price(valuation_date=valuation_date)
            records.append({
                "ID": inst.ID,
                "Shock (bps)": shock,
                "Price": round(price, 2)
            })
            total_value += price

        records.append({
            "ID": "PORTFOLIO_TOTAL",
            "Shock (bps)": shock,
            "Price": round(total_value, 2)
        })

    return pd.DataFrame(records)
