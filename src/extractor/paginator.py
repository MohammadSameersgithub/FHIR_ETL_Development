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
            response = requests.get(url = url,
                    params = params,
                    timeout = self.timeout)
            self.logger.info(f"{url} \n response status code: {response.status_code}")
            bundle = response.json()
            yield bundle
            url = None
            params = None
            for link in bundle.get("link",[]):
                if link["relation"] == 'next':
                    url = link["url"]
                    break     # break is for FOR loop
        except Exception as error:
            self.logger.info("Failed to get the response")
            self.logger.info(f"{url} \n response status code: {response.status_code}")
            raise error
