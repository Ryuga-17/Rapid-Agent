# AI Investment Committee Platform

This is an institutional-style portfolio intelligence MVP inspired by BlackRock's investment workflows. It fetches live market data, identifies macroeconomic regimes, generates AI-powered investment recommendations via the Groq LLM API, and persists all historical intelligence to MongoDB for change-tracking and comparative analysis.

## Architecture

The platform follows a clean service-oriented architecture:

* **Market Agent:** Fetches live pricing, market cap, and calculates volatility using `yfinance`.
* **Macro Agent:** Provides macroeconomic data (inflation, interest rates, GDP growth).
* **Regime Service:** Detects market regimes based on macroeconomic conditions.
* **Portfolio Agent:** Aggregates and analyzes multi-asset portfolios for sector exposure and concentration risks.
* **Committee Agent:** Leverages a specified Groq LLM (e.g., Llama 3.3) to formulate structured, qualitative investment recommendations.
* **Comparison Service:** A historical intelligence engine that tracks rating, confidence, and regime changes over time.
* **MongoDB Service:** Persists every analysis securely to MongoDB Atlas or a local instance, enabling historical memory.

## Prerequisites

- Python 3.9+
- A valid [Groq API Key](https://console.groq.com/keys)
- A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster (or local MongoDB running on port 27017)

## Setup Instructions

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
   Create a `.env` file in the root directory (you can copy `.env.example`) and add your Groq API key and MongoDB URI:
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

## API Endpoints

### 1. Analysis Endpoints
- **`POST /analyze`**: Generates a complete market, macro, and AI committee analysis for a single ticker (e.g., `RELIANCE.NS`).
- **`POST /analyze-portfolio`**: Generates an aggregated analysis for a multi-asset portfolio, including sector exposure and concentration risk.

### 2. Historical Intelligence Endpoints
*Every time an analysis is generated, it is persisted to MongoDB along with a tracked comparison against its previous run.*
- **`GET /history/stocks`**: Retrieves the most recent stock analyses.
- **`GET /history/stocks/{ticker}`**: Retrieves the entire timeline of analyses for a specific asset.
- **`GET /history/stocks/{ticker}/latest`**: Retrieves the absolute latest analysis for a specific asset.
- **`GET /history/portfolios`**: Retrieves the history of portfolio analyses.
- **`GET /history/portfolios/latest`**: Retrieves the absolute latest portfolio run.

## Included Test Scripts
The repository includes several bash scripts to quickly validate the platform without needing a frontend:
- `test_api.sh`: Spins up the server and tests the single-asset `/analyze` endpoint.
- `test_portfolio_api.sh`: Spins up the server and tests the multi-asset `/analyze-portfolio` endpoint.
- `test_script.py`: Tests the underlying Python agents directly without the web server.
- `test_models.py`: Pings the Groq API to list available LLMs.
