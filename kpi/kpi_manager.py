# kpi/kpi_manager.py
class KpiManager:
    def __init__(self):
        self.calculators = {}
        self.observers = []  # Observers can be UI components

    def register_calculator(self, calculator):
        self.calculators[calculator.name()] = calculator

    def calculate_all(self, landmarks, image_size) -> dict:
        results = {}
        for name, calc in self.calculators.items():
            results[name] = calc.calculate(landmarks, image_size)
        self.notify_observers(results)
        return results

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, results):
        for observer in self.observers:
            observer.update(results)