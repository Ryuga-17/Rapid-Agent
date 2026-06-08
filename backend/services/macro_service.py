class MacroService:
    def fetch_macro_data(self) -> dict:
        """
        Fetches macroeconomic data.
        For the MVP, we mock these values since real-time APIs often require subscriptions.
        """
        return {
            "inflation": 5.1,        # Mocked CPI inflation rate (%)
            "interest_rate": 6.5,    # Mocked central bank interest rate (%)
            "gdp_growth": 7.2        # Mocked GDP growth rate (%)
        }
