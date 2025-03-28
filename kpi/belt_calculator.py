from kpi.kpi_calculator import KpiCalculator

class BeltCalculator(KpiCalculator):
    def name(self) -> str:
        return "belt"
    
    def calculate(self, landmarks, image_size , frame=None) -> str:
        # Placeholder for belt status.
        return "0"