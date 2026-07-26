import json
import requests
from config.config_loader import config_load
from utils.logger import LoggerFactory

class Paginator:

    def __init__(self):

        self.config = config_load()
        self.base_url =  self.config.get('api').get('base_url')
        self.page_size =  self.config.get('api').get('page_size')
        self.timeout =  self.config.get('api').get('timeout')
        logger = LoggerFactory()
        self.logger = logger.get_logger(__name__)


    def fetch_pages(self, resource, params=None):
        
        url = f"{self.base_url.rstrip("/")}/{resource.lstrip("/")}"
        try:
            while url:
                response = requests.get(url = url,
                        params = params,
                        timeout = self.timeout)
                response.raise_for_status()
                bundle = response.json()
                record_count = len(bundle.get("entry", []))
                self.logger.info(f"Received {record_count} records from {resource}")
                yield bundle
                url = None
                params = None
                next_url = None
                for link in bundle.get("link",[]):
                    if link.get("relation") == 'next':
                        next_url = link.get("url")
                        break     # break is for FOR loop
                if next_url is None:
                        self.logger.info(
                            f"No more pages for {resource}. ")
                
                url = next_url
        except Exception as error:
            self.logger.info("Failed to get the response")
            self.logger.info(f"{url} \n response status code: {response.status_code}")
            raise error
