"""
Image downloader for saving company logos.
"""
import os
import requests
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse
import re


class ImageDownloader:
    """
    Class to download images from URLs.
    """

    def __init__(self, output_dir: str):
        """
        Initialize the image downloader.

        Args:
            output_dir: Directory to save downloaded images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def download_image(self, image_url: str, company_name: str, file_format: Optional[str] = None) -> Optional[str]:
        """
        Download an image from a URL and save it to the output directory.

        Args:
            image_url: URL of the image to download
            company_name: Name of the company (used for filename)
            file_format: Optional file format override

        Returns:
            Path to the downloaded file or None if download failed
        """
        try:
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()

            # Determine file extension
            if file_format and '/' in file_format:
                # Extract extension from MIME type
                mime_type = file_format.lower()
                if 'svg' in mime_type:
                    ext = '.svg'
                elif 'png' in mime_type:
                    ext = '.png'
                elif 'jpeg' in mime_type or 'jpg' in mime_type:
                    ext = '.jpg'
                elif 'gif' in mime_type:
                    ext = '.gif'
                else:
                    # Default to the MIME subtype
                    ext = f".{mime_type.split('/')[-1]}"
            else:
                # Extract extension from URL
                parsed_url = urlparse(image_url)
                path = parsed_url.path.lower()

                if path.endswith('.svg'):
                    ext = '.svg'
                elif path.endswith('.png'):
                    ext = '.png'
                elif path.endswith('.jpg') or path.endswith('.jpeg'):
                    ext = '.jpg'
                elif path.endswith('.gif'):
                    ext = '.gif'
                else:
                    # Try to extract extension
                    url_ext = os.path.splitext(path)[1]
                    if url_ext and len(url_ext) < 6:  # Reasonable length for an extension
                        ext = url_ext if url_ext.startswith('.') else f".{url_ext}"
                    else:
                        # Default to png if no extension found
                        ext = '.png'

            # Clean company name for filename
            clean_name = ''.join(c if c.isalnum() else '_' for c in company_name)
            filename = f"{clean_name}_logo{ext}"
            file_path = os.path.join(self.output_dir, filename)

            # Save the image
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return file_path

        except Exception as e:
            print(f"Error downloading image from {image_url}: {str(e)}")
            return None

    def download_from_search_results(self, search_results: List[Dict[str, Any]],
                                 company_name: str, max_downloads: int = 1,
                                 file_type: Optional[str] = None) -> List[str]:
        """
        Download images from search results.

        Args:
            search_results: List of search result items
            company_name: Name of the company
            max_downloads: Maximum number of images to download
            file_type: Optional file type filter ('svg' or 'png')

        Returns:
            List of paths to the downloaded files
        """
        downloaded_paths = []
        download_count = 0

        for result in search_results:
            image_url = result.get('url')
            file_format = result.get('file_format')

            if not image_url:
                continue

            # Check if the file type matches the requested type
            if file_type:
                url_lower = image_url.lower()
                if file_type == 'svg' and not url_lower.endswith('.svg'):
                    continue
                elif file_type == 'png' and not url_lower.endswith('.png'):
                    continue

            # Generate a unique filename with index
            index = len(downloaded_paths) + 1

            # Download the image
            file_path = self.download_image(image_url, f"{company_name}_{index}", file_format)
            if file_path:
                downloaded_paths.append(file_path)
                download_count += 1

                if download_count >= max_downloads:
                    break

        return downloaded_paths

    def download_multiple_formats(self, company_name: str, search_client,
                                 formats: List[str] = ['svg', 'png'],
                                 num_per_format: int = 5) -> Dict[str, List[str]]:
        """
        Download company logos in multiple formats.

        Args:
            company_name: Name of the company
            search_client: GoogleCustomSearch instance
            formats: List of formats to download
            num_per_format: Number of images to download per format

        Returns:
            Dictionary mapping format to list of downloaded file paths
        """
        results = {}

        for file_format in formats:
            print(f"Searching for {file_format.upper()} logos of {company_name}...")
            search_results = search_client.search_company_logo(
                company_name,
                num_results=10,  # Request more to increase chances of finding the right format
                file_type=file_format
            )

            if not search_results:
                print(f"No {file_format.upper()} results found for {company_name}")
                results[file_format] = []
                continue

            print(f"Found {len(search_results)} potential {file_format.upper()} logos for {company_name}")
            downloaded_paths = self.download_from_search_results(
                search_results,
                company_name,
                max_downloads=num_per_format,
                file_type=file_format
            )

            if downloaded_paths:
                print(f"Successfully downloaded {len(downloaded_paths)} {file_format.upper()} logos for {company_name}")
                results[file_format] = downloaded_paths
            else:
                print(f"Failed to download any {file_format.upper()} logo for {company_name}")
                results[file_format] = []

        return results
