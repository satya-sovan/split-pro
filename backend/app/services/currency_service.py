"""
Currency rate service - handles exchange rate fetching and caching
Supports multiple providers: Frankfurter (free), Open Exchange Rates, NBP
"""
from typing import Optional, Dict
from datetime import date, datetime, timedelta
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import CachedCurrencyRate


class CurrencyRateService:
    """Service for fetching and caching currency exchange rates"""

    def __init__(self):
        self.base_url = "https://api.frankfurter.app"
        self.cache_duration = timedelta(hours=24)

    async def get_rate(
        self,
        db: Session,
        from_currency: str,
        to_currency: str,
        rate_date: Optional[date] = None
    ) -> float:
        """
        Get exchange rate between two currencies

        Args:
            db: Database session
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')
            rate_date: Date for historical rate (default: today)

        Returns:
            Exchange rate as float
        """
        if from_currency == to_currency:
            return 1.0

        rate_date = rate_date or date.today()

        # Check cache first
        cached = self._get_cached_rate(db, from_currency, to_currency, rate_date)
        if cached:
            return cached

        # Fetch from API
        rate = await self._fetch_rate_from_api(from_currency, to_currency, rate_date)

        # Cache the result
        self._cache_rate(db, from_currency, to_currency, rate_date, rate)

        return rate

    async def get_batch_rates(
        self,
        db: Session,
        from_currencies: list[str],
        to_currency: str,
        rate_date: Optional[date] = None
    ) -> Dict[str, float]:
        """
        Get exchange rates for multiple currencies to a single target currency

        Args:
            db: Database session
            from_currencies: List of source currency codes
            to_currency: Target currency code
            rate_date: Date for historical rates

        Returns:
            Dictionary mapping currency codes to exchange rates
        """
        rates = {}

        for currency in from_currencies:
            try:
                rate = await self.get_rate(db, currency, to_currency, rate_date)
                rates[currency] = rate
            except Exception as e:
                print(f"Error fetching rate for {currency}: {e}")
                rates[currency] = 1.0  # Fallback to 1:1

        return rates

    def _get_cached_rate(
        self,
        db: Session,
        from_currency: str,
        to_currency: str,
        rate_date: date
    ) -> Optional[float]:
        """Check if rate is cached and not expired"""
        cached = db.query(CachedCurrencyRate).filter(
            CachedCurrencyRate.from_currency == from_currency,
            CachedCurrencyRate.to_currency == to_currency,
            CachedCurrencyRate.date == rate_date
        ).first()

        if cached:
            # Check if cache is still valid
            cache_age = datetime.utcnow() - cached.cached_at
            if cache_age < self.cache_duration:
                return cached.rate

        return None

    def _cache_rate(
        self,
        db: Session,
        from_currency: str,
        to_currency: str,
        rate_date: date,
        rate: float
    ):
        """Cache exchange rate in database"""
        cached = CachedCurrencyRate(
            from_currency=from_currency,
            to_currency=to_currency,
            date=rate_date,
            rate=rate,
            cached_at=datetime.utcnow()
        )

        # Upsert
        existing = db.query(CachedCurrencyRate).filter(
            CachedCurrencyRate.from_currency == from_currency,
            CachedCurrencyRate.to_currency == to_currency,
            CachedCurrencyRate.date == rate_date
        ).first()

        if existing:
            existing.rate = rate
            existing.cached_at = datetime.utcnow()
        else:
            db.add(cached)

        db.commit()

    async def _fetch_rate_from_api(
        self,
        from_currency: str,
        to_currency: str,
        rate_date: date
    ) -> float:
        """Fetch rate from Frankfurter API"""
        async with httpx.AsyncClient() as client:
            # Format date as YYYY-MM-DD
            date_str = rate_date.strftime("%Y-%m-%d")

            # Build URL
            url = f"{self.base_url}/{date_str}"
            params = {
                "from": from_currency,
                "to": to_currency
            }

            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Extract rate from response
                # Frankfurter returns: {"rates": {"EUR": 0.85}, ...}
                rate = data["rates"].get(to_currency)

                if rate is None:
                    raise ValueError(f"Rate not found for {to_currency}")

                return float(rate)

            except httpx.HTTPError as e:
                print(f"HTTP error fetching rate: {e}")
                # Fallback to 1:1 exchange rate
                return 1.0
            except (KeyError, ValueError) as e:
                print(f"Error parsing rate response: {e}")
                return 1.0


# Global service instance
currency_service = CurrencyRateService()

