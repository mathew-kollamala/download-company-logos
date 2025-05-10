#!/usr/bin/env python3
"""
Script to download company logos using Google Custom Search API.
"""
import os
import sys
import json
import argparse
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

from src.api.google_search import GoogleCustomSearch
from src.downloader.image_downloader import ImageDownloader
from src.utils.file_utils import load_config, ensure_directory
from src.utils.image_utils import resize_for_carousel


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Download company logos using Google Custom Search API')

    parser.add_argument('companies', nargs='+', help='Names of companies to download logos for')
    parser.add_argument('--config', default='config/config.json', help='Path to configuration file')
    parser.add_argument('--output-dir', default='data/logos', help='Directory to save downloaded logos')
    parser.add_argument('--num-per-format', type=int, default=5, help='Number of logos to download per format')
    parser.add_argument('--formats', nargs='+', default=['svg', 'png'],
                        help='File formats to download (default: svg png)')
    parser.add_argument('--carousel-size', nargs=2, type=int, default=[200, 100],
                        help='Size for carousel images as width height (default: 200 100)')
    parser.add_argument('--skip-resize', action='store_true',
                        help='Skip resizing images for carousel')

    return parser.parse_args()


def main():
    """Main function to download company logos."""
    args = parse_args()

    try:
        # Try to load configuration from config file
        try:
            config = load_config(args.config)
            api_key = config.get('google_api_key')
            search_engine_id = config.get('search_engine_id')
        except (FileNotFoundError, json.JSONDecodeError):
            # If config file doesn't exist or is invalid, use environment variables
            config = {}
            api_key = None
            search_engine_id = None

        # Use environment variables as fallback
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        search_engine_id = search_engine_id or os.getenv('GOOGLE_SEARCH_ENGINE_ID')

        if not api_key or not search_engine_id:
            print("Error: Google API key and Search Engine ID must be provided either in the config file or as environment variables")
            sys.exit(1)

        # Ensure output directory exists
        ensure_directory(args.output_dir)

        # Create directory for resized images
        carousel_dir = os.path.join(args.output_dir, 'carousel')
        ensure_directory(carousel_dir)

        # Initialize API client and downloader
        search_client = GoogleCustomSearch(api_key, search_engine_id)
        downloader = ImageDownloader(args.output_dir)

        # Download logos for each company
        for company in args.companies:
            print(f"\n=== Processing {company} ===")

            # Download logos in multiple formats
            downloaded_files = downloader.download_multiple_formats(
                company,
                search_client,
                formats=args.formats,
                num_per_format=args.num_per_format
            )

            # Flatten the list of downloaded files
            all_files = []
            for format_type, files in downloaded_files.items():
                all_files.extend(files)

            if not all_files:
                print(f"Failed to download any logos for {company}")
                continue

            print(f"Successfully downloaded {len(all_files)} logos for {company}")

            # Resize images for carousel if needed
            if not args.skip_resize:
                carousel_size = tuple(args.carousel_size)
                resized_files = resize_for_carousel(all_files, carousel_dir, carousel_size)

                if resized_files:
                    print(f"Resized {len(resized_files)} logos for carousel")
                    for file in resized_files:
                        print(f"  - {file}")
                else:
                    print("Failed to resize any logos for carousel")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
