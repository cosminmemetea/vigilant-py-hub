import json
from adapters.mediapipe_adapter import MediaPipeAdapter
from kpi.kpi_factory import KpiFactory
from kpi.kpi_manager import KpiManager
from processors.frame_processor import FrameProcessor
from ui.main_window import MainWindow
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class AppController:
    def __init__(self, config_path="config/config.json"):
        logging.info("Initializing AppController...")
        with open(config_path, "r") as f:
            self.config = json.load(f)
            logging.debug(f"Configuration loaded: {self.config}")
        
        self.mediapipe_adapter = MediaPipeAdapter(mode="live", config=self.config.get("mediapipe", {}))
        logging.debug("MediaPipeAdapter initialized.")
        
        kpi_factory = KpiFactory(self.config)
        calculators = kpi_factory.create_calculators()
        logging.debug(f"Calculators created: {[calc.name() for calc in calculators]}")
        
        self.kpi_manager = KpiManager()
        for calc in calculators:
            self.kpi_manager.register_calculator(calc)
        logging.debug("KpiManager initialized with calculators.")
        
        self.frame_processor = FrameProcessor(self.mediapipe_adapter, self.kpi_manager)
        logging.debug("FrameProcessor initialized.")
        
        # Group enabled KPIs by category
        enabled_kpis = {
            "numeric": [kpi["name"] for kpi in self.config.get("kpis", []) if kpi.get("enabled", True) and kpi.get("group") == "numeric"],
            "binary": [kpi["name"] for kpi in self.config.get("kpis", []) if kpi.get("enabled", True) and kpi.get("group") == "binary"],
            "state": [kpi["name"] for kpi in self.config.get("kpis", []) if kpi.get("enabled", True) and kpi.get("group") == "state"]
        }
        self.main_window = MainWindow(self.frame_processor, enabled_kpis)
        logging.info("AppController successfully initialized.")
    
    def get_main_window(self):
        return self.main_window