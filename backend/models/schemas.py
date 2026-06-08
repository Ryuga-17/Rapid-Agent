from pydantic import BaseModel, Field
from typing import List, Optional

class AnalysisRequest(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol (e.g., RELIANCE.NS)", json_schema_extra={"example": "RELIANCE.NS"})

class MarketData(BaseModel):
    price: float
    market_cap: float
    pe_ratio: Optional[float] = None
    volatility: Optional[float] = None
    sector: Optional[str] = None

class MacroData(BaseModel):
    inflation: float
    interest_rate: float
    gdp_growth: Optional[float] = None

class Recommendation(BaseModel):
    rating: str = Field(..., description="e.g., Buy, Hold, Sell")
    confidence: int = Field(..., description="Confidence score out of 100")
    bull_case: str
    bear_case: str
    key_risks: List[str]

class AnalysisResponse(BaseModel):
    company: str
    market_data: MarketData
    macro_data: MacroData
    recommendation: Recommendation

# --- Phase 1: Portfolio Agent Models ---

class Holding(BaseModel):
    ticker: str
    weight: float

class PortfolioRequest(BaseModel):
    portfolio: List[Holding] = Field(..., json_schema_extra={"example": [{"ticker": "TCS.NS", "weight": 25.0}, {"ticker": "INFY.NS", "weight": 25.0}]})

class PortfolioSummary(BaseModel):
    num_holdings: int
    largest_position: str
    largest_weight: float

class PortfolioAnalysis(BaseModel):
    portfolio_summary: PortfolioSummary
    sector_exposure: dict
    concentration_risk: str

# --- Phase 2: Regime Detection Models ---

class RegimeData(BaseModel):
    regime: str
    market_environment: str

# --- Phase 3 & 4: Upgraded Committee Models ---

class PortfolioRecommendation(BaseModel):
    recommendation: str = Field(..., description="e.g., Buy, Hold, Sell")
    confidence: int = Field(..., description="Confidence score out of 100")
    bull_case: str
    bear_case: str
    top_risks: List[str]

class PortfolioAnalysisResponse(BaseModel):
    portfolio_analysis: PortfolioAnalysis
    regime: RegimeData
    committee_recommendation: PortfolioRecommendation

# --- Phase 5 & 6: History and Comparison Models ---
from typing import Any

class ComparisonResult(BaseModel):
    recommendation_changed: bool
    previous_rating: Optional[str] = None
    current_rating: Optional[str] = None
    confidence_change: Optional[int] = None
    regime_changed: bool

class HistoryStockResponse(BaseModel):
    ticker: str
    timestamp: str
    market_data: dict
    macro_data: dict
    regime_data: dict
    committee_output: dict
    comparison: Optional[ComparisonResult] = None

class HistoryPortfolioResponse(BaseModel):
    timestamp: str
    portfolio: List[dict]
    portfolio_analysis: dict
    macro_data: dict
    regime_data: dict
    committee_output: dict
    comparison: Optional[ComparisonResult] = None
