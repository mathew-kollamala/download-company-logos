"""
Tests for the image downloader functionality.
"""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
import shutil

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.downloader.image_downloader import ImageDownloader


class TestImageDownloader(unittest.TestCase):
    """Test cases for ImageDownloader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = ImageDownloader(self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.downloader.image_downloader.requests.get')
    def test_download_image_success(self, mock_get):
        """Test successful image download."""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b'test image data']
        mock_get.return_value = mock_response
        
        # Mock file open
        with patch('builtins.open', mock_open()) as mock_file:
            # Call the method
            file_path = self.downloader.download_image(
                'https://example.com/logo.png',
                'Example Company'
            )
            
            # Assertions
            self.assertIsNotNone(file_path)
            self.assertTrue(file_path.endswith('Example_Company_logo.png'))
            mock_file.assert_called_once()
            mock_file().write.assert_called_once_with(b'test image data')
    
    @patch('src.downloader.image_downloader.requests.get')
    def test_download_image_failure(self, mock_get):
        """Test image download failure."""
        # Mock response to raise an exception
        mock_get.side_effect = Exception("Connection error")
        
        # Call the method
        file_path = self.downloader.download_image(
            'https://example.com/logo.png',
            'Example Company'
        )
        
        # Assertions
        self.assertIsNone(file_path)
    
    def test_download_from_search_results_success(self):
        """Test downloading from search results."""
        # Mock search results
        search_results = [
            {'url': 'https://example.com/logo1.png', 'file_format': 'image/png'},
            {'url': 'https://example.com/logo2.jpg', 'file_format': 'image/jpeg'}
        ]
        
        # Mock the download_image method
        with patch.object(self.downloader, 'download_image') as mock_download:
            mock_download.return_value = os.path.join(self.temp_dir, 'Example_Company_logo.png')
            
            # Call the method
            file_path = self.downloader.download_from_search_results(search_results, 'Example Company')
            
            # Assertions
            self.assertIsNotNone(file_path)
            mock_download.assert_called_once_with(
                'https://example.com/logo1.png',
                'Example Company',
                'image/png'
            )
    
    def test_download_from_search_results_all_fail(self):
        """Test downloading from search results when all downloads fail."""
        # Mock search results
        search_results = [
            {'url': 'https://example.com/logo1.png', 'file_format': 'image/png'},
            {'url': 'https://example.com/logo2.jpg', 'file_format': 'image/jpeg'}
        ]
        
        # Mock the download_image method to always fail
        with patch.object(self.downloader, 'download_image') as mock_download:
            mock_download.return_value = None
            
            # Call the method
            file_path = self.downloader.download_from_search_results(search_results, 'Example Company')
            
            # Assertions
            self.assertIsNone(file_path)
            self.assertEqual(mock_download.call_count, 2)


if __name__ == '__main__':
    unittest.main()
