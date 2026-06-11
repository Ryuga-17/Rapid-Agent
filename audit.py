import os
import json
import logging
from fastapi.testclient import TestClient

# Load env vars
from dotenv import load_dotenv
load_dotenv()

from backend.main import app
from backend.services.regime_service import RegimeService
from backend.agents.portfolio_agent import PortfolioAgent
from backend.models.schemas import Holding

logging.basicConfig(level=logging.ERROR)
client = TestClient(app)

results = {}

def test_endpoints():
    r = {}
    
    # Analyze stock
    res = client.post("/analyze", json={"ticker": "RELIANCE.NS"})
    r["analyze_stock"] = res.status_code == 200
    
    # History stocks
    res = client.get("/history/stocks")
    r["history_stocks"] = res.status_code == 200
    
    # Specific history
    res = client.get("/history/stocks/RELIANCE.NS")
    r["history_ticker"] = res.status_code == 200
    
    # Latest
    res = client.get("/history/stocks/RELIANCE.NS/latest")
    r["history_latest"] = res.status_code == 200

    # Changes
    res = client.get("/history/stocks/RELIANCE.NS/changes")
    r["history_changes"] = res.status_code == 200
    
    # Portfolio
    res = client.post("/analyze-portfolio", json={"portfolio": [{"ticker": "RELIANCE.NS", "weight": 100}]})
    r["analyze_portfolio"] = res.status_code == 200
    
    return r

def test_market():
    r = {}
    from backend.services.market_service import MarketService
    ms = MarketService()
    for ticker in ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]:
        data = ms.fetch_market_data(ticker)
        r[ticker] = data["price"] > 0
    return r

def test_regime():
    rs = RegimeService()
    r = {}
    # High Inflation
    r["High_Inflation"] = rs.detect_regime(6.0, 5.0, 3.0).regime == "High Inflation"
    # Moderate
    r["Moderate"] = rs.detect_regime(4.0, 5.0, 3.0).regime == "Moderate Inflation"
    # Low
    r["Low"] = rs.detect_regime(2.0, 5.0, 3.0).regime == "Low Inflation"
    # Stable Growth
    r["Stable"] = rs.detect_regime(2.0, 6.0, 6.5).market_environment == "Stable Growth"
    # Stagflation
    r["Stagflation"] = rs.detect_regime(6.0, 7.5, 2.0).market_environment == "Stagflation Risk"
    return r

def test_portfolio():
    pa = PortfolioAgent()
    r = {}
    # Equal Weight
    res = pa.analyze([Holding(ticker="TCS.NS", weight=50), Holding(ticker="INFY.NS", weight=50)])
    r["Equal_Risk"] = res.concentration_risk == "High" # 50% is High
    
    # Single Asset
    res = pa.analyze([Holding(ticker="RELIANCE.NS", weight=100)])
    r["Single_Risk"] = res.concentration_risk == "High"
    return r

results["endpoints"] = test_endpoints()
results["market"] = test_market()
results["regime"] = test_regime()
results["portfolio"] = test_portfolio()

print(json.dumps(results, indent=2))
