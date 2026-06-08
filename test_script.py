import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from backend.agents.market_agent import MarketAgent
from backend.agents.macro_agent import MacroAgent
from backend.agents.committee_agent import CommitteeAgent

def test():
    ticker = "RELIANCE.NS"
    print(f"Testing for {ticker}...")
    
    market = MarketAgent().gather_data(ticker)
    print("Market Data:", market)
    
    macro = MacroAgent().gather_data()
    print("Macro Data:", macro)
    
    committee = CommitteeAgent()
    recommendation = committee.analyze(
        ticker=ticker,
        company_name=market["company_name"],
        market_data=market["market_data"],
        macro_data=macro
    )
    print("Recommendation:", recommendation)

if __name__ == "__main__":
    test()
