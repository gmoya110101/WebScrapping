import requests
import pandas as pd
import re
import logging
from bs4 import BeautifulSoup
from time import sleep
from functools import reduce
from product import Product


logger = logging.getLogger("Web_Scrapper")
logger.setLevel(logging.INFO)
format = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class WebScrapper():
    def __init__(self, cfg:dict): 
        self.cfg:dict = cfg
        self.headers:dict = self.cfg["globals"]["headers"]
        self.timeout:int = self.cfg["globals"]["timeout"]
        self.product:str = self.cfg["globals"]["product"]
        self.astypes:dict = self.cfg["globals"]["astypes"]
        self.stores:dict = self.cfg["stores"]
        
    def replace_values(self, string:str, values:dict)->str:
        pattern = values["pattern"]
        repl = values["repl"]
        return re.sub(pattern, repl, string).strip()
        
    def request(self, url:str):
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
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
                value = reduce(self.replace_values, cfg[field]["replaces"], value)
            
            return value
        
        except Exception as e:
            logger.error(f"Without property: {field}")
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
            print(URL)
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
            print(products)

        df = pd.DataFrame(products)
        df = df.astype(self.astypes)
        return df
        
    def run(self):
        store:dict = self.stores["benavides"]["cfg"]
        products = self.extract_products(store)
        print(products)
       
        