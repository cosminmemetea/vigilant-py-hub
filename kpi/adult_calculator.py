from kpi.kpi_calculator import KpiCalculator

class AdultCalculator(KpiCalculator):
    def name(self) -> str:
        return "adult"
    
    def calculate(self, landmarks, image_size, frame=None) -> str:
        # Simple placeholder: returns 'Adult' if landmarks exist.
        return "Adult" if landmarks is not None else "Unknown"
