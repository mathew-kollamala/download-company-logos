"""
Tests for the Google Custom Search API integration.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.google_search import GoogleCustomSearch


class TestGoogleCustomSearch(unittest.TestCase):
    """Test cases for GoogleCustomSearch class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.search_engine_id = "test_search_engine_id"
        self.search_client = GoogleCustomSearch(self.api_key, self.search_engine_id)
    
    @patch('src.api.google_search.requests.get')
    def test_search_company_logo_success(self, mock_get):
        """Test successful logo search."""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'items': [
                {
                    'link': 'https://example.com/logo.png',
                    'title': 'Example Logo',
                    'image': {
                        'contextLink': 'https://example.com',
                        'width': 200,
                        'height': 100,
                        'thumbnailLink': 'https://example.com/thumbnail.png'
                    },
                    'fileFormat': 'image/png'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the method
        results = self.search_client.search_company_logo('Example Company')
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'https://example.com/logo.png')
        self.assertEqual(results[0]['title'], 'Example Logo')
        self.assertEqual(results[0]['width'], 200)
        self.assertEqual(results[0]['height'], 100)
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], 'https://www.googleapis.com/customsearch/v1')
        self.assertEqual(kwargs['params']['q'], 'Example Company logo')
        self.assertEqual(kwargs['params']['cx'], self.search_engine_id)
        self.assertEqual(kwargs['params']['key'], self.api_key)
        self.assertEqual(kwargs['params']['searchType'], 'image')
    
    @patch('src.api.google_search.requests.get')
    def test_search_company_logo_no_results(self, mock_get):
        """Test logo search with no results."""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}  # No items in response
        mock_get.return_value = mock_response
        
        # Call the method
        results = self.search_client.search_company_logo('Nonexistent Company')
        
        # Assertions
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
