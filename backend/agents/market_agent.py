from backend.services.market_service import MarketService
from backend.models.schemas import MarketData
from backend.events import track_execution

class MarketAgent:
    def __init__(self):
        self.market_service = MarketService()

    @track_execution("Market Data Collection")
    def gather_data(self, ticker: str) -> dict:
        """
        Orchestrates the retrieval of market data.
        """
        raw_data = self.market_service.fetch_market_data(ticker)
        
        # Structure the data into our expected model format
        market_data = MarketData(
            price=raw_data.get("price", 0.0),
            market_cap=raw_data.get("market_cap", 0.0),
            pe_ratio=raw_data.get("pe_ratio"),
            volatility=raw_data.get("volatility"),
            sector=raw_data.get("sector", "Unknown")
        )
        
        return {
            "company_name": raw_data.get("company_name", ticker),
            "market_data": market_data
        }
