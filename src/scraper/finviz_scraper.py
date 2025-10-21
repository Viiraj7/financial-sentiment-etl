#
# src/scraper/finviz_scraper.py
# VERSION 2.2: Final corrected version with updated selectors.
#

import requests
from bs4 import BeautifulSoup
from typing import List, Dict

from src.utils.config_loader import load_config
from src.utils.logger import logger

config = load_config()
SCRAPER_CONFIG = config.get('scraper', {})
FINVIZ_URL = SCRAPER_CONFIG.get('sources', {}).get('finviz')
USER_AGENT = SCRAPER_CONFIG.get('user_agent')

def scrape_finviz() -> List[Dict[str, str]]:
    articles = []
    if not FINVIZ_URL or not USER_AGENT:
        logger.error("Finviz URL or User-Agent not found in configuration.")
        return articles

    logger.info(f"Starting scrape for Finviz: {FINVIZ_URL}")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(FINVIZ_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # THE FIX: Updated class name to 'news-table'
        news_table = soup.find('table', class_='news-table')
        
        if not news_table:
            logger.warning("Could not find the news table on the Finviz page.")
            return articles

        # THE FIX: Updated class name to 'news-tab-link'
        all_headline_tags = news_table.find_all('a', class_='news-tab-link')
        
        for tag in all_headline_tags:
            articles.append({
                "headline": tag.text.strip(),
                "url": tag['href']
            })
            
        logger.info(f"Successfully scraped {len(articles)} articles from Finviz.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during Finviz scraping: {e}", exc_info=True)
        return []
    
    return articles