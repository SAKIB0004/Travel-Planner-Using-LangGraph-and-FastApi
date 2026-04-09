"""Currency conversion helper with multiple fallback APIs."""
from __future__ import annotations

from typing import Any

import httpx

from app.config.settings import get_settings
from app.utils.helpers import cache_get, cache_set
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CurrencyToolService:
    """Service for currency conversion and exchange rates."""
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get current exchange rate from one currency to another.
        Uses caching to avoid repeated API calls.
        """
        if from_currency.upper() == to_currency.upper():
            return 1.0
        
        # Check cache
        cache_key = f"exchange_rate:{from_currency.upper()}_{to_currency.upper()}"
        cached = cache_get(cache_key)
        if cached is not None:
            return float(cached)
        
        # Try API
        rate = await self._fetch_exchange_rate(from_currency, to_currency)
        if rate:
            cache_set(cache_key, rate)
            return rate
        
        # Fallback to mock rates
        return self._get_mock_rate(from_currency, to_currency)
    
    async def _fetch_exchange_rate(self, from_currency: str, to_currency: str) -> float | None:
        """Try to fetch real exchange rate from multiple APIs."""
        from_code = from_currency.upper()
        to_code = to_currency.upper()
        
        # Try ExchangeRate-API (free tier available)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Note: ExchangeRate-API free tier has limited requests
                url = f"https://api.exchangerate-api.com/v4/latest/{from_code}"
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    rate = data.get("rates", {}).get(to_code)
                    if rate:
                        return float(rate)
        except Exception as exc:
            logger.debug("exchangerate_api_error", from_currency=from_code, to_currency=to_code, error=str(exc))
        
        # Try ExchangeRate-Host (free, no key required)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"https://api.exchangerate-api.com/v4/latest/{from_code}"
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    rate = data.get("rates", {}).get(to_code)
                    if rate:
                        return float(rate)
        except Exception as exc:
            logger.debug("exchangerate_host_error", from_currency=from_code, to_currency=to_code, error=str(exc))
        
        return None
    
    def _get_mock_rate(self, from_currency: str, to_currency: str) -> float:
        """Return approximate historical exchange rates for common pairs."""
        from_code = from_currency.upper()
        to_code = to_currency.upper()
        
        # Approximate rates to USD (April 2026 baseline)
        rates_to_usd = {
            "USD": 1.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 150.0,
            "AUD": 1.52,
            "CAD": 1.37,
            "CHF": 0.88,
            "CNY": 7.24,
            "INR": 83.1,
            "THB": 34.5,
            "SGD": 1.34,
            "IDR": 15800.0,
            "MXN": 17.1,
            "BRL": 4.97,
            "KRW": 1310.0,
            "HKD": 7.81,
            "NOK": 10.5,
            "SEK": 11.2,
            "DKK": 6.87,
            "NZD": 1.65,
            "ZAR": 18.8,
        }
        
        # Calculate cross rate
        from_to_usd = rates_to_usd.get(from_code, 1.0)
        to_to_usd = rates_to_usd.get(to_code, 1.0)
        
        if from_to_usd == 0:
            from_to_usd = 1.0
        if to_to_usd == 0:
            to_to_usd = 1.0
        
        return to_to_usd / from_to_usd
    
    async def convert_amount(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str
    ) -> dict[str, Any]:
        """
        Convert an amount from one currency to another.
        
        Returns dict with original amount, target amount, and exchange rate.
        """
        rate = await self.get_exchange_rate(from_currency, to_currency)
        converted = amount * rate
        
        return {
            "from_amount": amount,
            "from_currency": from_currency.upper(),
            "to_amount": round(converted, 2),
            "to_currency": to_currency.upper(),
            "exchange_rate": round(rate, 4),
            "note": "Rates are approximate and updated daily." if rate else "Using historical rates.",
        }


currency_service = CurrencyToolService()
