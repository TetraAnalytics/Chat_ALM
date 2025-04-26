from Instruments.BaseInstrument import BaseInstrument
import pandas as pd


class InterestRateSwap(BaseInstrument):
    def __init__(self, ID, notional, start_date, end_date, fixed_rate, float_spread,
                 yield_rate, frequency=2, day_count="30/360", country=None):
        super().__init__(ID, notional, fixed_rate, end_date, start_date, yield_rate, day_count, country)
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.fixed_rate = fixed_rate
        self.float_spread = float_spread
        self.frequency = frequency
