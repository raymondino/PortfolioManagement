import datetime
from scipy import optimize


def generate_month_ranges(year_list):
    """
    generate a list of tuple of two dates, indicating the starting and ending date of a month
    :param year_list: a list of int year
    :return: a list of month range dates
    """
    if year_list is None or len(year_list) == 0:
        return []
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    start_end_dates_for_a_month = []
    for year in year_list:
        for i in range(0, 12):
            if is_leap_year(year) and months[i] == 2:
                start_end_dates_for_a_month.append((f"{year}-2-1", f"{year}-2-29"))
            else:
                start_end_dates_for_a_month.append((f"{year}-{months[i]}-1", f"{year}-{months[i]}-{days[i]}"))
    return start_end_dates_for_a_month


def is_leap_year(year):
    return (year % 4 == 0 and year % 100 == 0 and year % 400 == 0) or (year % 4 == 0)


# def xnpv(rate, cashflows):
#     """
#     source: https://stackoverflow.com/questions/46668172/calculating-xirr-in-python
#     a helper function to calculate the average return rate for fixed_investment.
#     :param rate: rate is the parameter to be solved.
#     :param cashflows: a list of tuples (datetime, money). money is negative int if invested, or positive int if vested.
#     :return:
#     """
#     return sum([cf / (1 + rate) ** ((t - cashflows[0][0]).days / 365.0) for (t, cf) in cashflows])
#
#
# def xirr(cashflows, guess=0.2):
#     """
#     source: https://stackoverflow.com/questions/46668172/calculating-xirr-in-python
#     a helper function to calculate the average return rate for fixed_investment.
#     :param cashflows: a list of tuples (datetime, money). money is negative int if invested, or positive int if vested.
#     :param guess: a value used to calculate XIRR. Read more on XIRR if want to know details of this guess.
#     :return: the XIRR rate (can be used as the average return of the fixed_investment strategy.
#     """
#     try:
#         return optimize.newton(lambda r: xnpv(r, cashflows), guess)
#     except:
#         print('Calc Wrong')


def secant_method(tol, f, x0):
    """
    https://github.com/peliot/XIRR-and-XNPV/blob/master/financial.py
    Solve for x where f(x)=0, given starting x0 and tolerance.

    Arguments
    ----------
    tol: tolerance as percentage of final result. If two subsequent x values are with tol percent, the function will return.
    f: a function of a single variable
    x0: a starting value of x to begin the solver
    Notes
    ------
    The secant method for finding the zero value of a function uses the following formula to find subsequent values of x.

    x(n+1) = x(n) - f(x(n))*(x(n)-x(n-1))/(f(x(n))-f(x(n-1)))

    Warning
    --------
    This implementation is simple and does not handle cases where there is no solution. Users requiring a more robust version should use scipy package optimize.newton.
    """

    x1 = x0 * 1.1
    while (abs(x1 - x0) / abs(x1) > tol):
        x0, x1 = x1, x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    return x1


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