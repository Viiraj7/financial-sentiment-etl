#
# src/scraper/yahoo_scraper.py
#
# This script contains the logic for scraping news headlines from the
# dynamic Yahoo Finance news page, which requires browser automation.
# VERSION 2.0: Upgraded to use Explicit Waits and more precise selectors.
#

# Standard library imports
import time
from typing import List, Dict

# Third-party imports
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
# --- IMPROVEMENT 1: Import tools for Explicit Waits ---
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Local application/library specific imports
from src.utils.config_loader import load_config
from src.utils.logger import logger

# Load configuration
config = load_config()
SCRAPER_CONFIG = config.get('scraper', {})
YAHOO_URL = SCRAPER_CONFIG.get('sources', {}).get('yahoo')
USER_AGENT = SCRAPER_CONFIG.get('user_agent')
SCROLL_COUNT = SCRAPER_CONFIG.get('yahoo_scraper', {}).get('scroll_count', 3)
SCROLL_DELAY = SCRAPER_CONFIG.get('yahoo_scraper', {}).get('scroll_delay', 2)

def scrape_yahoo() -> List[Dict[str, str]]:
    """
    Scrapes the Yahoo Finance news page using Selenium to handle infinite scrolling.
    Uses explicit waits for efficiency and robustness.

    Returns:
        A list of dictionaries, where each represents an article with its
        'headline' and 'url'. Returns an empty list on failure.
    """
    articles = []
    if not YAHOO_URL or not USER_AGENT:
        logger.error("Yahoo URL or User-Agent not found in configuration.")
        return articles

    logger.info(f"Starting scrape for Yahoo Finance: {YAHOO_URL}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.info("Selenium WebDriver started successfully in headless mode.")
        
        driver.get(YAHOO_URL)
        
        # --- IMPROVEMENT 1: Implement Explicit Wait ---
        # We create a wait object with a 10-second timeout.
        wait = WebDriverWait(driver, 10)
        # We tell it to wait until the main news container is present on the page.
        # This is much more reliable than a fixed time.sleep().
        wait.until(EC.presence_of_element_located((By.ID, "Fin-Stream")))

        logger.info(f"Scrolling {SCROLL_COUNT} times to load dynamic content...")
        for _ in range(SCROLL_COUNT):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_DELAY) # A short sleep here is okay to allow new items to render

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # --- IMPROVEMENT 2: Use a More Precise CSS Selector ---
        # Instead of finding all <h3> tags, we first find the main news container.
        # This makes our scraping much more targeted and robust.
        news_container = soup.find('div', id='Fin-Stream')
        
        if not news_container:
            logger.warning("Could not find the main news container ('Fin-Stream') on the page.")
            return []

        # Now, we only search for headlines *within* that specific container.
        headline_items = news_container.find_all('li', class_='js-stream-content')

        for item in headline_items:
            link_tag = item.find('a')
            if link_tag and link_tag.has_attr('href'):
                headline_text = link_tag.text.strip()
                if len(headline_text) > 20: 
                    base_url = "https://finance.yahoo.com"
                    url = link_tag['href']
                    if not url.startswith('http'):
                        url = base_url + url
                    
                    articles.append({
                        "headline": headline_text,
                        "url": url
                    })

        logger.info(f"Successfully scraped {len(articles)} articles from Yahoo Finance.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during Yahoo scraping: {e}")
        return []
    finally:
        if driver:
            driver.quit()
            logger.info("Selenium WebDriver closed.")
            
    return articles
