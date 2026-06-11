import os
import json
from groq import Groq
from backend.models.schemas import MarketData, MacroData, Recommendation, PortfolioAnalysis, RegimeData, PortfolioRecommendation
from backend.events import track_execution
import logging

logger = logging.getLogger(__name__)

class CommitteeAgent:
    def __init__(self):
        # The Groq client will automatically pick up the GROQ_API_KEY environment variable.
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    @track_execution("Committee Analysis (LLM)")
    def analyze(self, ticker: str, company_name: str, market_data: MarketData, macro_data: MacroData) -> Recommendation:
        """
        Uses the Groq API to generate an investment recommendation based on market and macro data.
        """
        prompt = f"""
        You are a senior quantitative finance architect and investment committee member.
        Analyze the following data for {company_name} ({ticker}) and provide an investment recommendation.
        
        Market Data:
        - Price: {market_data.price}
        - Market Cap: {market_data.market_cap}
        - PE Ratio: {market_data.pe_ratio}
        - Volatility: {market_data.volatility}
        
        Macro Data:
        - Inflation: {macro_data.inflation}%
        - Interest Rate: {macro_data.interest_rate}%
        - GDP Growth: {macro_data.gdp_growth}%
        
        Provide your response exactly as a JSON object matching this schema:
        {{
            "rating": "Buy" | "Hold" | "Sell",
            "confidence": <integer from 0 to 100>,
            "bull_case": "<string explaining the bull case>",
            "bear_case": "<string explaining the bear case>",
            "key_risks": ["<risk 1>", "<risk 2>", "..."]
        }}
        Do not include any text outside the JSON block.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Updated to a supported Groq model
                messages=[
                    {"role": "system", "content": "You are a helpful financial AI assistant. Always return pure JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            return Recommendation(
                rating=data.get("rating", "Hold"),
                confidence=data.get("confidence", 50),
                bull_case=data.get("bull_case", "Not provided."),
                bear_case=data.get("bear_case", "Not provided."),
                key_risks=data.get("key_risks", [])
            )
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            # Fallback response in case of error
            return Recommendation(
                rating="Hold",
                confidence=0,
                bull_case="Error generating analysis.",
                bear_case="Error generating analysis.",
                key_risks=["API Error"]
            )

    @track_execution("Committee Analysis (LLM)")
    def analyze_portfolio(self, portfolio_analysis: PortfolioAnalysis, macro_data: MacroData, regime_data: RegimeData) -> PortfolioRecommendation:
        """
        Uses the Groq API to generate an investment recommendation for a portfolio.
        """
        prompt = f"""
        You are an institutional investment committee.
        Analyze the following data and provide an investment recommendation for the portfolio.
        
        Portfolio Composition:
        - Number of Holdings: {portfolio_analysis.portfolio_summary.num_holdings}
        - Largest Position: {portfolio_analysis.portfolio_summary.largest_position} ({portfolio_analysis.portfolio_summary.largest_weight}%)
        - Sector Exposure: {portfolio_analysis.sector_exposure}
        - Concentration Risk: {portfolio_analysis.concentration_risk}
        
        Macro Environment:
        - Inflation: {macro_data.inflation}%
        - Interest Rate: {macro_data.interest_rate}%
        - GDP Growth: {macro_data.gdp_growth}%
        
        Current Regime:
        - Regime: {regime_data.regime}
        - Market Environment: {regime_data.market_environment}
        
        Provide your response exactly as a JSON object matching this schema:
        {{
            "recommendation": "Buy" | "Hold" | "Sell",
            "confidence": <integer from 0 to 100>,
            "bull_case": "<string explaining the bull case>",
            "bear_case": "<string explaining the bear case>",
            "top_risks": ["<risk 1>", "<risk 2>", "..."]
        }}
        Do not include any text outside the JSON block.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful financial AI assistant. Always return pure JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            return PortfolioRecommendation(
                recommendation=data.get("recommendation", "Hold"),
                confidence=data.get("confidence", 50),
                bull_case=data.get("bull_case", "Not provided."),
                bear_case=data.get("bear_case", "Not provided."),
                top_risks=data.get("top_risks", [])
            )
            
        except Exception as e:
            logger.error(f"Error generating portfolio recommendation: {e}")
            return PortfolioRecommendation(
                recommendation="Hold",
                confidence=0,
                bull_case="Error generating analysis.",
                bear_case="Error generating analysis.",
                top_risks=["API Error"]
            )
