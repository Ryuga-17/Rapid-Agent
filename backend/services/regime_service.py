from backend.models.schemas import RegimeData
from backend.events import track_execution

class RegimeService:
    @track_execution("Regime Detection")
    def detect_regime(self, inflation: float, interest_rate: float, gdp_growth: float) -> RegimeData:
        """
        Determines the current market regime based on macroeconomic inputs.
        """
        # Determine regime based on inflation
        if inflation > 5.0:
            regime = "High Inflation"
        elif 3.0 <= inflation <= 5.0:
            regime = "Moderate Inflation"
        else:
            regime = "Low Inflation"
            
        # Determine market environment based on GDP and interest rates
        if gdp_growth >= 6.0 and interest_rate < 7.0:
            market_environment = "Stable Growth"
        elif gdp_growth < 6.0 and interest_rate >= 7.0:
            market_environment = "Stagflation Risk"
        elif gdp_growth >= 7.0:
            market_environment = "High Growth"
        else:
            market_environment = "Neutral"

        return RegimeData(
            regime=regime,
            market_environment=market_environment
        )
