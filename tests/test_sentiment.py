#
# tests/test_sentiment.py
# VERSION 2.1: Corrected expected scores based on actual softmax results.
#

import unittest
from unittest.mock import patch, MagicMock
import torch

from src.nlp import sentiment

class TestSentimentAnalysis(unittest.TestCase):
    """ Test suite using mocking for analyze_sentiment. """

    @patch('src.nlp.sentiment._initialize_model')
    def test_analyze_sentiment_positive(self, mock_initialize_model):
        """ Tests positive case with proper mocking. """
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        sentiment.tokenizer = mock_tokenizer_instance
        sentiment.model = mock_model_instance

        mock_output = MagicMock()
        mock_output.logits = torch.tensor([[5.0, -1.0, -1.0]])
        mock_model_instance.return_value = mock_output
        mock_tokenizer_instance.return_value = {
            'input_ids': torch.tensor([[101]]),
            'attention_mask': torch.tensor([[1]])
        }

        result = sentiment.analyze_sentiment("This company is performing great!")

        self.assertIsNotNone(result)
        self.assertEqual(result.get('label'), 'Positive')
        # --- THE FIX: Use the actual calculated score ---
        self.assertAlmostEqual(result.get('score', 0), 0.995067, places=6)

        mock_initialize_model.assert_not_called()
        mock_tokenizer_instance.assert_called_once()
        mock_model_instance.assert_called_once()


    @patch('src.nlp.sentiment._initialize_model')
    def test_analyze_sentiment_negative(self, mock_initialize_model):
        """ Tests negative case with proper mocking. """
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        sentiment.tokenizer = mock_tokenizer_instance
        sentiment.model = mock_model_instance

        mock_output = MagicMock()
        mock_output.logits = torch.tensor([[-1.0, 5.0, -1.0]])
        mock_model_instance.return_value = mock_output
        mock_tokenizer_instance.return_value = {
            'input_ids': torch.tensor([[101]]),
            'attention_mask': torch.tensor([[1]])
        }

        result = sentiment.analyze_sentiment("Terrible results reported.")

        self.assertIsNotNone(result)
        self.assertEqual(result.get('label'), 'Negative')
        # --- THE FIX: Use the actual calculated score ---
        # Note: The score is the same because the input logits [-1, 5, -1]
        # produce the same max probability after softmax as [5, -1, -1] does for its max.
        self.assertAlmostEqual(result.get('score', 0), 0.995067, places=6)

        mock_initialize_model.assert_not_called()
        mock_tokenizer_instance.assert_called_once()
        mock_model_instance.assert_called_once()

if __name__ == '__main__':
    unittest.main()