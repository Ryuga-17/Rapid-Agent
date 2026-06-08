import os
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

class MongoDBService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(uri)
        self.db = self.client.investment_committee

        # Collections
        self.stock_analyses = self.db.stock_analyses
        self.portfolio_analyses = self.db.portfolio_analyses
        self.macro_snapshots = self.db.macro_snapshots
        self.committee_reports = self.db.committee_reports

        # Create Indexes
        self._create_indexes()

    def _create_indexes(self):
        try:
            self.stock_analyses.create_index([("ticker", 1)])
            self.stock_analyses.create_index([("timestamp", -1)])
            self.portfolio_analyses.create_index([("timestamp", -1)])
            logger.info("MongoDB indexes verified/created.")
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")

    # --- Stock Analysis Methods ---

    def save_stock_analysis(self, analysis_doc: dict):
        self.stock_analyses.insert_one(analysis_doc)

    def get_stock_analysis_history(self, ticker: str, limit: int = 10):
        cursor = self.stock_analyses.find({"ticker": ticker}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)

    def get_latest_stock_analysis(self, ticker: str):
        return self.stock_analyses.find_one({"ticker": ticker}, {"_id": 0}, sort=[("timestamp", -1)])
    
    def get_all_latest_stock_analyses(self, limit: int = 10):
        # Depending on requirements, this might mean latest overall or latest distinct tickers.
        # We will assume latest overall for now.
        cursor = self.stock_analyses.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)

    # --- Portfolio Analysis Methods ---

    def save_portfolio_analysis(self, analysis_doc: dict):
        self.portfolio_analyses.insert_one(analysis_doc)

    def get_portfolio_history(self, limit: int = 10):
        cursor = self.portfolio_analyses.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)

    def get_latest_portfolio_analysis(self):
        return self.portfolio_analyses.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
