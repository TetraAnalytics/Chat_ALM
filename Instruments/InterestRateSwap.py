import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Instruments.BaseInstrument import BaseInstrument

class InterestRateSwap(BaseInstrument):
    def __init__(self, ID, notional, fixed_rate, float_spread, start_date, end_date,
                 yield_rate, pay_fixed=True, frequency=4, zero_curve=None, forward_curve=None,
                 fixed_leg_day_count="30/360", float_leg_day_count="Actual/360", country=None):
        super().__init__(ID, notional, fixed_rate, end_date, start_date, yield_rate, fixed_leg_day_count, country)
        self.float_spread = float_spread
        self.pay_fixed = pay_fixed
        self.frequency = frequency
        self.zero_curve = zero_curve
        self.forward_curve = forward_curve
        self.fixed_leg_day_count = fixed_leg_day_count
        self.float_leg_day_count = float_leg_day_count

        if self.country == "India":
            self.fixed_leg_day_count = "30/360"
            self.float_leg_day_count = "Actual/360"

    def _interpolate_curve(self, months, curve_df, column):
        curve_months = curve_df['Months'].values
        curve_values = curve_df[column].values
        return np.interp(months, curve_months, curve_values)

    def generate_cashflows(self, valuation_date=None):
        if valuation_date is None:
            valuation_date = pd.to_datetime(datetime.today().date())

        start = pd.to_datetime(self.issue_date)
        end = pd.to_datetime(self.maturity_date)
        delta = relativedelta(months=12 // self.frequency)

        payment_dates, t_months = [], []
        current = start
        while current < end:
            current += delta
            if current > end:
                break
            payment_dates.append(current)
            t_months.append((current.year - valuation_date.year) * 12 + current.month - valuation_date.month)

        fixed_leg = [self.notional * self.coupon_rate / self.frequency] * len(payment_dates)
        float_rates = self._interpolate_curve(t_months, self.forward_curve, 'Forward Rate')
        float_leg = [self.notional * (r + self.float_spread) / self.frequency for r in float_rates]

        net_cashflows = [(float_leg[i] - fixed_leg[i]) if self.pay_fixed else (fixed_leg[i] - float_leg[i])
                         for i in range(len(payment_dates))]

        return pd.DataFrame({
            'payment_date': payment_dates,
            'fixed_leg': fixed_leg,
            'float_leg': float_leg,
            'net_cashflow': net_cashflows,
            'months_forward': t_months
        })

    def calculate_price(self, discount_curve=None, valuation_date=None):
        df = self.generate_cashflows(valuation_date)
        months = df['months_forward'].values
        zero_rates = self._interpolate_curve(months, self.zero_curve, 'Zero Rate')
        df['discount_factor'] = 1 / (1 + zero_rates / self.frequency) ** (self.frequency * (months / 12))
        df['pv'] = df['net_cashflow'] * df['discount_factor']
        return df['pv'].sum()

    def calculate_duration(self, valuation_date=None):
        df = self.generate_cashflows(valuation_date)
        months = df['months_forward'].values
        zero_rates = self._interpolate_curve(months, self.zero_curve, 'Zero Rate')
        df['discount_factor'] = 1 / (1 + zero_rates / self.frequency) ** (self.frequency * (months / 12))
        df['pv'] = df['net_cashflow'] * df['discount_factor']
        df['t_years'] = months / 12
        df['weighted_time'] = df['t_years'] * df['pv']
        macaulay = df['weighted_time'].sum() / df['pv'].sum()
        modified = macaulay / (1 + np.mean(zero_rates) / self.frequency)
        return round(macaulay, 4), round(modified, 4)
