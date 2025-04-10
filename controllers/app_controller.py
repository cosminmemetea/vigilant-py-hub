from config.config_loader import load_config
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
        self.config = load_config(config_path)
        logging.debug(f"Configuration loaded: {self.config.dict()}")
        
        self.mediapipe_adapter = MediaPipeAdapter(mode="live", config=self.config.mediapipe)
        logging.debug("MediaPipeAdapter initialized.")
        
        kpi_factory = KpiFactory(self.config.dict())
        calculators = kpi_factory.create_calculators()
        logging.debug(f"Calculators created: {[calc.name() for calc in calculators]}")
        
        self.kpi_manager = KpiManager()
        for calc in calculators:
            self.kpi_manager.register_calculator(calc)
        logging.debug("KpiManager initialized with calculators.")
        
        self.frame_processor = FrameProcessor(self.mediapipe_adapter, self.kpi_manager)
        logging.debug("FrameProcessor initialized.")
        
        # Dynamically group enabled KPIs by their group attribute
        enabled_kpis = {}
        for calc in calculators:
            group = calc.group()
            if group not in enabled_kpis:
                enabled_kpis[group] = []
            enabled_kpis[group].append(calc.name())
        self.main_window = MainWindow(self.frame_processor, enabled_kpis)
        logging.info("AppController successfully initialized.")
    
    def get_main_window(self):
        return self.main_window