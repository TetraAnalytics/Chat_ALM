import pandas as pd
from dateutil.relativedelta import relativedelta
from Instruments.BaseInstrument import BaseInstrument
from datetime import datetime


class DemandDeposit(BaseInstrument):
    def __init__(self, ID, notional, maturity_date, issue_date, yield_rate,
                 rate=0.00, decay_term_months=60, frequency=12, day_count="30/360", country=None):
        super().__init__(ID, notional, rate, maturity_date, issue_date, yield_rate, day_count, country)
        self.rate = rate
        self.decay_term_months = decay_term_months
        self.frequency = frequency

        if self.country == "India":
            self.day_count = "30/360"  # Default for local deposits

    @classmethod
    def from_dataframe_row(cls, row):
        return cls(
            ID=row["ID"],
            notional=row["Notional"],
            withdrawal_rate=row.get("WithdrawalRate", 0.0),
            day_count=row.get("DayCount", "30/360"),
            country=row.get("Country", None)
        )

    def generate_cashflows(self):
        start_date = pd.to_datetime(self.issue_date)
        period = 12 // self.frequency
        payment_dates, interest_payments, principal_payments = [], [], []

        for m in range(1, self.decay_term_months + 1):
            date = start_date + relativedelta(months=m)
            if m % period == 0:
                remaining_balance = self.notional * (1 - (m / self.decay_term_months))
                interest = remaining_balance * self.rate / self.frequency
                principal = self.notional / self.decay_term_months
                payment_dates.append(date)
                interest_payments.append(interest)
                principal_payments.append(principal)

        return pd.DataFrame({
            'payment_date': payment_dates,
            'interest': interest_payments,
            'principal': principal_payments
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
