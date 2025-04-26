def generate_cashflows_for_portfolio(instruments):
    """
    Generate a dictionary of DataFrames, each containing the cash flows of an instrument.
    """
    cashflows = {}
    for inst in instruments:
        df = inst.generate_cashflows()
        cashflows[inst.ID] = df
    return cashflows
