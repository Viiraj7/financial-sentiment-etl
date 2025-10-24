#
# src/database/db_manager.py
# VERSION 2.0: Updated hash generation to include scraped date for temporal uniqueness.
#

import sqlite3
import hashlib
from datetime import datetime
import json

from src.utils.config_loader import load_config
from src.utils.logger import logger

config = load_config()
DB_PATH = config.get('database', {}).get('path', 'data/news_sentiment.db')
SCHEMA_PATH = config.get('database', {}).get('schema', 'src/database/schema.sql')

# --- UPDATED HASH FUNCTION ---
def _generate_hash(headline: str, url: str, scraped_date: str) -> str:
    """
    Generates a unique MD5 hash based on headline, URL, and scraped date.
    Including the date ensures temporal uniqueness for recurring headlines.

    Args:
        headline (str): The text of the article headline.
        url (str): The URL of the article.
        scraped_date (str): The date the article was scraped (YYYY-MM-DD format).

    Returns:
        str: A 32-character hexadecimal string representing the MD5 hash.
    """
    hash_input = f"{headline}-{url}-{scraped_date}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def create_database():
    """ Creates the database and table(s) based on the schema.sql file. """
    try:
        logger.info("Checking and creating database if it doesn't exist...")
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        logger.info(f"Database setup complete. Ready at {DB_PATH}")
    except FileNotFoundError:
        logger.error(f"FATAL: Schema file not found at {SCHEMA_PATH}.")
    except sqlite3.Error as e:
        logger.error(f"An error occurred during database creation: {e}")

# --- UPDATED INSERT FUNCTION ---
def insert_article(source: str, headline: str, article_url: str, finbert_result: dict):
    """
    Inserts a single news article and its sentiment analysis into the database.
    Prevents duplicates based on headline, URL, and scraped date hash.
    """
    scraped_timestamp = datetime.now()
    scraped_date_str = scraped_timestamp.strftime('%Y-%m-%d')
    
    # Generate the unique fingerprint using headline, URL, and date
    article_hash = _generate_hash(headline, article_url, scraped_date_str)
    
    sql = """
    INSERT OR IGNORE INTO news_sentiment (
        scraped_timestamp, 
        published_timestamp,
        article_hash, 
        source, 
        article_url,
        headline, 
        sentiment_label, 
        sentiment_score, 
        aspects_json,
        sentiment_model_version
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    model_version = "finbert_v1_base"
    params = (
        scraped_timestamp,
        None, # published_timestamp
        article_hash,
        source,
        article_url,
        headline,
        finbert_result.get('label'),
        finbert_result.get('score'),
        None, # aspects_json
        model_version
    )
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Inserted [{source}]: '{headline[:50]}...'")
        else:
            logger.debug(f"Duplicate ignored [{source}]: '{headline[:50]}...'")
            
    except sqlite3.Error as e:
        logger.error(f"Database error inserting article: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()