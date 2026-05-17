import os
from apexlol_scraper import scrape_all_champions
from config import APEXLOL_CACHE_DIR

scrape_all_champions(APEXLOL_CACHE_DIR)
print("Finished scraping all champions!")
print(f"Cache dir: {APEXLOL_CACHE_DIR}")
