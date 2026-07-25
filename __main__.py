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

# checkpoint_manager = CheckpointManager()

# checkpoint_manager.save(resource = 'Patient',
#                         last_successful_page = 3)
# checkpoint_manager.update_progress(resource = 'Patient',
#                         last_successful_page = 3)

from src.extractor.paginator import Paginator

paginator = Paginator()

bundle = paginator.fetch_pages(resource = 'Observation')

# print(bundle.keys())
# print(len(bundle.get('entry',[])))
# print(len(response.get('entry').get('resource')))


