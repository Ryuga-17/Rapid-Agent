# AI Investment Committee Platform

This is an institutional-style portfolio intelligence MVP inspired by BlackRock's investment workflows. It acts as an automated "Investment Committee", fetching live market data, identifying macroeconomic regimes, generating AI-powered investment recommendations via the Groq LLM API, and persisting all historical intelligence to MongoDB for change-tracking and comparative analysis.

---

## 🌟 Core Features

1. **Live Data Aggregation**: Fetches real-time market data, pricing, market cap, and calculates annualized volatility using `yfinance`.
2. **Regime Detection**: Analyzes current macroeconomic indicators (inflation, GDP, interest rates) to classify the current market environment (e.g. "Stagflation Risk", "Stable Growth", "High Inflation").
3. **AI-Driven Committee Analysis**: Feeds aggregated structured data into a Groq-powered LLM (`llama-3.3-70b-versatile`). The AI is prompted to act as a senior quantitative finance architect, outputting pure JSON recommendations (Buy/Hold/Sell) with a confidence score, bull case, bear case, and key risks.
4. **Historical Memory & Context**: Every analysis is automatically saved to MongoDB Atlas. When a stock is analyzed multiple times, the system retrieves the previous analysis, compares it to the new one, and outputs a `historical_context` payload showing exactly how the recommendation, confidence, and risks have shifted over time.
5. **Change Tracking & Auditability**: Stores chronological shifts in a dedicated `recommendation_changes` database collection, allowing institutional memory to be queried via the API.
6. **Multi-Asset Portfolio Analysis**: Analyzes portfolios to determine sector exposure and concentration risks, providing holistic portfolio-level recommendations.

---

## 🏗️ Architecture

The platform follows a clean service-oriented architecture:

* **Market Agent**: Interacts with Yahoo Finance for live pricing and volatility metrics.
* **Macro Agent**: Provides macroeconomic baseline data (inflation, interest rates, GDP growth).
* **Regime Service**: Evaluates macro conditions and outputs the market regime.
* **Portfolio Agent**: Aggregates multi-asset portfolios for sector exposure and concentration risks.
* **Committee Agent**: The LLM integration layer (Groq API) responsible for qualitative reasoning.
* **Comparison Service**: The historical intelligence engine that calculates the diffs in rating, confidence, and newly identified risks between runs.
* **MongoDB Service**: Persists all analyses, portfolio runs, and change tracking logs to MongoDB.

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- A valid [Groq API Key](https://console.groq.com/keys)
- A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster

### Installation

1. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory and add your Groq API key and MongoDB URI:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
   ```

4. **Run the Application**
   Start the FastAPI development server:
   ```bash
   uvicorn backend.main:app --reload
   ```
   The API will be accessible at `http://localhost:8000`. You can access the interactive Swagger UI at `http://localhost:8000/docs`.

---

## 📡 API Documentation

### 1. Analysis Endpoints

#### `POST /analyze`
Generates a complete market, macro, and AI committee analysis for a single ticker. If the ticker was analyzed previously, it automatically generates a `historical_context` comparison.
**Payload:**
```json
{
  "ticker": "RELIANCE.NS"
}
```

#### `POST /analyze-portfolio`
Generates an aggregated analysis for a multi-asset portfolio, including sector exposure and concentration risk.
**Payload:**
```json
{
  "portfolio": [
    { "ticker": "TCS.NS", "weight": 50 },
    { "ticker": "INFY.NS", "weight": 50 }
  ]
}
```

### 2. Historical Intelligence Endpoints
*Every time an analysis is generated, it is persisted to MongoDB. These endpoints retrieve that memory.*

- **`GET /history/stocks`**: Retrieves the most recent stock analyses across all tickers.
- **`GET /history/stocks/{ticker}`**: Retrieves the entire chronological timeline of analyses for a specific asset.
- **`GET /history/stocks/{ticker}/latest`**: Retrieves only the absolute latest analysis for a specific asset.
- **`GET /history/stocks/{ticker}/changes`**: Retrieves a chronological log of all recommendation, confidence, and risk changes that occurred for a specific asset.
- **`GET /history/portfolios`**: Retrieves the history of all portfolio analyses.
- **`GET /history/portfolios/latest`**: Retrieves the absolute latest portfolio run.

---

## 🗄️ Database Collections
- `stock_analyses`: Stores the raw inputs, macro data, and the final LLM committee output for every individual stock run.
- `portfolio_analyses`: Stores the portfolio compositions, sector exposures, concentration risks, and portfolio-level LLM recommendations.
- `recommendation_changes`: Dedicated audit log storing only the calculated differences (e.g., changes from "Buy" to "Hold", drops in confidence) between subsequent analysis runs for the same ticker.
