from src.scraper import yahoo_rss_scraper
from src.nlp import sentiment
from src.database import db_manager
from src.utils.logger import logger

def run_pipeline():
    logger.info("=============================================")
    logger.info("====== Starting ETL Pipeline Run ======")
    logger.info("=============================================")

    logger.info("--- Phase 1: EXTRACT ---")
    all_articles = yahoo_rss_scraper.scrape_yahoo_rss()

    if not all_articles:
        logger.warning("No articles were scraped. Ending pipeline run.")
        return

    logger.info(f"Extracted a total of {len(all_articles)} articles from Yahoo RSS.")

    logger.info("--- Phase 2 & 3: TRANSFORM and LOAD ---")
    processed_count = 0
    seen_urls = set()

    for article in all_articles:
        url = article.get('url')
        headline = article.get('headline')
        if not url or not headline or url in seen_urls:
            continue
        seen_urls.add(url)
        source = 'Yahoo RSS'

        logger.debug(f"Processing: '{headline[:60]}...'")
        finbert_result = sentiment.analyze_sentiment(headline)

        if not finbert_result:
            logger.warning(f"Sentiment analysis failed for: '{headline}'")
            continue

        db_manager.insert_article(
            source=source,
            headline=headline,
            article_url=url,
            finbert_result=finbert_result
        )
        processed_count += 1

    logger.info(f"Successfully processed and loaded {processed_count} unique articles.")
    logger.info("====== ETL Pipeline Run Finished ======")
