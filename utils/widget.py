import math


def millify(n):
    """
    A helper function to convert large numbers to human-readable numbers
    :param n: the large number
    :return: a human readable number string
    """
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
    if -1 <= n <= 1:
        return percentify(n)
    return millify(n)
