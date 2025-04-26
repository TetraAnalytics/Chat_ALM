from concurrent.futures import ProcessPoolExecutor


def _duration_instrument(args):
    instrument, valuation_date = args
    mac, mod = instrument.calculate_duration(valuation_date=valuation_date)
    return instrument.ID, {"macaulay_duration": mac, "modified_duration": mod}


def calculate_durations_for_portfolio(instruments, valuation_date=None):
    with ProcessPoolExecutor() as executor:
        results = executor.map(_duration_instrument, [(inst, valuation_date) for inst in instruments])
    return {ID: durations for ID, durations in results}
