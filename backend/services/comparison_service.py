class ComparisonService:
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

        comparison = {
            "recommendation_changed": current_rec != prev_rec,
            "previous_rating": prev_rec,
            "current_rating": current_rec,
            "confidence_change": current_conf - prev_conf,
            "regime_changed": current_regime != prev_regime
        }

        return comparison
