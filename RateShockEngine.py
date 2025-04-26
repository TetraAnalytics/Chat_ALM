# Analytics/RateShockEngine.py

import pandas as pd


def apply_parallel_rate_shocks(portfolio):
    """
    Apply +100bps and -100bps parallel rate shocks to each instrument and calculate new market values.
    """
    shocks = [-200, -100, 0, 100, 200]  # Shock scenarios in basis points
    results = []

    for shock in shocks:
        shock_multiplier = 1 + (shock / 10000)  # E.g., +100bps = 1.01, -100bps = 0.99

        total_market_value = 0.0

        for inst in portfolio:
            try:
                shocked_yield = inst.yield_rate * shock_multiplier
                inst_copy = type(inst)(**inst.__dict__)  # Deep copy to avoid changing original
                inst_copy.yield_rate = shocked_yield

                price = inst_copy.calculate_price()

                total_market_value += price

            except Exception as e:
                print(f"⚠️ Error processing shock for instrument {inst.ID}: {e}")

        results.append({
            "Shock (bps)": shock,
            "Portfolio Market Value": total_market_value,
        })

    df = pd.DataFrame(results)

    # Add the "Change in Market Value" column
    base_value = df.loc[df['Shock (bps)'] == 0, 'Portfolio Market Value'].values[0]
    df["Change in Market Value"] = df["Portfolio Market Value"] - base_value

    return df
