import pandas as pd
from dateutil.relativedelta import relativedelta
from Instruments.BaseInstrument import BaseInstrument
from datetime import datetime


class Bond(BaseInstrument):
    def __init__(self, ID, notional, coupon_rate, maturity_date, issue_date, yield_rate,
                 frequency=2, day_count="30/360", country=None, instrument_subtype="Government"):
        super().__init__(ID, notional, coupon_rate, maturity_date, issue_date, yield_rate, day_count, country)
        self.frequency = frequency
        self.instrument_subtype = instrument_subtype

        if self.country == "India":
            if self.instrument_subtype == "Government":
                self.day_count = "Actual/Actual"
            elif self.instrument_subtype == "Corporate":
                self.day_count = "30/360"  # or "Actual/365" if needed

    @classmethod
    def from_dataframe_row(cls, row):
        return cls(
            ID=row["ID"],
            notional=row["Notional"],
            coupon_rate=row.get("CouponRate", 0.0),
            maturity_date=row["MaturityDate"],
            issue_date=row["IssueDate"],
            yield_rate=row.get("YieldRate", 0.0),
            frequency=row.get("Frequency", 2),
            day_count=row.get("DayCount", "30/360"),
            country=row.get("Country", None),
            instrument_subtype=row.get("InstrumentSubtype", "Government")
        )

    def generate_cashflows(self):
        issue = pd.to_datetime(self.issue_date)
        maturity = pd.to_datetime(self.maturity_date)
        periods = int((maturity.year - issue.year) * self.frequency + (maturity.month - issue.month) / (12 / self.frequency))
        payment = self.notional * self.coupon_rate / self.frequency

        return pd.DataFrame({
            "payment_date": [issue + relativedelta(months=int(i * 12 / self.frequency)) for i in range(1, periods + 1)],
            "interest": [payment] * periods,
            "principal": [0] * (periods - 1) + [self.notional]
        })

    def calculate_price(self, discount_curve=None, valuation_date=None):
        df = self.generate_cashflows()
        if valuation_date is None:
            valuation_date = pd.to_datetime(datetime.today().date())

        df['t'] = (df['payment_date'] - valuation_date).dt.days / 365
        df['df'] = 1 / (1 + self.yield_rate / self.frequency) ** (self.frequency * df['t'])
        df['pv'] = (df['interest'] + df['principal']) * df['df']
        return df['pv'].sum()

    def calculate_duration(self, valuation_date=None):
        df = self.generate_cashflows()
        if valuation_date is None:
            valuation_date = pd.to_datetime(datetime.today().date())

        df['t'] = (df['payment_date'] - valuation_date).dt.days / 365
        df['df'] = 1 / (1 + self.yield_rate / self.frequency) ** (self.frequency * df['t'])
        df['pv'] = (df['interest'] + df['principal']) * df['df']
        df['weighted_time'] = df['t'] * df['pv']

        macaulay = df['weighted_time'].sum() / df['pv'].sum()
        modified = macaulay / (1 + self.yield_rate / self.frequency)
        return round(macaulay, 4), round(modified, 4)
