import dns.resolver
from whois import whois

def round_to_int(number: float):
    """
    Round the given number to the nearest integer unless
    the int is zero.
    """
    if float(number) < 1:
        return float(number)
    else:
        return round(float(number))

def check_registrar(domain):
    """
    Query WHOIS records for the given domain

    Usage:
        result, registrar, expiration = check_registrar(domain)
    """
    query = whois(domain)
    if query: # If domain exists
        registrar = query.registrar
        expiration = str(query.expiration_date)
        if registrar.lower().startswith("cloudflare"):
            return 'PASSED', registrar, expiration
        else:
            return 'FAILED', registrar, expiration
    else:
        return 'ERROR', 'UNKNOWN', 'UNKNOWN'