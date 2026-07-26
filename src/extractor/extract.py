from datetime import datetime, UTC
from src.extractor.paginator import Paginator
from src.extractor.raw_writer import RawWriter
from utils.checkpoint import CheckpointManager
from utils.logger import LoggerFactory
from config.config_loader import config_load


class Extractor:

    def __init__(self):

        self.config = config_load()
        self.base_url =  self.config.get('api').get('base_url')
        self.page_size =  self.config.get('api').get('page_size')
        self.initial_load_date = self.config.get('api').get('initial_load_date')
        logger = LoggerFactory()
        self.logger = logger.get_logger(__name__)
        self.paginator = Paginator()
        self.raw_writer = RawWriter()
        self.checkpoint_manager = CheckpointManager()
        
    def run(self, resource):

        extraction_start_timestamp = datetime.now(UTC).isoformat()
        checkpoint = self.checkpoint_manager.load()

        resource_checkpoint = checkpoint.get(resource, {})

        last_successful_watermark = resource_checkpoint.get("last_successful_watermark")
        last_successful_page = resource_checkpoint.get("last_successful_page",0)

        if last_successful_watermark is None:
            params = {"_count": self.page_size,
                        "_lastUpdated": f"ge{self.initial_load_date}"}
            self.logger.info(
                                f"Performing initial load for resource "
                                f"{resource} from "
                                f"{self.initial_load_date}"
                            )

        else:
            params = {"_count": self.page_size,
                        "_lastUpdated": last_successful_watermark}
            self.logger.info(
                                f"Performing incremental load for resource "
                                f"{resource} from "
                                f"{last_successful_watermark}"
                            )

        page_number = last_successful_page + 1 
        total_records = 0
        file_path = None
        try:
            for bundle in self.paginator.fetch_pages(resource = resource, params = params):
                file_path = self.raw_writer.write(resource = resource, 
                                    bundle = bundle, 
                                    page_number = page_number)
                records_in_page = len(bundle.get("entry",[]))
                total_records += records_in_page

                self.logger.info(
                                f"Resource: {resource} | "
                                f"Page: {page_number} | "
                                f"Records in page: {records_in_page} | "
                                f"Total records: {total_records} | "
                                f"File: {file_path}"
                            )
                page_number+=1
            self.checkpoint_manager.save(
                        resource=resource,
                        checkpoint=checkpoint,
                        last_successful_page=page_number - 1,
                        total_records=total_records,
                        status="COMPLETED",
                        last_successful_watermark=extraction_start_timestamp )

            self.logger.info(
                        f"Resource {resource} extraction completed "
                        f"successfully. "
                        f"Total records: {total_records}")

        except Exception as error:
            self.checkpoint_manager.save(
                        resource=resource,
                        checkpoint=checkpoint,
                        last_successful_page=page_number - 1,
                        total_records=total_records,
                        status="FAILED")

            self.logger.exception(
                        f"Resource {resource} extraction failed. "
                        f"Last successful page: "
                        f"{page_number - 1} | "
                        f"Total records processed: "
                        f"{total_records} | "
                        f"Last file: {file_path}")
            raise
