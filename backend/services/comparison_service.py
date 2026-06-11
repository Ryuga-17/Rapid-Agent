from backend.events import track_execution

class ComparisonService:
    @track_execution("Historical Memory Retrieval")
    def compare_with_previous_analysis(self, current_analysis: dict, previous_analysis: dict) -> dict:
        """
        Compares the current analysis with the previous analysis and returns the differences.
        """
        if not previous_analysis:
            return None

        # Handle both stock (recommendation) and portfolio (committee_recommendation)
        current_rec = current_analysis.get("committee_output", {}).get("recommendation") or \
                      current_analysis.get("committee_output", {}).get("rating")
        
        prev_rec = previous_analysis.get("committee_output", {}).get("recommendation") or \
                   previous_analysis.get("committee_output", {}).get("rating")

        current_conf = current_analysis.get("committee_output", {}).get("confidence", 0)
        prev_conf = previous_analysis.get("committee_output", {}).get("confidence", 0)

        current_regime = current_analysis.get("regime_data", {}).get("regime")
        prev_regime = previous_analysis.get("regime_data", {}).get("regime")

        current_risks = current_analysis.get("committee_output", {}).get("key_risks") or \
                        current_analysis.get("committee_output", {}).get("top_risks") or []
        prev_risks = previous_analysis.get("committee_output", {}).get("key_risks") or \
                     previous_analysis.get("committee_output", {}).get("top_risks") or []

        new_risks = list(set(current_risks) - set(prev_risks))

        comparison = {
            "recommendation_changed": current_rec != prev_rec,
            "previous_rating": prev_rec,
            "current_rating": current_rec,
            "confidence_change": current_conf - prev_conf,
            "regime_changed": current_regime != prev_regime,
            "new_risks": new_risks
        }

        return comparison
