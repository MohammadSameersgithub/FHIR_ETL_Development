from pathlib import Path
from datetime import datetime, UTC
import json
from utils.logger import LoggerFactory


class CheckpointManager:

    def __init__(self):
        self.checkpoint_path = Path(__file__).resolve().parents[1] / "data/checkpoint/"
        self.checkpoint_file = self.checkpoint_path / "checkpoint.json"
        logger = LoggerFactory()
        self.logger = logger.get_logger(__name__)

    def _load(self):
        self.checkpoint_path.mkdir(parents=True, exist_ok=True)

        if not self.checkpoint_file.exists():
            self.logger.info("Checkpoint not found. Creating a new checkpoint.")
            checkpoint = {}
            with self.checkpoint_file.open('w', encoding="utf-8") as file:
                json.dump(checkpoint, file, indent=4)
            return checkpoint
        
        else:
            with self.checkpoint_file.open("r", encoding="utf-8") as file:
                checkpoint = json.load(file)
            return checkpoint

    def save(self, resource, last_successful_page):

        checkpoint = self._load()
        self.logger.info("Checkpoint loaded")
        checkpoint[resource] = {
            "last_successful_page" : last_successful_page,
            "last_successfull_timestamp" : datetime.now(UTC).isoformat(),
            "status" : "RUNNING"
            }
        with self.checkpoint_file.open("w", encoding="utf-8") as file:
            json.dump(checkpoint, file, indent=4)
        self.logger.info("Checkpoint saved successfully")

    def update_progress(self, resource, last_successful_page):

        checkpoint = self._load()
        self.logger.info("Checkpoint loaded")
        checkpoint[resource] = {
            "last_successful_page": last_successful_page,
            "last_extraction_timestamp" : datetime.now(UTC).isoformat(),
            "status" : "COMPLETED"
            }
        with self.checkpoint_file.open("w", encoding="utf-8") as file:
            json.dump(checkpoint, file, indent=4)
        self.logger.info("Checkpoint updated successfully")
