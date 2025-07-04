import requests
import pandas as pd
import re
import logging
import sys
from bs4 import BeautifulSoup
from time import sleep
from functools import reduce
from product import Product


logger = logging.getLogger("Web_Scrapper")
logger.handlers.clear()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

logger.addHandler(handler)

class BaseWebScrapper():
    def __init__(self, store:str, cfg:dict): 
        self.cfg:dict = cfg
        self.headers:dict = self.cfg["globals"]["headers"]
        self.timeout:int = self.cfg["globals"]["timeout"]
        self.product:str = self.cfg["globals"]["product"]
        self.astypes:dict = self.cfg["globals"]["astypes"]
        self.store:str = store
        self.store_cfg:dict = self.cfg["stores"][self.store]["cfg"]
        
    def replace_values(self, string:str, values:dict)->str:
        return re.sub(string=string,**values).strip()
        
    def request(self, url:str):
        try:
            response = requests.get(url, 
                                    headers=self.headers, 
                                    timeout=self.timeout)
            response.raise_for_status()  # Raise an error for bad responses
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        
    def extract_all_items(self, markup:str, cfg:dict):             
        html = BeautifulSoup(markup, self.cfg["globals"]["parser"])        
        items = html.find_all(**cfg)
        return items
    
    def extract_item(self, item, cfg:dict, field:str) -> str:
        try:
            element:dict = cfg[field]["elements"]
            
            if field == "link":
                value = item.find(element["name"])[element["prop"]]
                return value
            
            value = item.find(**element).text
            
            if "replaces" in cfg[field]:
                value = reduce(self.replace_values, 
                               cfg[field]["replaces"], 
                               value)
            
            return value
        
        except Exception as e:
            logger.warning(f"Without property: {field}")
            return None
    
    def get_product(self, item, cfg:dict)-> Product:
        aux_item = {}
        
        for field in cfg:
            aux_item[field] = self.extract_item(item=item, cfg=cfg, field=field)
        
        return aux_item
    
    def extract_products(self, store:dict)-> pd.DataFrame:
        page = 1
        products = []
        logger.info(f"Product to extract: {self.product}")
        
        while True:
            
            URL:str = store["url"]
            values = [{"pattern": "#PRODUCT#", "repl": self.product}, 
                      {"pattern": "#PAGE#", "repl": str(page)}]
            
            URL = reduce(self.replace_values, values, URL)
            logger.info(f"Getting data from: {URL}")
            response = self.request(URL)
                
            items = self.extract_all_items(markup= response.text, 
                                            cfg=store["main"]["elements"])
            
            if not items:
                logger.info(f"Without items in page {page}")
                break
            
            logger.info(f"{len(items)} products found on page {page}")
            
            for item in items:     
                product = self.get_product(item, store["data"])           
                products.append(product)                    

            page += 1
            sleep(1)
            

        df = pd.DataFrame(products)
        df = df.astype(self.astypes)
        return df
        
    def run(self) -> pd.DataFrame:
        logger.info(f"Getting data from {self.store}")
        store:dict = self.store_cfg
        products = self.extract_products(store)

        return products
       
        