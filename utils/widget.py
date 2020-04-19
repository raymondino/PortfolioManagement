import math


def millify(n):
    """
    A helper function to convert large numbers to human-readable numbers
    :param n: the large number
    :return: a human readable number string
    """
    if math.isnan(n):
        return n
    millnames = ['', ' K', ' M', ' B', ' T']
    n = float(n)
    millidx = max(0,min(len(millnames)-1,int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])


def percentify(n):
    """
    A helper function to convert a number to percentage string
    :param n: a number
    :return: a percentage string
    """
    return '{:.2f}{}'.format(n*100, '%')


def decimalize(n):
    """
    A helper function to reserve 2 decimal number
    :param n: a number
    :return: a 2 decimal number string
    """
    return '{:.2f}'.format(n)


def mix_number(n):
    """
    A helper function to return either a percentage or a human readable number
    :param n: a number
    :return: a percentage or a human readable number
    """
    if -10 <= n <= 10:
        return percentify(n)
    return millify(n)

def xnpv(rate, cashflows):
    """
    https://github.com/peliot/XIRR-and-XNPV/blob/master/financial.py
    Calculate the net present value of a series of cashflows at irregular intervals.
    Arguments
    ---------
    * rate: the discount rate to be applied to the cash flows
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    Returns
    -------
    * returns a single value which is the NPV of the given cash flows.
    Notes
    ---------------
    * The Net Present Value is the sum of each of cash flows discounted back to the date of the first cash flow. The discounted value of a given cash flow is A/(1+r)**(t-t0), where A is the amount, r is the discout rate, and (t-t0) is the time in years from the date of the first cash flow in the series (t0) to the date of the cash flow being added to the sum (t).
    * This function is equivalent to the Microsoft Excel function of the same name.
    """

    chron_order = sorted(cashflows, key=lambda x: x[0])
    t0 = chron_order[0][0]  # t0 is the date of the first cash flow
    return sum([cf / (1 + rate) ** ((t - t0).days / 365.0) for (t, cf) in chron_order])


def xirr(cashflows, guess=0.05):
    """
    https://github.com/peliot/XIRR-and-XNPV/blob/master/financial.py
    Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.
    Arguments
    ---------
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    * guess (optional, default = 0.1): a guess at the solution to be used as a starting point for the numerical solution.
    Returns
    --------
    * Returns the IRR as a single value
    Notes
    ----------------
    * The Internal Rate of Return (IRR) is the discount rate at which the Net Present Value (NPV) of a series of cash flows is equal to zero. The NPV of the series of cash flows is determined using the xnpv function in this module. The discount rate at which NPV equals zero is found using the secant method of numerical solution.
    * This function is equivalent to the Microsoft Excel function of the same name.
    * For users that do not have the scipy module installed, there is an alternate version (commented out) that uses the secant_method function defined in the module rather than the scipy.optimize module's numerical solver. Both use the same method of calculation so there should be no difference in performance, but the secant_method function does not fail gracefully in cases where there is no solution, so the scipy.optimize.newton version is preferred.
    """

    # return secant_method(0.0001,lambda r: xnpv(r,cashflows),guess)
    return optimize.newton(lambda r: xnpv(r, cashflows), guess)
