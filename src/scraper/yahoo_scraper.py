#
# src/scraper/yahoo_scraper.py
# VERSION 2.3: Added stability options to prevent SSL/handshake errors.
#

import time
from typing import List, Dict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.config_loader import load_config
from src.utils.logger import logger

config = load_config()
SCRAPER_CONFIG = config.get('scraper', {})
YAHOO_URL = SCRAPER_CONFIG.get('sources', {}).get('yahoo')
USER_AGENT = SCRAPER_CONFIG.get('user_agent')
SCROLL_COUNT = SCRAPER_CONFIG.get('yahoo_scraper', {}).get('scroll_count', 3)
SCROLL_DELAY = SCRAPER_CONFIG.get('yahoo_scraper', {}).get('scroll_delay', 2)

def scrape_yahoo() -> List[Dict[str, str]]:
    articles = []
    if not YAHOO_URL or not USER_AGENT:
        logger.error("Yahoo URL or User-Agent not found in configuration.")
        return articles

    logger.info(f"Starting scrape for Yahoo Finance: {YAHOO_URL}")

    # --- THE FIX: ADDED STABILITY OPTIONS ---
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # These arguments are crucial for preventing common SSL/handshake errors.
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')

    driver = None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.info("Selenium WebDriver started successfully.")
        driver.get(YAHOO_URL)
        
        wait = WebDriverWait(driver, 20) # Increased timeout
        wait.until(EC.presence_of_element_located((By.ID, "Fin-Stream")))

        logger.info(f"Scrolling {SCROLL_COUNT} times to load dynamic content...")
        for _ in range(SCROLL_COUNT):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_DELAY)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        news_container = soup.find('div', id='Fin-Stream')
        if not news_container:
            logger.warning("Could not find the main news container on the page.")
            return []

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
                    articles.append({"headline": headline_text, "url": url})

        logger.info(f"Successfully scraped {len(articles)} articles from Yahoo Finance.")

    except Exception as e:
        logger.error(f"An unexpected error during Yahoo scraping: {e}", exc_info=True)
        return []
    finally:
        if driver:
            driver.quit()
            logger.info("Selenium WebDriver closed.")
            
    return articles