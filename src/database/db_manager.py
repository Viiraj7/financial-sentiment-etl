#
# src/database/db_manager.py
#
# This script is the sole manager of the SQLite database. It handles
# creating the database from the schema and inserting new article data.
#

# Standard library imports
import sqlite3
import hashlib
from datetime import datetime
import json

# Local application/library specific imports
from src.utils.config_loader import load_config
from src.utils.logger import logger

# Load configuration settings
config = load_config()
DB_PATH = config.get('database', {}).get('path', 'data/news_sentiment.db')
SCHEMA_PATH = config.get('database', {}).get('schema', 'src/database/schema.sql')

def _generate_hash(headline: str) -> str:
    """
    Generates a unique MD5 hash for a given headline string.
    This serves as a unique fingerprint to prevent duplicate entries.

    Args:
        headline (str): The text of the article headline.

    Returns:
        str: A 32-character hexadecimal string representing the MD5 hash.
    """
    # encode() converts the string into bytes, which is required by hashlib
    return hashlib.md5(headline.encode()).hexdigest()

def create_database():
    """
    Creates the database and table(s) based on the schema.sql file.
    This is safe to run multiple times; it will not recreate existing tables.
    """
    try:
        logger.info("Checking and creating database if it doesn't exist...")
        # Read the SQL commands from our schema file
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        # Connect to the SQLite database (this will create the file if it doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute the entire SQL script from the schema file
        # This can include multiple commands (CREATE TABLE, CREATE INDEX, etc.)
        cursor.executescript(schema_sql)
        
        conn.commit()
        conn.close()
        logger.info(f"Database setup complete. Ready at {DB_PATH}")
    except FileNotFoundError:
        logger.error(f"FATAL: Schema file not found at {SCHEMA_PATH}. Cannot create database.")
    except sqlite3.Error as e:
        logger.error(f"An error occurred during database creation: {e}")

def insert_article(source: str, headline: str, article_url: str, finbert_result: dict):
    """
    Inserts a single news article and its sentiment analysis into the database.
    It prevents duplicates by checking the headline's hash.

    Args:
        source (str): The source of the news (e.g., 'Finviz').
        headline (str): The article's headline.
        article_url (str): The URL of the article.
        finbert_result (dict): A dictionary containing the FinBERT analysis
                               (e.g., {'label': 'Positive', 'score': 0.98}).
    """
    # Generate the unique fingerprint for the headline
    article_hash = _generate_hash(headline)
    scraped_timestamp = datetime.now()
    
    # Using 'INSERT OR IGNORE' is a highly efficient SQLite feature.
    # If the 'article_hash' already exists, the command does nothing and
    # does not raise an error. This is our primary defense against duplicates.
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
    
    # We will hardcode the model version for now.
    model_version = "finbert_v1_base"
    
    # For now, we don't have published_timestamp or aspects_json
    # so we will insert them as None.
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
        
        # cursor.rowcount will be 1 if a new row was inserted,
        # and 0 if the hash already existed and the row was ignored.
        if cursor.rowcount > 0:
            logger.info(f"Successfully inserted article from {source}: '{headline[:50]}...'")
        else:
            logger.debug(f"Article from {source} is a duplicate, ignored: '{headline[:50]}...'")
            
    except sqlite3.Error as e:
        logger.error(f"Database error while inserting article: {e}")
    finally:
        if conn:
            conn.close()