#
# src/etl/pipeline.py
#
# This script orchestrates the entire ETL process, connecting all the
# individual modules to form a cohesive data pipeline.
#

# --- 1. Imports ---
# Import the functions from our other modules
from src.scraper import finviz_scraper, yahoo_scraper
from src.nlp import sentiment
from src.database import db_manager
from src.utils.logger import logger

def run_pipeline():
    """
    Executes the full ETL (Extract, Transform, Load) pipeline.
    """
    logger.info("=============================================")
    logger.info("====== Starting ETL Pipeline Run ======")
    logger.info("=============================================")
    
    # --- 2. EXTRACT ---
    # Call both scrapers to get lists of raw article data.
    logger.info("--- Phase 1: EXTRACT ---")
    finviz_articles = finviz_scraper.scrape_finviz()
    yahoo_articles = yahoo_scraper.scrape_yahoo()
    
    # Combine the lists into one master list for processing.
    all_articles = finviz_articles + yahoo_articles
    
    if not all_articles:
        logger.warning("No articles found from any source. Ending pipeline run.")
        return
        
    logger.info(f"Extracted a total of {len(all_articles)} articles.")
    
    # --- 3. TRANSFORM and LOAD ---
    # Loop through each article one-by-one to process and save it.
    logger.info("--- Phase 2 & 3: TRANSFORM and LOAD ---")
    
    processed_count = 0
    for article in all_articles:
        headline = article.get('headline')
        url = article.get('url')
        source = 'Finviz' if 'finviz.com' in url else 'Yahoo'
        
        # Basic validation to ensure we have a headline to process.
        if not headline:
            logger.warning(f"Skipping article with no headline from source: {source}")
            continue

        logger.debug(f"Processing article: '{headline[:60]}...'")

        # --- TRANSFORM ---
        # Call our NLP module to get the sentiment analysis.
        finbert_result = sentiment.analyze_sentiment(headline)
        
        # If the analysis fails for any reason, finbert_result will be empty.
        # We log a warning and skip to the next article.
        if not finbert_result:
            logger.warning(f"Sentiment analysis failed for headline: '{headline}'")
            continue
            
        # --- LOAD ---
        # Call our database manager to insert the processed data.
        # The db_manager handles duplicate prevention internally.
        db_manager.insert_article(
            source=source,
            headline=headline,
            article_url=url,
            finbert_result=finbert_result
        )
        processed_count += 1

    logger.info(f"Successfully processed and attempted to load {processed_count} articles.")
    logger.info("====== ETL Pipeline Run Finished ======")