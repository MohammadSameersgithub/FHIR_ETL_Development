import json
import requests
from config.config_loader import config_load

class Paginator:

    def __init__(self):

        self.config = config_load()
        self.base_url =  self.config.get('api').get('base_url')
        self.page_size =  self.config.get('api').get('page_size')
        self.timeout =  self.config.get('api').get('timeout')


    def fetch_pages(self, resource, params=None):
        
        url = f"{self.base_url.rstrip("/")}/{resource.lstrip("/")}"

        response = requests.get(url = url,
                params = {"_count": 5},
                timeout = self.timeout)
        print(response.url)
        print(response.status_code)
        print(response.text)
        bundle = response.json()
        
        return bundle
