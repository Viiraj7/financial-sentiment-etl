#
# tests/test_db_manager.py
# Unit tests for the database manager module.
#

import unittest
import hashlib
# We need to import the module we want to test
from src.database import db_manager

class TestDbManagerHelpers(unittest.TestCase):
    """
    Test suite specifically for helper functions within db_manager.
    """

    def test_generate_hash_consistency(self):
        """
        Tests that the _generate_hash function produces the same hash
        for the same input every time.
        """
        headline = "This is a test headline for consistency."
        hash1 = db_manager._generate_hash(headline)
        hash2 = db_manager._generate_hash(headline)
        # Assert that running it twice yields the identical result.
        self.assertEqual(hash1, hash2)

    def test_generate_hash_correctness(self):
        """
        Tests that the _generate_hash function produces the known, correct
        MD5 hash for a specific input string.
        """
        # Arrange: Define input and the pre-calculated correct output.
        input_headline = "Known input string"
        # I pre-calculated this MD5 hash using Python's hashlib directly:
        # >>> import hashlib
        # >>> hashlib.md5("Known input string".encode()).hexdigest()
        # 'd3b7c7f076a44a946e330f653a1a39dd'
        expected_hash = "d3b7c7f076a44a946e330f653a1a39dd"

        # Act: Call the function.
        actual_hash = db_manager._generate_hash(input_headline)

        # Assert: Check if the actual output matches the expected output.
        self.assertEqual(actual_hash, expected_hash)

    def test_generate_hash_uniqueness(self):
        """
        Tests that slightly different inputs produce different hashes.
        """
        headline1 = "Slightly different headline 1"
        headline2 = "Slightly different headline 2" # Only the number changed
        hash1 = db_manager._generate_hash(headline1)
        hash2 = db_manager._generate_hash(headline2)
        # Assert that the hashes are NOT equal.
        self.assertNotEqual(hash1, hash2)

# This standard block allows running the tests directly from this file
if __name__ == '__main__':
    unittest.main()