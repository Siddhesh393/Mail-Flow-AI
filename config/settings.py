import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_settings():
    if not CONFIG_PATH.exists():
        return {}

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
