from typing import List
from backend.models.schemas import Holding, PortfolioAnalysis, PortfolioSummary
from backend.agents.market_agent import MarketAgent
import logging

logger = logging.getLogger(__name__)

class PortfolioAgent:
    def __init__(self):
        self.market_agent = MarketAgent()

    def analyze(self, portfolio: List[Holding]) -> PortfolioAnalysis:
        """
        Analyzes a portfolio of holdings.
        Fetches market data to determine sector exposure and calculates summary metrics.
        """
        num_holdings = len(portfolio)
        
        # Calculate summary
        largest_position = ""
        largest_weight = 0.0
        
        # Determine concentration risk
        concentration_risk = "Low"
        
        sector_exposure = {}
        
        for holding in portfolio:
            if holding.weight > largest_weight:
                largest_weight = holding.weight
                largest_position = holding.ticker
                
            # Fetch market data to get the sector
            market_info = self.market_agent.gather_data(holding.ticker)
            sector = market_info["market_data"].sector or "Unknown"
            
            # Aggregate sector weights
            sector_exposure[sector] = sector_exposure.get(sector, 0.0) + holding.weight
            
        # Determine concentration risk based on largest weight
        if largest_weight >= 40.0:
            concentration_risk = "High"
        elif largest_weight >= 20.0:
            concentration_risk = "Medium"
        else:
            concentration_risk = "Low"
            
        summary = PortfolioSummary(
            num_holdings=num_holdings,
            largest_position=largest_position,
            largest_weight=largest_weight
        )
        
        return PortfolioAnalysis(
            portfolio_summary=summary,
            sector_exposure=sector_exposure,
            concentration_risk=concentration_risk
        )
