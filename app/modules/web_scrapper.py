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
         
            value = item.find(**cfg[field]["elements"]).text
            
            if "replaces" in cfg[field]:
                value = reduce(self.replace_values, cfg[field]["replaces"], value)
            
            return value
        
        except Exception as e:
            logger.error(f"Without property: {field}")
            return None
    
    def get_product(self, item, cfg:dict)-> Product:
        # description = item.find(**cfg["description"]["elements"]).text
        # oldPrice = item.find(**cfg["old_price"]["elements"]).text
        # currentPrice = item.find(**cfg["current_price"]["elements"]).text
        
        # description = reduce(self.replace_values, cfg["description"]["replaces"], currentPrice)
        # oldPrice = reduce(self.replace_values, cfg["oldPrice"]["replaces"], currentPrice)
        # currentPrice = reduce(self.replace_values, cfg["current_price"]["replaces"], currentPrice)
        aux_item = {}
        
        for field in cfg:
            aux_item[field] = self.extract_item(item=item, cfg=cfg, field=field)
        print(aux_item)
        # product = Product(description = aux_item["description"],
        #                   old_price = aux_item["old_price"],
        #                   current_price = aux_item["description"],
        #                   link="")
        
        # return product
    
    def run(self):
        store:dict = self.stores["similares"]["cfg"]
        URL:str = store["url"]
        URL = self.replace_values(values= {"pattern": "#PRODUCT#", 
                                           "repl": self.product}, 
                                  string  = URL)
        page = 1
        products = []
        print(self.product)
        
        while True:
            
            URL = self.replace_values(values = {"pattern": "#PAGE#", 
                                               "repl": str(page)},
                                      string= URL)
            logger.info(URL)
            print(URL)
            response = self.request(URL)
                        
            if response.status_code != 200:
                logger.error(response.error)
            
            else:
                
                items = self.extract_all_items(markup= response.text, cfg=store["main"]["elements"])
                
                if not items:
                    print("Without items")
                    break
                print(f"{len(items)} products found on page {page}")
                
                for item in items:     
                    product = self.get_product(item, store["data"]).to_dict()           
                    # products.append(product)                    

                page += 1
                break
                sleep(1)