from utils.logger import LoggerFactory
from config.config_loader import config_load
from datetime import datetime, UTC
from pathlib import Path
import json

class RawWriter:

    def __init__(self):

        self.config = config_load()    
        logger = LoggerFactory()
        self.logger = logger.get_logger(__name__)
        self.output_dir = Path(__file__).resolve().parents[2] / self.config['storage']['raw_path']

    def write(self, resource, bundle, page_number):
        extract_time = datetime.now(UTC).strftime("%Y-%m-%d")
        output_path = self.output_dir/f"{resource}/{extract_time}"
        output_path.mkdir(parents = True, exist_ok = True)
        self.logger.info(f"writing the file to {output_path}")
        output_file = output_path/f"page_{page_number:05d}.json"
        self.logger.info(f"writing {output_file}")
        with output_file.open("w",encoding="utf-8") as file:
            json.dump(bundle,file, indent=4)
        self.logger.info(f"successfully written the file {output_file}")
        return output_file

