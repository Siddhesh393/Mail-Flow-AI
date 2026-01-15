import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

def load_settings():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
