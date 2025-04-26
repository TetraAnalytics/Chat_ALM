# Analytics/YieldCurveBuilder.py

import pandas as pd
import numpy as np


def build_zero_forward_curve():
    """
    Returns a sample DataFrame with months, zero rates, and forward rates.
    Replace this with a bootstrap function in production.
    """
    months = np.arange(1, 121)
    zero_rates = 0.04 + 0.0002 * (months - 60)  # Example: upward slope
    forward_rates = zero_rates + 0.0005  # Forward > spot assumption

    df = pd.DataFrame({
        "Months": months,
        "Zero Rate": zero_rates,
        "Forward Rate": forward_rates
    })

    return df, df
