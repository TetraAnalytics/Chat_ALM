# Mortgage.py
import pandas as pd
from dateutil.relativedelta import relativedelta
from Instruments.BaseInstrument import BaseInstrument
import numpy_financial as npf
from datetime import datetime


class Mortgage(BaseInstrument):
    def __init__(self, ID, notional, coupon_rate, maturity_date, issue_date, yield_rate,
                 term_months=360, day_count="30/360", country=None):
        super().__init__(ID, notional, coupon_rate, maturity_date, issue_date, yield_rate, day_count, country)
        self.term_months = term_months

        if self.country == "India":
            self.day_count = "30/360"  # rbi standard for mortgages

    @classmethod
    def from_dataframe_row(cls, row):
        """
        Create a Mortgage object from a single row of a DataFrame.
        Expected columns: ID, NOTIONAL, COUPON, MATURITY_DATE, ISSUE_DATE, YIELD, TERM_MONTHS, DAY_COUNT, COUNTRY
        """
        return cls(
            ID=row["ID"],
            notional=row["NOTIONAL"],
            coupon_rate=row["COUPON"],
            maturity_date=row["MATURITY_DATE"],
            issue_date=row["ISSUE_DATE"],
            yield_rate=row["YIELD"],
            term_months=int(row.get("TERM_MONTHS", 360)),  # Default 360 months if not provided
            day_count=row.get("DAY_COUNT", "30/360"),
            country=row.get("COUNTRY", None)
        )

    def generate_cashflows(self):
        issue = pd.to_datetime(self.issue_date)
        payment_dates = [issue + relativedelta(months=i) for i in range(1, self.term_months + 1)]
        monthly_rate = self.coupon_rate / 12
        pmt = npf.pmt(rate=monthly_rate, nper=self.term_months, pv=-self.notional)

        balance = self.notional
        interest_payments = []
        principal_payments = []

        for _ in range(self.term_months):
            interest_payment = balance * monthly_rate
            principal_payment = pmt - interest_payment
            balance -= principal_payment

            interest_payments.append(interest_payment)
            principal_payments.append(principal_payment)

        return pd.DataFrame({
            "payment_date": payment_dates,
            "interest": interest_payments,
            "principal": principal_payments
        })

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
