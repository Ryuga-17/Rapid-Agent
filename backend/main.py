from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables early before local imports
load_dotenv()

from backend.models.schemas import AnalysisRequest, AnalysisResponse, PortfolioRequest, PortfolioAnalysisResponse
from backend.agents.market_agent import MarketAgent
from backend.agents.macro_agent import MacroAgent
from backend.agents.committee_agent import CommitteeAgent
from backend.agents.portfolio_agent import PortfolioAgent
from backend.services.regime_service import RegimeService
from backend.services.mongodb_service import MongoDBService
from backend.services.comparison_service import ComparisonService
from backend.routes.history import router as history_router
from backend.routes.stream import router as stream_router
from backend.events import current_trace_id, current_trace_data
from datetime import datetime, timezone
import uuid
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Investment Committee",
    description="An institutional-style portfolio intelligence MVP.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(history_router)
app.include_router(stream_router)

market_agent = MarketAgent()
macro_agent = MacroAgent()
committee_agent = CommitteeAgent()
portfolio_agent = PortfolioAgent()
regime_service = RegimeService()
db_service = MongoDBService()
comparison_service = ComparisonService()

def safe_dump(obj):
    from fastapi.encoders import jsonable_encoder
    return jsonable_encoder(obj)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest, trace_id: str = Query(None, description="Optional trace ID for SSE subscription")):
    if not trace_id:
        trace_id = str(uuid.uuid4())
    current_trace_id.set(trace_id)
    current_trace_data.set([])
    
    ticker = request.ticker
    logger.info(f"Received analysis request for ticker: {ticker} (Trace: {trace_id})")
    
    try:
        # Step 1: Gather Market Data
        market_info = market_agent.gather_data(ticker)
        company_name = market_info["company_name"]
        market_data = market_info["market_data"]
        
        # Step 2: Gather Macro Data
        macro_data = macro_agent.gather_data()
        
        # Step 2b: Detect Regime (for storage requirements)
        regime_data = regime_service.detect_regime(
            inflation=macro_data.inflation,
            interest_rate=macro_data.interest_rate,
            gdp_growth=macro_data.gdp_growth or 0.0
        )
        
        # Step 3: Generate Recommendation using LLM
        recommendation = committee_agent.analyze(
            ticker=ticker,
            company_name=company_name,
            market_data=market_data,
            macro_data=macro_data
        )

        # Step 4: Persistence and Historical Comparison
        current_analysis = {
            "ticker": ticker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market_data": safe_dump(market_data),
            "macro_data": safe_dump(macro_data),
            "regime_data": safe_dump(regime_data),
            "committee_output": safe_dump(recommendation)
        }

        previous_analysis = db_service.get_latest_stock_analysis(ticker)
        comparison = comparison_service.compare_with_previous_analysis(current_analysis, previous_analysis)
        current_analysis["comparison"] = comparison

        db_service.save_stock_analysis(current_analysis)
        
        if comparison:
            change_doc = {
                "ticker": ticker,
                "timestamp": current_analysis["timestamp"],
                "previous_rating": comparison.get("previous_rating"),
                "current_rating": comparison.get("current_rating"),
                "confidence_change": comparison.get("confidence_change"),
                "regime_changed": comparison.get("regime_changed"),
                "new_risks": comparison.get("new_risks")
            }
            db_service.save_recommendation_change(change_doc)
            
        historical_context = comparison if comparison else None

        # Construct and return final response
        response = AnalysisResponse(
            company=company_name,
            market_data=market_data,
            macro_data=macro_data,
            recommendation=recommendation,
            historical_context=historical_context
        )
        
        trace_data = current_trace_data.get()
        if trace_data:
            db_service.save_execution_trace(trace_id, trace_data)
            
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis.")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/analyze-portfolio", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio_endpoint(request: PortfolioRequest, trace_id: str = Query(None, description="Optional trace ID for SSE subscription")):
    if not trace_id:
        trace_id = str(uuid.uuid4())
    current_trace_id.set(trace_id)
    current_trace_data.set([])

    logger.info(f"Received portfolio analysis request (Trace: {trace_id})")
    
    try:
        # Step 1: Analyze Portfolio
        portfolio_analysis = portfolio_agent.analyze(request.portfolio)
        
        # Step 2: Gather Macro Data
        macro_data = macro_agent.gather_data()
        
        # Step 3: Detect Regime
        regime_data = regime_service.detect_regime(
            inflation=macro_data.inflation,
            interest_rate=macro_data.interest_rate,
            gdp_growth=macro_data.gdp_growth or 0.0
        )
        
        # Step 4: Generate Recommendation using LLM
        recommendation = committee_agent.analyze_portfolio(
            portfolio_analysis=portfolio_analysis,
            macro_data=macro_data,
            regime_data=regime_data
        )
        
        # Step 5: Persistence and Historical Comparison
        current_analysis = {
            "portfolio": [safe_dump(h) for h in request.portfolio],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "portfolio_analysis": safe_dump(portfolio_analysis),
            "macro_data": safe_dump(macro_data),
            "regime_data": safe_dump(regime_data),
            "committee_output": safe_dump(recommendation)
        }

        previous_analysis = db_service.get_latest_portfolio_analysis()
        comparison = comparison_service.compare_with_previous_analysis(current_analysis, previous_analysis)
        current_analysis["comparison"] = comparison

        db_service.save_portfolio_analysis(current_analysis)
        
        historical_context = comparison if comparison else None

        # Construct and return final response
        response = PortfolioAnalysisResponse(
            portfolio_analysis=portfolio_analysis,
            regime=regime_data,
            committee_recommendation=recommendation,
            historical_context=historical_context
        )
        
        trace_data = current_trace_data.get()
        if trace_data:
            db_service.save_execution_trace(trace_id, trace_data)
            
        return response
        
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during portfolio analysis.")
