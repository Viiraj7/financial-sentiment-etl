#
# src/scraper/yahoo_scraper.py
# VERSION 4.0: Final production version with page load strategy and robust cookie handling.
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
from selenium.common.exceptions import TimeoutException

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

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    
    # --- THE ULTIMATE FIX 1: Page Load Strategy ---
    # This tells Selenium not to wait for the full page to load (with ads, trackers, etc.).
    # It will proceed as soon as the main HTML is ready, which is much faster and more stable.
    options.page_load_strategy = 'eager'

    driver = None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # --- THE ULTIMATE FIX 2: Page Load Timeout ---
        # Set a maximum time for the page to load. If it takes longer, it will stop and raise an error.
        # This prevents the script from hanging indefinitely.
        driver.set_page_load_timeout(30)

        logger.info("Selenium WebDriver started successfully.")
        driver.get(YAHOO_URL)
        
        try:
            cookie_wait = WebDriverWait(driver, 10) # Wait up to 10 seconds for the banner
            # This is a more robust selector for the "Accept all" button.
            accept_button = cookie_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'form[action="/consent"] .btn.primary')))
            accept_button.click()
            logger.info("Clicked the cookie consent 'Accept all' button.")
            time.sleep(2) # Give the page a moment to react
        except TimeoutException:
            logger.debug("Cookie consent banner not found or already handled.")
        
        content_wait = WebDriverWait(driver, 20)
        content_wait.until(EC.presence_of_element_located((By.ID, "Fin-Stream")))

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