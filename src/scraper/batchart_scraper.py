#
# src/scraper/barchart_scraper.py
# A simple and reliable scraper for the static Barchart news page.
#
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from src.utils.config_loader import load_config
from src.utils.logger import logger

config = load_config()
SCRAPER_CONFIG = config.get('scraper', {})
BARCHART_URL = SCRAPER_CONFIG.get('sources', {}).get('barchart')
USER_AGENT = SCRAPER_CONFIG.get('user_agent')

def scrape_barchart() -> List[Dict[str, str]]:
    articles = []
    logger.info(f"Starting scrape for Barchart: {BARCHART_URL}")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(BARCHART_URL, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        news_divs = soup.select("div.bc-news-article")
        if not news_divs:
            logger.warning("Could not find news articles on Barchart.")
            return []

        for div in news_divs:
            if link_tag := div.find('a', class_='article-title'):
                if href := link_tag.get('href'):
                    full_url = "https://www.barchart.com" + href
                    articles.append({"headline": link_tag.get_text(strip=True), "url": full_url})
        
        logger.info(f"Successfully scraped {len(articles)} articles from Barchart.")
    except Exception as e:
        logger.error(f"An error occurred during Barchart scraping: {e}", exc_info=True)
    return articles