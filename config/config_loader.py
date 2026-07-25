import yaml
from pathlib import Path

def config_load():
    config_path = Path(__file__).parent / "config.yaml"

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
