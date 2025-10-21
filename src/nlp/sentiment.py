#
# src/nlp/sentiment.py
#
# This script handles the sentiment analysis using a pre-trained FinBERT model.
# It's designed to load the complex AI model only once for efficiency.
#

# Import necessary libraries from Hugging Face Transformers and PyTorch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Local application/library specific imports
from src.utils.logger import logger

# --- Model Configuration ---
# Define the name of the pre-trained FinBERT model we want to use.
# This model is hosted on the Hugging Face model hub.
MODEL_NAME = "ProsusAI/finbert"

# --- Global Variables for Singleton Pattern ---
# Loading a large model like FinBERT is slow and memory-intensive.
# We use a singleton pattern here: we'll load the model and tokenizer
# into these global variables the *first* time they are needed,
# and then reuse them for all subsequent calls. This is a crucial
# optimization for performance.
tokenizer = None
model = None

def _initialize_model():
    """
    Initializes the FinBERT tokenizer and model. This function is called
    internally only once when the first analysis is requested.
    """
    global tokenizer, model
    try:
        logger.info(f"Initializing FinBERT model: {MODEL_NAME}. This may take a moment...")
        # The tokenizer converts human-readable text into a format (tokens)
        # that the AI model can understand.
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # The model is the pre-trained neural network that performs the
        # sequence classification (in this case, sentiment analysis).
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        logger.info("FinBERT model initialized successfully.")
    except Exception as e:
        logger.error(f"FATAL: Failed to load FinBERT model. Error: {e}")
        # If the model can't be loaded, we should not continue.
        tokenizer = None
        model = None

def analyze_sentiment(headline: str) -> dict:
    """
    Analyzes the sentiment of a single headline using the loaded FinBERT model.

    Args:
        headline (str): The news headline to analyze.

    Returns:
        dict: A dictionary containing the 'label' (Positive, Negative, Neutral)
              and the 'score' (confidence of the model). Returns an empty
              dictionary if analysis fails.
    """
    global tokenizer, model

    # --- Initialization Check (Singleton Pattern) ---
    # Check if the model has been loaded yet. If not, load it.
    if tokenizer is None or model is None:
        _initialize_model()
        # If initialization failed, we cannot proceed.
        if tokenizer is None or model is None:
            return {}

    try:
        # 1. Tokenize the input text.
        # `padding=True` and `truncation=True` handle headlines of different lengths.
        # `return_tensors='pt'` returns the data as PyTorch tensors.
        inputs = tokenizer(headline, padding=True, truncation=True, return_tensors='pt', max_length=512)

        # 2. Get model predictions (inference).
        # We run the model without calculating gradients to save memory and speed up computation.
        with torch.no_grad():
            outputs = model(**inputs)

        # 3. Process the output.
        # The model outputs raw scores called "logits".
        # We apply the softmax function to convert these logits into probabilities (from 0 to 1).
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # 4. Get the results.
        # Find the highest probability and its corresponding label index.
        score = predictions.max().item()  # The highest probability
        label_index = predictions.argmax().item()  # The index of the highest probability

        # The model's configuration tells us what each index means.
        # For FinBERT: 0=Positive, 1=Negative, 2=Neutral
        labels = ['Positive', 'Negative', 'Neutral']
        label = labels[label_index]

        logger.debug(f"Analyzed '{headline[:50]}...': Label={label}, Score={score:.4f}")
        return {'label': label, 'score': score}

    except Exception as e:
        logger.error(f"Error during sentiment analysis for headline '{headline}': {e}")
        return {}