import feedparser
from typing import List, Dict
from src.utils.logger import logger
from src.utils.config_loader import load_config

config = load_config()
SCRAPER_CONFIG = config.get('scraper', {})
RSS_URL = SCRAPER_CONFIG.get('sources', {}).get('yahoo_rss')

def scrape_yahoo_rss() -> List[Dict[str, str]]:
    articles: List[Dict[str, str]] = []
    
    if not RSS_URL:
        logger.error("Yahoo RSS URL not found in configuration.")
        return articles

    logger.info(f"Starting RSS scrape for Yahoo Finance: {RSS_URL}")
    
    try:
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries:
            headline = entry.get("title")
            url = entry.get("link")
            if headline and url:
                articles.append({"headline": headline, "url": url})

        logger.info(f"Successfully scraped {len(articles)} articles from Yahoo RSS.")

    except Exception as e:
        logger.error(f"Error scraping Yahoo RSS feed: {e}", exc_info=True)
    
    return articles
