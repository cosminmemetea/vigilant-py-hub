from pydantic import BaseModel
from typing import List, Dict, Optional

class KpiConfig(BaseModel):
    name: str
    enabled: bool = True
    group: str
    params: Optional[Dict] = {}

class AppConfig(BaseModel):
    mediapipe: Dict
    kpis: List[KpiConfig]

def load_config(path: str) -> AppConfig:
    with open(path, "r") as f:
        import json
        data = json.load(f)
        return AppConfig(**data)