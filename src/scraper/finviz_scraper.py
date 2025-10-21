#
# src/scraper/finviz_scraper.py
#
# This script contains the logic for scraping news headlines from the
# static Finviz news page.
#

# Standard library imports
from typing import List, Dict

# Third-party imports
import requests
from bs4 import BeautifulSoup

# Local application/library specific imports
from src.utils.config_loader import load_config
from src.utils.logger import logger

# Load configuration
config = load_config()
SCRAPER_CONFIG = config.get('scraper', {})
FINVIZ_URL = SCRAPER_CONFIG.get('sources', {}).get('finviz')
USER_AGENT = SCRAPER_CONFIG.get('user_agent')

def scrape_finviz() -> List[Dict[str, str]]:
    """
    Scrapes the Finviz news page for headlines and their URLs.

    Returns:
        A list of dictionaries, where each dictionary represents an article
        with its 'headline' and 'url'. Returns an empty list on failure.
        e.g., [{"headline": "Some news...", "url": "http://example.com"}, ...]
    """
    articles = []
    if not FINVIZ_URL or not USER_AGENT:
        logger.error("Finviz URL or User-Agent not found in configuration.")
        return articles

    logger.info(f"Starting scrape for Finviz: {FINVIZ_URL}")

    try:
        # Set a User-Agent header to mimic a real browser request
        headers = {'User-Agent': USER_AGENT}
        
        # Perform the HTTP GET request to download the page
        response = requests.get(FINVIZ_URL, headers=headers)
        
        # This will raise an error if the request failed (e.g., 404, 500)
        response.raise_for_status()
        
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main news table by its class name
        # We inspect the page source in a browser to find these identifiers
        news_table = soup.find('table', class_='nn_news-table')
        if not news_table:
            logger.warning("Could not find the news table on the Finviz page.")
            return articles

        # Find all headline links within that table
        all_headline_tags = news_table.find_all('a', class_='nn-tab-link')
        
        for tag in all_headline_tags:
            articles.append({
                "headline": tag.text.strip(),  # .strip() removes whitespace
                "url": tag['href']             # Get the URL from the 'href' attribute
            })
            
        logger.info(f"Successfully scraped {len(articles)} articles from Finviz.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during request to Finviz: {e}")
        # Return an empty list to indicate failure
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred during Finviz scraping: {e}")
        return []
    
    return articles