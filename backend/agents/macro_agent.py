from backend.services.macro_service import MacroService
from backend.models.schemas import MacroData
from backend.events import track_execution

class MacroAgent:
    def __init__(self):
        self.macro_service = MacroService()

    @track_execution("Macro Analysis")
    def gather_data(self) -> MacroData:
        """
        Orchestrates the retrieval of macroeconomic data.
        """
        raw_data = self.macro_service.fetch_macro_data()
        
        macro_data = MacroData(
            inflation=raw_data.get("inflation", 0.0),
            interest_rate=raw_data.get("interest_rate", 0.0),
            gdp_growth=raw_data.get("gdp_growth")
        )
        
        return macro_data
