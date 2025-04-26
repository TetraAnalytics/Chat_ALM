from concurrent.futures import ProcessPoolExecutor


def _price_instrument(args):
    instrument, valuation_date = args
    return instrument.ID, instrument.calculate_price(valuation_date=valuation_date)


def calculate_prices_for_portfolio(instruments, valuation_date=None):
    with ProcessPoolExecutor() as executor:
        results = executor.map(_price_instrument, [(inst, valuation_date) for inst in instruments])
    return {ID: round(price, 4) for ID, price in results}
