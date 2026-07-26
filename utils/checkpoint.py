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

    def load(self):

        self.checkpoint_path.mkdir(parents=True, exist_ok=True)

        if not self.checkpoint_file.exists():
            self.logger.info("Checkpoint not found. Creating a new checkpoint.")
            checkpoint = {}
            self._write_checkpoint(checkpoint)
            return checkpoint
        
        try:
            with self.checkpoint_file.open("r", encoding="utf-8") as file:
                checkpoint = json.load(file)

            if not isinstance(checkpoint, dict):
                raise ValueError("Checkpoint must be a JSON object.")

            return checkpoint

        except (json.JSONDecodeError, ValueError) as error:
            self.logger.error(
                f"Invalid checkpoint file: {error}")
            raise

    def save(self, resource, checkpoint, last_successful_page, 
                    total_records, status, last_successful_watermark=None):
        
        self.checkpoint_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("Checkpoint loaded")

        existing_checkpoint = checkpoint.get(resource,{})

        checkpoint_data = {
            "last_successful_page" : last_successful_page,
            "total_records" : total_records,
            "status" : status }

        existing_watermark = existing_checkpoint.get("last_successful_watermark")

        if last_successful_watermark is not None:
            checkpoint_data["last_successful_watermark"] = last_successful_watermark

        elif existing_watermark is not None:
            checkpoint_data["last_successful_watermark"] = existing_watermark

        checkpoint[resource] = checkpoint_data

        self._write_checkpoint(checkpoint)

        self.logger.info(
            f"Checkpoint saved successfully for resource: "
            f"{resource} | "
            f"status: {status} | "
            f"last successful page: {last_successful_page}"
        )

    ## atomic writes to avoid corrupted checkpoints
    def _write_checkpoint(self, checkpoint):
        temp_file = self.checkpoint_file.with_suffix(".tmp")

        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(checkpoint, file, indent=4)

        temp_file.replace(self.checkpoint_file)

