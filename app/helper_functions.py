import requests
from whois import whois
import ipaddress
import re
from typing import Tuple


def round_to_int(number: float):
    """
    Round the given number to the nearest integer unless
    the int is zero.
    """
    if float(number) < 1:
        return float(number)
    else:
        return round(float(number))


def is_valid_ip(value: str) -> bool:
    """Return True if value is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_hostname(value: str) -> bool:
    """Validate RFC 1123 hostname format (basic)."""
    if len(value) > 253:
        return False
    if value.endswith('.'):
        value = value[:-1]
    # Each label: 1-63 chars, alphanumeric or hyphen, not starting/ending with hyphen
    label_re = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
    return all(label_re.match(label) for label in value.split('.'))


def is_valid_hostname_or_ip(value: str) -> bool:
    return is_valid_ip(value) or is_valid_hostname(value)


def check_registrar(domain: str) -> Tuple[str, str]:
    """
    Query WHOIS records for the given domain safely.

    Returns a tuple (registrar, expiration) or ("UNKNOWN", "UNKNOWN") on failure.
    """
    try:
        if not is_valid_hostname(domain):
            return 'UNKNOWN', 'UNKNOWN'
        query = whois(domain)
        if query:
            registrar = getattr(query, 'registrar', None) or 'UNKNOWN'
            expiration = str(getattr(query, 'expiration_date', 'UNKNOWN'))
            return registrar, expiration
    except Exception:
        # Do not leak internal errors; return generic unknowns
        pass
    return 'UNKNOWN', 'UNKNOWN'


def get_country_from_ip(ip_address: str) -> str:
    """
    Fetches the country code for a given IP address from ipinfo.io.
    Applies input validation and network timeouts.
    """
    if not is_valid_ip(ip_address):
        return 'Unknown'
    url = f'https://ipinfo.io/{ip_address}/country'
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException:
        return 'Unknown'



