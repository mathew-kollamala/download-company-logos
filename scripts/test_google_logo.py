#!/usr/bin/env python3
"""
Test script to download Google logos and resize them for a carousel.
This script is used to test the functionality with just one company to limit API costs.
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

from src.api.google_search import GoogleCustomSearch
from src.downloader.image_downloader import ImageDownloader
from src.utils.file_utils import ensure_directory
from src.utils.image_utils import resize_for_carousel


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test downloading Google logos')
    
    parser.add_argument('--output-dir', default='data/test_logos', 
                        help='Directory to save downloaded logos')
    parser.add_argument('--num-per-format', type=int, default=5, 
                        help='Number of logos to download per format')
    parser.add_argument('--formats', nargs='+', default=['svg', 'png'], 
                        help='File formats to download (default: svg png)')
    parser.add_argument('--carousel-size', nargs=2, type=int, default=[200, 100], 
                        help='Size for carousel images as width height (default: 200 100)')
    
    return parser.parse_args()


def main():
    """Main function to test downloading Google logos."""
    args = parse_args()
    
    try:
        # Get API credentials from environment variables
        api_key = os.getenv('GOOGLE_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            print("Error: Google API key and Search Engine ID must be provided as environment variables")
            sys.exit(1)
        
        # Ensure output directories exist
        ensure_directory(args.output_dir)
        carousel_dir = os.path.join(args.output_dir, 'carousel')
        ensure_directory(carousel_dir)
        
        # Initialize API client and downloader
        search_client = GoogleCustomSearch(api_key, search_engine_id)
        downloader = ImageDownloader(args.output_dir)
        
        # Company to test with
        company = "Google"
        
        print(f"\n=== Testing with {company} ===")
        
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
            sys.exit(1)
            
        print(f"Successfully downloaded {len(all_files)} logos for {company}")
        
        # Resize images for carousel
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
