"""
Google Custom Search API integration for finding company logos.
"""
import json
import requests
from typing import Dict, List, Optional, Any


class GoogleCustomSearch:
    """
    Class to interact with Google Custom Search API to find company logos.
    """

    def __init__(self, api_key: str, search_engine_id: str):
        """
        Initialize the Google Custom Search API client.

        Args:
            api_key: Google API key
            search_engine_id: Google Custom Search Engine ID
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search_company_logo(self, company_name: str, num_results: int = 5,
                           file_type: str = None, transparent: bool = True) -> List[Dict[str, Any]]:
        """
        Search for a company's logo using Google Custom Search API.

        Args:
            company_name: Name of the company to search for
            num_results: Number of results to return (max 10)
            file_type: Optional file type filter ('svg' or 'png')
            transparent: Whether to prefer transparent logos

        Returns:
            List of image results with URLs and metadata
        """
        # Build the query to find logos with both name and logo
        query = f"{company_name} logo transparent"

        if file_type:
            query += f" filetype:{file_type}"

        params = {
            'q': query,
            'cx': self.search_engine_id,
            'key': self.api_key,
            'searchType': 'image',
            'num': min(num_results, 10),  # API limit is 10
            'imgSize': 'large',  # Prefer large images
            'safe': 'active',
        }

        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        search_results = response.json()

        if 'items' not in search_results:
            return []

        return [
            {
                'url': item.get('link', ''),
                'title': item.get('title', ''),
                'context_url': item.get('image', {}).get('contextLink', ''),
                'width': item.get('image', {}).get('width', 0),
                'height': item.get('image', {}).get('height', 0),
                'thumbnail_url': item.get('image', {}).get('thumbnailLink', ''),
                'file_format': item.get('fileFormat', ''),
            }
            for item in search_results.get('items', [])
        ]
