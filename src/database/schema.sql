--
-- src/database/schema.sql
--
-- This file defines the PRODUCTION-GRADE structure of our database table,
-- specifically designed to store the rich output from a FinBERT model.
--

CREATE TABLE IF NOT EXISTS news_sentiment (
    -- 'id' is the primary key for our database's internal use.
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 'scraped_timestamp' is when OUR system processed the article.
    scraped_timestamp DATETIME NOT NULL,

    -- 'published_timestamp' is when the article was originally published.
    published_timestamp DATETIME NULL,

    -- 'article_hash' is a unique fingerprint of the headline to prevent duplicates.
    -- The 'UNIQUE' constraint is a database rule that rejects duplicate entries.
    article_hash TEXT NOT NULL UNIQUE,

    -- 'source' is where we got the news from (e.g., 'Finviz', 'Yahoo').
    source TEXT NOT NULL,

    -- 'article_url' is the direct link to the source article for traceability.
    article_url TEXT NULL,

    -- 'headline' stores the full text of the news headline.
    headline TEXT NOT NULL,

    -- === FINBERT OUTPUT COLUMNS ===

    -- 'sentiment_label' stores the classification from FinBERT (e.g., 'Positive', 'Negative', 'Neutral').
    sentiment_label TEXT NOT NULL,

    -- 'sentiment_score' stores the confidence of the FinBERT model in its label (e.g., 0.98).
    -- This is much more informative than a simple compound score.
    sentiment_score REAL NOT NULL,

    -- 'aspects_json' stores the full, detailed Aspect-Based Sentiment Analysis (ABSA) results.
    -- We store it as a JSON text string, which is a flexible and powerful pattern.
    -- Example: '[{"entity": "Apple", "aspect": "iPhone sales", "sentiment": "Positive"}]'
    aspects_json TEXT NULL,

    -- 'sentiment_model_version' tracks which model produced the score (e.g., "finbert_v1").
    sentiment_model_version TEXT NOT NULL
);

-- === INDEXES for PERFORMANCE ===

-- Creates an index on the timestamp column for fast time-based queries.
CREATE INDEX IF NOT EXISTS idx_scraped_timestamp ON news_sentiment (scraped_timestamp);

-- Creates an index on the source for fast filtering by 'Finviz' or 'Yahoo'.
CREATE INDEX IF NOT EXISTS idx_source ON news_sentiment (source);