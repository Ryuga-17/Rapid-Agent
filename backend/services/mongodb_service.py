import os
import certifi
from pymongo import MongoClient
import logging
from backend.events import track_execution

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
        self.client = MongoClient(uri, tlsCAFile=certifi.where())
        self.db = self.client.investment_committee

        # Collections
        self.stock_analyses = self.db.stock_analyses
        self.portfolio_analyses = self.db.portfolio_analyses
        self.macro_snapshots = self.db.macro_snapshots
        self.committee_reports = self.db.committee_reports
        self.recommendation_changes = self.db.recommendation_changes
        self.execution_traces = self.db.execution_traces

        # Create Indexes
        self._create_indexes()

    def _create_indexes(self):
        try:
            self.stock_analyses.create_index([("ticker", 1)])
            self.stock_analyses.create_index([("timestamp", -1)])
            self.portfolio_analyses.create_index([("timestamp", -1)])
            self.recommendation_changes.create_index([("ticker", 1)])
            self.recommendation_changes.create_index([("timestamp", -1)])
            self.execution_traces.create_index([("trace_id", 1)])
            logger.info("MongoDB indexes verified/created.")
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")

    # --- Stock Analysis Methods ---

    @track_execution("MongoDB Persistence")
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

    @track_execution("MongoDB Persistence")
    def save_portfolio_analysis(self, analysis_doc: dict):
        self.portfolio_analyses.insert_one(analysis_doc)

    def get_portfolio_history(self, limit: int = 10):
        cursor = self.portfolio_analyses.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)

    def get_latest_portfolio_analysis(self):
        return self.portfolio_analyses.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])

    # --- Recommendation Changes Methods ---

    @track_execution("Audit Logging")
    def save_recommendation_change(self, change_doc: dict):
        self.recommendation_changes.insert_one(change_doc)

    def get_recommendation_changes(self, ticker: str, limit: int = 10):
        cursor = self.recommendation_changes.find({"ticker": ticker}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)

    # --- Execution Traces Methods ---

    def save_execution_trace(self, trace_id: str, events: list):
        self.execution_traces.insert_one({"trace_id": trace_id, "events": events})

    def get_execution_traces(self):
        cursor = self.execution_traces.find({}, {"_id": 0}).sort("_id", -1)
        return list(cursor)
