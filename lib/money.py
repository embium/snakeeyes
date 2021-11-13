def cents_to_dollars(cents):
    """
    Convert cents to dollars.

    :param cents: Amount in cents
    :type cents: int
    :return: float
    """
    if not cents:
        return 0

    return round(cents / 100.0, 2)


def dollars_to_cents(dollars):
    """
    Convert dollars to cents.

    :param dollars: Amount in dollars
    :type dollars: float
    :return: int
    """
    if not dollars:
        return 0

    return int(dollars * 100)
