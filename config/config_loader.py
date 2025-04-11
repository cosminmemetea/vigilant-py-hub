# config/config_loader.py
# Defines configuration models and a function to load application settings from a JSON file.

from pydantic import BaseModel  # Provides data validation and parsing for configuration models.
from typing import List, Dict, Optional  # Enables type hints for lists, dictionaries, and optional fields.

class KpiConfig(BaseModel):
    """Configuration model for a single KPI (Key Performance Indicator)."""
    name: str  # Unique name of the KPI.
    enabled: bool = True  # Whether the KPI is active (defaults to True).
    group: str  # Category or group the KPI belongs to for organization.
    params: Optional[Dict] = {}  # Optional parameters for KPI customization (defaults to empty dict).

class AppConfig(BaseModel):
    """Top-level configuration model for the application."""
    mediapipe: Dict  # Configuration settings for the MediaPipe adapter.
    kpis: List[KpiConfig]  # List of KPI configurations for the application.

def load_config(path: str) -> AppConfig:
    """Load and parse application configuration from a JSON file.

    Args:
        path (str): Path to the JSON configuration file.

    Returns:
        AppConfig: Parsed configuration object validated against the AppConfig model.
    """
    with open(path, "r") as f:  # Open the JSON file in read mode.
        import json  # Import json module for parsing the file.
        data = json.load(f)  # Read and parse the JSON data into a Python dictionary.
        return AppConfig(**data)  # Validate and convert the data into an AppConfig instance.