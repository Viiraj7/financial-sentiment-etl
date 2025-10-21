#
# test_model_download.py
#
# A simple, standalone script to download and cache the FinBERT model.
# This helps us debug network issues and gives a clear progress bar.
#

# We only need the transformers library for this.
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "ProsusAI/finbert"

print(f"--- Starting download for model: {MODEL_NAME} ---")
print("This is a large file (400MB+) and may take several minutes.")
print("Please be patient and let it complete.")

try:
    # This command will download the necessary files and show a progress bar.
    # If the files are already partially downloaded, it will resume.
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    
    print("\n--- SUCCESS! ---")
    print("The FinBERT model has been successfully downloaded and cached on your machine.")
    print("You can now run the main 'python main.py' script.")
    print("This one-time download will not happen again.")

except Exception as e:
    print(f"\n--- ERROR ---")
    print(f"An error occurred during the download: {e}")
    print("This is likely a network issue or a firewall blocking the download.")
    print("Please check your internet connection and try running this script again.")