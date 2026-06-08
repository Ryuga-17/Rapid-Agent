import yfinance as yf
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MarketService:
    def fetch_market_data(self, ticker: str) -> dict:
        """
        Fetches market data for a given ticker using yfinance.
        Calculates basic volatility using the last 30 days of data.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Fetch historical data for volatility calculation (e.g., 1 month)
            hist = stock.history(period="1mo")
            volatility = None
            if not hist.empty and len(hist) > 1:
                # Calculate daily returns
                hist['Returns'] = hist['Close'].pct_change()
                # Annualized volatility approx (252 trading days)
                volatility = hist['Returns'].std() * np.sqrt(252) * 100
            
            return {
                "price": info.get("currentPrice") or info.get("regularMarketPrice") or 0.0,
                "market_cap": info.get("marketCap") or 0.0,
                "pe_ratio": info.get("trailingPE"),
                "volatility": round(volatility, 2) if volatility else None,
                "company_name": info.get("shortName", ticker),
                "sector": info.get("sector", "Unknown")
            }
        except Exception as e:
            logger.error(f"Error fetching market data for {ticker}: {e}")
            return {
                "price": 0.0,
                "market_cap": 0.0,
                "pe_ratio": None,
                "volatility": None,
                "company_name": ticker,
                "sector": "Unknown"
            }
