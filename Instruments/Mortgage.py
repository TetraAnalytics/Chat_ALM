import pandas as pd
from dateutil.relativedelta import relativedelta
from Instruments.BaseInstrument import BaseInstrument
import numpy as np
from datetime import datetime

class Mortgage(BaseInstrument):
    def __init__(self, ID, notional, coupon_rate, maturity_date, issue_date, yield_rate,
                 CPR=0.0, day_count="30/360", country=None):
        super().__init__(ID, notional, coupon_rate, maturity_date, issue_date, yield_rate, day_count, country)
        self.CPR = CPR

        if self.country == "India":
            self.day_count = "30/360"  # Used for home loan EMI schedules

    def generate_cashflows(self):
        issue = pd.to_datetime(self.issue_date)
        maturity = pd.to_datetime(self.maturity_date)
        months = (maturity.year - issue.year) * 12 + (maturity.month - issue.month)
        monthly_rate = self.coupon_rate / 12
        payment = np.pmt(monthly_rate, months, -self.notional)
        balance = self.notional
        rows = []

        for m in range(1, months + 1):
            interest = balance * monthly_rate
            principal = payment - interest
            prepay = (balance - principal) * (1 - (1 - self.CPR) ** (1 / 12))
            total_principal = principal + prepay
            balance -= total_principal
            rows.append({
                "payment_date": issue + relativedelta(months=m),
                "interest": interest,
                "principal": total_principal
            })
            if balance <= 0:
                break

        return pd.DataFrame(rows)

    def calculate_price(self, discount_curve=None, valuation_date=None):
        df = self.generate_cashflows()
        if valuation_date is None:
            valuation_date = pd.to_datetime(datetime.today().date())
        df['t'] = (df['payment_date'] - valuation_date).dt.days / 365
        df['df'] = 1 / (1 + self.yield_rate / 12) ** (12 * df['t'])
        df['pv'] = (df['interest'] + df['principal']) * df['df']
        return df['pv'].sum()

    def calculate_duration(self, valuation_date=None):
        df = self.generate_cashflows()
        if valuation_date is None:
            valuation_date = pd.to_datetime(datetime.today().date())
        df['t'] = (df['payment_date'] - valuation_date).dt.days / 365
        df['df'] = 1 / (1 + self.yield_rate / 12) ** (12 * df['t'])
        df['pv'] = (df['interest'] + df['principal']) * df['df']
        df['weighted_time'] = df['t'] * df['pv']
        macaulay = df['weighted_time'].sum() / df['pv'].sum()
        modified = macaulay / (1 + self.yield_rate / 12)
        return round(macaulay, 4), round(modified, 4)
