# controllers/app_controller.py
# Defines the AppController class, responsible for initializing and coordinating the application's core components.

from config.config_loader import load_config  # Loads configuration settings from a JSON file.
from adapters.mediapipe_adapter import MediaPipeAdapter  # Provides an interface to MediaPipe for pose/motion detection.
from kpi.kpi_factory import KpiFactory  # Creates KPI calculators based on configuration.
from kpi.kpi_manager import KpiManager  # Manages KPI calculators for performance metric computation.
from processors.frame_processor import FrameProcessor  # Processes video frames using MediaPipe and KPI calculators.
from ui.main_window import MainWindow  # Defines the main GUI window for the application.
import logging  # Enables logging for debugging and monitoring application behavior.

# Configure logging to display timestamp, log level, and message for debugging purposes.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class AppController:
    def __init__(self, config_path="config/config.json"):
        """Initialize the AppController with configuration and core components."""
        logging.info("Initializing AppController...")
        # Load configuration from the specified JSON file.
        self.config = load_config(config_path)
        logging.debug(f"Configuration loaded: {self.config.dict()}")
        
        # Initialize MediaPipe adapter for live mode with configuration settings.
        self.mediapipe_adapter = MediaPipeAdapter(mode="live", config=self.config.mediapipe)
        logging.debug("MediaPipeAdapter initialized.")
        
        # Create KPI calculators based on the loaded configuration.
        kpi_factory = KpiFactory(self.config.dict())
        calculators = kpi_factory.create_calculators()
        logging.debug(f"Calculators created: {[calc.name() for calc in calculators]}")
        
        # Initialize KPI manager and register all calculators for metric computation.
        self.kpi_manager = KpiManager()
        for calc in calculators:
            self.kpi_manager.register_calculator(calc)
        logging.debug("KpiManager initialized with calculators.")
        
        # Initialize frame processor with MediaPipe adapter and KPI manager.
        self.frame_processor = FrameProcessor(self.mediapipe_adapter, self.kpi_manager)
        logging.debug("FrameProcessor initialized.")
        
        # Group enabled KPIs by their group attribute for display in the UI.
        # Dynamically group enabled KPIs by their group attribute

        enabled_kpis = {}
        for calc in calculators:
            group = calc.group()
            if group not in enabled_kpis:
                enabled_kpis[group] = []
            enabled_kpis[group].append(calc.name())
        
        # Initialize the main window with the frame processor and grouped KPIs.
        self.main_window = MainWindow(self.frame_processor, enabled_kpis)
        logging.info("AppController successfully initialized.")
    
    def get_main_window(self):
        """Return the main window instance for display."""
        return self.main_window