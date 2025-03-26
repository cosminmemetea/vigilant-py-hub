# File: controllers/app_controller.py
import json
from adapters.mediapipe_adapter import MediaPipeAdapter
from kpi.kpi_factory import KpiFactory
from kpi.kpi_manager import KpiManager
from processors.frame_processor import FrameProcessor
from ui.main_window import MainWindow

class AppController:
    def __init__(self, config_path="config/config.json"):
        # Load configuration from JSON file.
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        # Initialize MediaPipe adapter with configuration.
        self.mediapipe_adapter = MediaPipeAdapter(mode="live", config=self.config.get("mediapipe"))
        
        # Create KPI calculators via the factory.
        kpi_factory = KpiFactory(self.config)
        calculators = kpi_factory.create_calculators()
        
        # Initialize KPI manager and register calculators.
        self.kpi_manager = KpiManager()
        for calc in calculators:
            self.kpi_manager.register_calculator(calc)
        
        # Initialize the frame processor.
        self.frame_processor = FrameProcessor(self.mediapipe_adapter, self.kpi_manager)
        
        # Create the main UI window and inject the frame processor.
        self.main_window = MainWindow(self.frame_processor)
    
    def get_main_window(self):
        return self.main_window
