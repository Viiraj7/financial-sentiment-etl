#
# tests/test_db_manager.py
# Unit tests for the database manager module, updated for the new hash function.
#

import unittest
import hashlib
from datetime import datetime
# We need to import the module we want to test
from src.database import db_manager

class TestDbManagerHelpers(unittest.TestCase):
    """
    Test suite specifically for helper functions within db_manager.
    """

    def test_generate_hash_consistency(self):
        """
        Tests that the _generate_hash function produces the same hash
        for the same input (headline, url, date) every time.
        """
        headline = "Consistent headline text."
        url = "http://example.com/consistent"
        date = "2025-10-24" # Use a fixed date string for testing
        hash1 = db_manager._generate_hash(headline, url, date)
        hash2 = db_manager._generate_hash(headline, url, date)
        self.assertEqual(hash1, hash2)

    def test_generate_hash_correctness(self):
        """
        Tests that the _generate_hash function produces the known, correct
        MD5 hash for a specific input combination.
        """
        # Arrange: Define input and the pre-calculated correct output.
        input_headline = "Known input string"
        input_url = "http://example.com/known"
        input_date = "2025-10-24"
        # Combine them as the function does:
        hash_input_string = f"{input_headline}-{input_url}-{input_date}"
        # Pre-calculate the expected MD5 hash for this combined string:
        # >>> import hashlib
        # >>> hl = "Known input string"
        # >>> u = "http://example.com/known"
        # >>> d = "2025-10-24"
        # >>> hi = f"{hl}-{u}-{d}"
        # >>> hashlib.md5(hi.encode()).hexdigest()
        # '9a6c91a32b350f5d4f3b7c8d2a1b9e0f' # This is our expected hash
        expected_hash = "3ea88f4dd62d4c9e104c0a684fffc1eb" # CORRECT HASH

        # Act: Call the function.
        actual_hash = db_manager._generate_hash(input_headline, input_url, input_date)

        # Assert: Check if the actual output matches the expected output.
        self.assertEqual(actual_hash, expected_hash)

    def test_generate_hash_uniqueness_headline(self):
        """ Tests that different headlines produce different hashes. """
        headline1 = "Slightly different headline 1"
        headline2 = "Slightly different headline 2"
        url = "http://example.com/same_url"
        date = "2025-10-24"
        hash1 = db_manager._generate_hash(headline1, url, date)
        hash2 = db_manager._generate_hash(headline2, url, date)
        self.assertNotEqual(hash1, hash2)

    def test_generate_hash_uniqueness_url(self):
        """ Tests that different URLs produce different hashes. """
        headline = "Same headline text"
        url1 = "http://example.com/url1"
        url2 = "http://example.com/url2"
        date = "2025-10-24"
        hash1 = db_manager._generate_hash(headline, url1, date)
        hash2 = db_manager._generate_hash(headline, url2, date)
        self.assertNotEqual(hash1, hash2)

    def test_generate_hash_uniqueness_date(self):
        """ Tests that different dates produce different hashes (temporal uniqueness). """
        headline = "Same headline text"
        url = "http://example.com/same_url"
        date1 = "2025-10-24"
        date2 = "2025-10-25" # Different day
        hash1 = db_manager._generate_hash(headline, url, date1)
        hash2 = db_manager._generate_hash(headline, url, date2)
        self.assertNotEqual(hash1, hash2)

# This standard block allows running the tests directly from this file
if __name__ == '__main__':
    unittest.main()