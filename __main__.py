## config.yaml test
from config.config_loader import config_load
import logging

config = config_load()
# print(config)

# logger test
from utils.logger import LoggerFactory

# logger = LoggerFactory()
# logger = logger.get_logger(__name__, level=logging.DEBUG)
# logger.info("testing the log")
# logger.error("testing the exception log")
# try:
#     1 / 0
# except Exception:
#     logger.exception("testing the exception log")
# logger.debug("testing the debug log")
# logger.warning("testing the warning log")

from utils.checkpoint import CheckpointManager
from datetime import datetime, UTC
# checkpoint_manager = CheckpointManager()
# checkpoint = checkpoint_manager.load()
# checkpoint_manager.save(resource = 'Patient',
#                         checkpoint = checkpoint,
#                         last_successful_page = 20,
#                         total_records = 500,
#                         status = "NOT STARTED",
#                         last_successful_watermark = datetime.now(UTC).isoformat())
# checkpoint_manager.update_progress(resource = 'Patient',
#                             checkpoint = checkpoint,
#                         last_successful_page = 3)

from src.extractor.paginator import Paginator
from src.extractor.raw_writer import RawWriter
from src.extractor.extract import Extractor


paginator = Paginator()
raw_writer = RawWriter()
extract = Extractor()
extract = extract.run(resource = 'Patient')

# print(type(bundle))
# print(len(bundle.get('entry',[])))
# print(len(response.get('entry').get('resource')))

