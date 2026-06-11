from fastapi import APIRouter, HTTPException
from typing import List
from backend.services.mongodb_service import MongoDBService
from backend.models.schemas import HistoryStockResponse, HistoryPortfolioResponse, RecommendationChangeResponse

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

db_service = MongoDBService()

@router.get("/stocks", response_model=List[HistoryStockResponse])
async def get_latest_stocks():
    """Returns the latest stock analyses across all tickers."""
    docs = db_service.get_all_latest_stock_analyses(limit=20)
    return docs

@router.get("/stocks/{ticker}", response_model=List[HistoryStockResponse])
async def get_stock_history(ticker: str):
    """Returns all analyses for a specific ticker."""
    docs = db_service.get_stock_analysis_history(ticker)
    return docs

@router.get("/stocks/{ticker}/latest", response_model=HistoryStockResponse)
async def get_latest_stock(ticker: str):
    """Returns most recent analysis for a specific ticker."""
    doc = db_service.get_latest_stock_analysis(ticker)
    if not doc:
        raise HTTPException(status_code=404, detail="No history found for this ticker.")
    return doc

@router.get("/stocks/{ticker}/changes", response_model=List[RecommendationChangeResponse])
async def get_stock_changes(ticker: str):
    """Returns recommendation changes for a specific ticker."""
    docs = db_service.get_recommendation_changes(ticker)
    return docs

@router.get("/portfolios", response_model=List[HistoryPortfolioResponse])
async def get_portfolios_history():
    """Returns recent portfolio analyses."""
    docs = db_service.get_portfolio_history()
    return docs

@router.get("/portfolios/latest", response_model=HistoryPortfolioResponse)
async def get_latest_portfolio():
    """Returns latest portfolio analysis."""
    doc = db_service.get_latest_portfolio_analysis()
    if not doc:
        raise HTTPException(status_code=404, detail="No portfolio history found.")
    return doc
