#
# main.py
#
# This is the main entry point for the entire application.
# Its purpose is to initialize the necessary components and start the ETL pipeline.
#

# Local application/library specific imports
from src.database import db_manager
from src.etl import pipeline
from src.utils.logger import logger

def main():
    """
    The main function that orchestrates the application startup.
    """
    logger.info("Application starting...")
    
    # --- 1. Initialize Database ---
    # It's a best practice to ensure the database schema is in place
    # before any data processing begins. This function is idempotent,
    # meaning it's safe to run even if the database already exists.
    db_manager.create_database()
    
    # --- 2. Run the ETL Pipeline ---
    # This call kicks off the main logic of the application:
    # Extract -> Transform -> Load
    pipeline.run_pipeline()
    
    logger.info("Application finished its run.")

# The __name__ == "__main__" block is a standard Python construct.
# It ensures that the code inside this block only runs when the script
# is executed directly (e.g., `python main.py`).
if __name__ == "__main__":
    main()