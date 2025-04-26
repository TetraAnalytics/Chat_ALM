from abc import ABC, abstractmethod

class BaseInstrument(ABC):
    def __init__(self, ID, notional, coupon_rate, maturity_date, issue_date, yield_rate, day_count="30/360", country=None):
        self.ID = ID
        self.notional = notional
        self.coupon_rate = coupon_rate
        self.maturity_date = maturity_date
        self.issue_date = issue_date
        self.yield_rate = yield_rate
        self.country = country
        self.day_count = self._assign_day_count(day_count)

    def _assign_day_count(self, user_day_count):
        if self.country == "India":
            return "30/360"  # default override logic handled in subclasses
        return user_day_count

    @abstractmethod
    def generate_cashflows(self):
        pass

    @abstractmethod
    def calculate_price(self, discount_curve=None, valuation_date=None):
        pass

    @abstractmethod
    def calculate_duration(self, valuation_date=None):
        pass
