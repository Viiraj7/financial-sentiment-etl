# src/scraper/finviz_scraper.py
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
    articles: List[Dict[str, str]] = []
    if not FINVIZ_URL or not USER_AGENT:
        logger.error("Finviz URL or User-Agent not found in configuration.")
        return articles

    logger.info(f"Starting scrape for Finviz: {FINVIZ_URL}")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(FINVIZ_URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # New structure: find the section for news lines
        # Inspecting page shows multiple <div class="news"> or list of <a> maybe inside an unordered list
        # For example: <td width="100%"><table><tr><td><a href="..." target="_blank">Headline</a></td></tr>...</table></td>
        # So we’ll grab all <a> tags under the “news” table/tr area.

        # Approach 1: find table with class news-table (if still there) as fallback
        news_table = soup.find('table', class_='news-table')

        if news_table:
            logger.info("Found news-table via class 'news-table'. Using legacy selector.")
            links = news_table.find_all('a')
        else:
            # Approach 2: find using other structural clues
            logger.info("news-table not found; using alternate selector.")
            # From current FINVIZ page: all news items are inside <td width="100%"> under <table class="body-table"><tr><td>…
            # Let's find all td elements with width="100%" and then links inside
            links = []
            td100 = soup.find_all('td', attrs={'width': '100%'})
            for td in td100:
                # find anchor tags inside
                for a in td.find_all('a', href=True):
                    links.append(a)

        # Process anchor tags
        for tag in links:
            href = tag.get('href')
            text = tag.get_text(strip=True)
            if not href or not text:
                continue
            # Some links might be relative, convert to absolute
            if href.startswith('/'):
                href = f"https://finviz.com{href}"
            articles.append({
                "headline": text,
                "url": href
            })

        logger.info(f"Successfully scraped {len(articles)} articles from Finviz.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Finviz scraping: {e}", exc_info=True)
        return []

    return articles
