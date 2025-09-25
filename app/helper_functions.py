import dns.resolver
import requests
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
    if query: # if domain exists
        registrar = query.registrar
        expiration = str(query.expiration_date)
        return registrar, expiration
    else:
        return 'UNKNOWN', 'UNKNOWN'

def get_country_from_ip(ip_address: str):
    """
    Fetches the country code for a given IP address from ipinfo.io.
    """
    url = f'https://ipinfo.io/{ip_address}/country'
    try:
        response = requests.get(url)
        # This will raise an exception if the request was not successful (e.g., 404 Not Found)
        response.raise_for_status()
        # .strip() removes any leading/trailing whitespace, like newlines
        country_code = response.text.strip()
        return country_code
    except requests.exceptions.RequestException as e:
        return 'Unknown'



