#!/usr/bin/env python3
"""
currency_api

A tiny library and CLI for converting currency amounts using the public
Frankfurter API (https://www.frankfurter.app/).

It provides:
- Validation helpers for ISO-like 3-letter currency codes.
- Amount parsing using Decimal with non-negative constraints.
- A convert() function that calls the API, handles errors robustly, and
  returns the converted amount as Decimal.
- A command-line interface that prints a human-readable conversion line.

Implementation notes:
- Decimal precision is set high (28) and amounts are normalized to 6 decimal
  places using HALF_UP rounding to mirror common currency behaviour.
- Network and API errors are mapped to IOError or ValueError with readable
  messages.
"""
import sys
import re
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext
from urllib import request, error

API_ENDPOINT = "https://api.frankfurter.app/latest"

# Increase precision to be safe with currencies
getcontext().prec = 28

CODE_RE = re.compile(r"^[A-Za-z]{3}$")


def _normalize_decimal(d: Decimal) -> str:
    """Return a normalized string for a Decimal amount.

    The value is rounded to 6 fractional digits using HALF_UP and then any
    trailing zeros and the trailing decimal point are stripped. The result is
    suitable for inclusion in URLs and for compact display.

    Args:
        d: Decimal amount to normalize.

    Returns:
        A string representation like "1.23", "0.000001", or "10".

    Examples:
        _normalize_decimal(Decimal('1.2300004')) -> '1.23'
        _normalize_decimal(Decimal('10.000000')) -> '10'
    """
    # Round to 6 decimal places like Java setScale(6, HALF_UP) and strip trailing zeros
    q = Decimal("0.000001")
    d = d.quantize(q, rounding=ROUND_HALF_UP)
    s = format(d, 'f')  # fixed-point decimal string
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s


def validate_currency_code(code: str) -> None:
    """Validate that a currency code is a 3-letter alphabetic string.

    The check is case-insensitive. On failure, a ValueError is raised.

    Args:
        code: Currency code, e.g. "USD", "eur".

    Raises:
        ValueError: If code is None or does not match [A-Za-z]{3}.
    """
    if code is None or not CODE_RE.match(code):
        raise ValueError(f"Invalid currency code: {code}")


def parse_amount(amount_str: str) -> Decimal:
    """Parse a non-negative amount from a string into Decimal.

    Args:
        amount_str: Numeric string to parse (e.g. "123", "0.10").

    Returns:
        Decimal: Parsed amount.

    Raises:
        ValueError: If the string is not a valid number or is negative.
    """
    try:
        d = Decimal(amount_str)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid amount: {amount_str}")
    if d < 0:
        raise ValueError("amount must be non-negative")
    return d


def convert(from_code: str, to_code: str, amount: Decimal, timeout: int = 15) -> Decimal:
    """Convert an amount from one currency to another using the Frankfurter API.

    Builds a GET request to the latest rates endpoint, validates inputs,
    performs the HTTP call with a timeout, and parses the JSON response.

    Args:
        from_code: Source currency code (e.g. "USD").
        to_code: Target currency code (e.g. "EUR").
        amount: Decimal amount to convert; must be non-negative.
        timeout: Socket timeout in seconds for the HTTP call (default 15).

    Returns:
        Decimal: Converted amount as returned by the API.

    Raises:
        ValueError: For invalid inputs or if the API returns a parseable error
            or the response cannot be parsed into a number.
        IOError: For HTTP status errors or network-level failures.
    """
    validate_currency_code(from_code)
    validate_currency_code(to_code)
    if amount is None:
        raise ValueError("amount must not be null")

    url = (
        f"{API_ENDPOINT}?amount={_normalize_decimal(amount)}"
        f"&from={from_code.upper()}&to={to_code.upper()}"
    )

    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read().decode('utf-8', errors='replace')
    except error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        # Try to parse API error message
        try:
            data = json.loads(body)
            msg = data.get('error')
            if isinstance(msg, str):
                raise ValueError(f"API error: {msg}")
        except Exception:
            pass
        raise IOError(f"API request failed with status {e.code}")
    except error.URLError as e:
        raise IOError(f"Network error: {e.reason}")

    if status != 200:
        raise IOError(f"API request failed with status {status}")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise ValueError("Could not parse conversion result from API response")

    # Frankfurter returns {"amount":..., "base":"USD", "date":"...", "rates": {"EUR": 1.2345}}
    if isinstance(data, dict) and 'error' in data and isinstance(data['error'], str):
        raise ValueError(f"API error: {data['error']}")

    rates = data.get('rates') if isinstance(data, dict) else None
    if not isinstance(rates, dict):
        raise ValueError("Could not parse conversion result from API response")

    key = to_code.upper()
    val = rates.get(key)
    if val is None:
        raise ValueError("Could not parse conversion result from API response")

    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError):
        raise ValueError("Could not parse conversion result from API response")


def main(argv):
    """Command-line entry point.

    Expects three arguments: FROM TO AMOUNT. Prints a single line with the
    conversion result or an error message to stderr. Returns a process exit
    status code (0 on success, 1 on failure; 0 also for usage help).

    Args:
        argv: List of strings [FROM, TO, AMOUNT].

    Returns:
        int: Exit status code.
    """
    if len(argv) != 3:
        print("Usage: python currency_api.py <FROM> <TO> <AMOUNT>")
        print("Example: python currency_api.py USD EUR 123.45")
        return 0

    from_code, to_code, amount_str = argv

    try:
        amount = parse_amount(amount_str)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    try:
        converted = convert(from_code, to_code, amount)
    except Exception as e:
        # Mirror Java messaging style where possible
        print(f"Conversion failed: {e}", file=sys.stderr)
        return 1

    left = _normalize_decimal(amount)
    right = _normalize_decimal(converted)
    print(f"{left} {from_code.upper()} = {right} {to_code.upper()}")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
