"""
Number utilities for currency handling and BigInt operations
Ported from src/utils/numbers.ts

All amounts are stored as integers (cents) to avoid floating point errors.
For example: $12.50 = 1250 (cents)
"""
from typing import Union


class BigMath:
    """
    BigInt math utilities
    Python ints have arbitrary precision, so most operations are straightforward
    """

    @staticmethod
    def abs(n: int) -> int:
        """Absolute value"""
        return abs(n)

    @staticmethod
    def sign(n: int) -> int:
        """Sign of number: -1, 0, or 1"""
        if n > 0:
            return 1
        elif n < 0:
            return -1
        else:
            return 0

    @staticmethod
    def min(*args: int) -> int:
        """Minimum of values"""
        return min(args)

    @staticmethod
    def max(*args: int) -> int:
        """Maximum of values"""
        return max(args)

    @staticmethod
    def round_div(dividend: int, divisor: int) -> int:
        """
        Divide and round to nearest integer
        Used for splitting amounts
        """
        if divisor == 0:
            return 0
        return round(dividend / divisor)


class CurrencyHelpers:
    """
    Currency-aware helpers for converting between BigInt (cents) and display values

    Example:
        helpers = CurrencyHelpers("USD", "en-US")
        display = helpers.to_ui_string(1250)  # "$12.50"
        cents = helpers.to_safe_bigint("12.50")  # 1250
    """

    def __init__(self, currency: str = "USD", locale: str = "en-US", decimal_digits: int = 2):
        self.currency = currency.upper()
        self.locale = locale
        self.decimal_digits = decimal_digits
        self.decimal_multiplier = 10 ** decimal_digits

    def to_ui_string(self, amount: int) -> str:
        """
        Convert BigInt (cents) to formatted currency string

        Args:
            amount: Amount in cents (e.g., 1250 for $12.50)

        Returns:
            Formatted string (e.g., "$12.50")
        """
        value = amount / self.decimal_multiplier
        return f"{self.currency} {value:.{self.decimal_digits}f}"

    def to_safe_bigint(self, value: Union[str, int, float]) -> int:
        """
        Convert user input to BigInt (cents)

        Args:
            value: User input - can be string "12.50", int 12, or float 12.50

        Returns:
            Amount in cents (e.g., 1250)
        """
        if isinstance(value, int):
            # Already in cents if it's a large number, otherwise assume dollars
            if abs(value) > 1000:
                return value
            return value * self.decimal_multiplier

        if isinstance(value, float):
            return int(round(value * self.decimal_multiplier))

        if isinstance(value, str):
            # Remove currency symbols and whitespace
            cleaned = value.strip()
            for symbol in ['$', '€', '£', '¥', self.currency]:
                cleaned = cleaned.replace(symbol, '')
            cleaned = cleaned.strip()

            # Handle empty string
            if not cleaned:
                return 0

            # Parse as float then convert to cents
            try:
                float_value = float(cleaned)
                return int(round(float_value * self.decimal_multiplier))
            except ValueError:
                return 0

        return 0

    def sanitize_input(self, input_str: str) -> str:
        """
        Sanitize input by allowing only digits, negative sign, and decimal separator
        """
        cleaned = ""
        has_decimal = False
        has_negative = False

        for char in input_str:
            # Allow negative sign at the start
            if char == '-' and not has_negative and len(cleaned) == 0:
                cleaned += char
                has_negative = True
                continue

            # Allow decimal point (only one)
            if char in ['.', ','] and not has_decimal:
                cleaned += '.'
                has_decimal = True
                continue

            # Allow digits
            if char.isdigit():
                cleaned += char

        return cleaned


def calculate_equal_split(total: int, num_participants: int) -> list[int]:
    """
    Split amount equally among participants

    Args:
        total: Total amount in cents
        num_participants: Number of people to split among

    Returns:
        List of amounts for each participant

    Example:
        calculate_equal_split(1000, 3) -> [334, 333, 333]
    """
    if num_participants == 0:
        return []

    base_share = total // num_participants
    remainder = total % num_participants

    shares = [base_share] * num_participants

    # Distribute remainder to first N participants
    for i in range(remainder):
        shares[i] += 1

    return shares


def calculate_percentage_split(total: int, percentages: list[float]) -> list[int]:
    """
    Split amount by percentage

    Args:
        total: Total amount in cents
        percentages: List of percentages (e.g., [50.0, 30.0, 20.0])

    Returns:
        List of amounts for each participant
    """
    if not percentages:
        return []

    shares = []
    allocated = 0

    for i, percentage in enumerate(percentages):
        if i == len(percentages) - 1:
            # Last participant gets the remainder to avoid rounding errors
            shares.append(total - allocated)
        else:
            share = int(round(total * percentage / 100))
            shares.append(share)
            allocated += share

    return shares


def calculate_share_split(total: int, shares: list[int]) -> list[int]:
    """
    Split amount by shares (ratios)

    Args:
        total: Total amount in cents
        shares: List of share counts (e.g., [2, 1, 1] for 2:1:1 ratio)

    Returns:
        List of amounts for each participant

    Example:
        calculate_share_split(1000, [2, 1, 1]) -> [500, 250, 250]
    """
    if not shares:
        return []

    total_shares = sum(shares)
    if total_shares == 0:
        return [0] * len(shares)

    amounts = []
    allocated = 0

    for i, share in enumerate(shares):
        if i == len(shares) - 1:
            # Last participant gets the remainder
            amounts.append(total - allocated)
        else:
            amount = BigMath.round_div(total * share, total_shares)
            amounts.append(amount)
            allocated += amount

    return amounts


def get_currency_helpers(currency: str = "USD", locale: str = "en-US") -> CurrencyHelpers:
    """
    Factory function to get currency helpers

    This matches the TypeScript getCurrencyHelpers() function
    """
    # Map currency to decimal digits
    # Most currencies use 2 decimals, but some are different
    decimal_digits_map = {
        "JPY": 0,  # Japanese Yen
        "KRW": 0,  # Korean Won
        "VND": 0,  # Vietnamese Dong
        "BHD": 3,  # Bahraini Dinar
        "JOD": 3,  # Jordanian Dinar
        "KWD": 3,  # Kuwaiti Dinar
        "OMR": 3,  # Omani Rial
        "TND": 3,  # Tunisian Dinar
    }

    decimal_digits = decimal_digits_map.get(currency.upper(), 2)
    return CurrencyHelpers(currency, locale, decimal_digits)

