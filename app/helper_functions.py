def round_to_int(number: float):
    """
    Round the given number to the nearest integer unless
    the int is zero.
    """
    if float(number) < 1:
        return float(number)
    else:
        return round(float(number))