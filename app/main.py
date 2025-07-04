import logging
import sys
import json
from modules.web_scrapper import BaseWebScrapper


logger = logging.getLogger("Main")
logger.handlers.clear()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

logger.addHandler(handler)

def get_cfg(path:str) -> dict:
    return json.load(open(path))

def master():
    
    cfg = get_cfg("./conf.json")
    cfg = cfg["webscrapper"]["cfg"]
    scrapper = BaseWebScrapper(cfg=cfg, store="similares")
    df_similares = scrapper.run()
    # scrapper = WebScrapper(cfg=cfg, store="benavides")
    # df_benavides = scrapper.run()
    scrapper = BaseWebScrapper(cfg=cfg, store="del_ahorro")
    df_del_ahorro = scrapper.run()

if __name__ == "__main__":
    logger.info("------------------------------------------------------- STARTING PROGRAM -------------------------------------------------------")    
    master()
    logger.info("-------------------------------------------------------   END PROGRAM    -------------------------------------------------------")