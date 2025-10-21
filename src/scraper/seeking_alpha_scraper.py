#
# src/scraper/seeking_alpha_scraper.py
# A simple and reliable scraper for the static Seeking Alpha market news page.
#
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from src.utils.config_loader import load_config
from src.utils.logger import logger

config = load_config()
SCRAPER_CONFIG = config.get('scraper', {})
SA_URL = SCRAPER_CONFIG.get('sources', {}).get('seeking_alpha')
USER_AGENT = SCRAPER_CONFIG.get('user_agent')

def scrape_seeking_alpha() -> List[Dict[str, str]]:
    articles = []
    logger.info(f"Starting scrape for Seeking Alpha: {SA_URL}")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(SA_URL, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all article containers
        # On Seeking Alpha, these are <article> tags with a specific data-test-id
        article_tags = soup.find_all('article', attrs={'data-test-id': 'post-list-article'})
        if not article_tags:
            logger.warning("Could not find news articles on Seeking Alpha.")
            return []

        for tag in article_tags:
            # The headline is in the first <a> tag inside a <div> with a specific data-test-id
            if headline_div := tag.find('div', attrs={'data-test-id': 'post-list-title'}):
                if link_tag := headline_div.find('a'):
                    if href := link_tag.get('href'):
                        full_url = "https://seekingalpha.com" + href
                        articles.append({"headline": link_tag.get_text(strip=True), "url": full_url})

        logger.info(f"Successfully scraped {len(articles)} articles from Seeking Alpha.")
    except Exception as e:
        logger.error(f"An error occurred during Seeking Alpha scraping: {e}", exc_info=True)
    return articles