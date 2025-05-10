#!/usr/bin/env python3
"""
Script to prepare logo files for website use.
This script takes logos from the carousel directory, renames them to be web-friendly
(lowercase, no spaces or special characters), and copies them to a new directory.
"""
import os
import sys
import argparse
import re
import shutil
from typing import List, Dict, Tuple

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.file_utils import ensure_directory


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Prepare logo files for website use')

    parser.add_argument('--input-dir', default='data/logos/carousel',
                        help='Directory containing the resized logo files')
    parser.add_argument('--output-dir', default='data/logos_for_website',
                        help='Directory to save the web-friendly logo files')
    parser.add_argument('--company', nargs='*',
                        help='Optional list of specific companies to process (default: all)')

    return parser.parse_args()


def clean_filename(filename: str) -> str:
    """
    Convert a filename to a web-friendly format.

    Args:
        filename: Original filename

    Returns:
        Web-friendly filename (lowercase, no spaces or special characters)
    """
    # Get the base name and extension
    name, ext = os.path.splitext(filename)

    # Extract company name (assuming format like "Company_1_logo_resized.svg")
    company_match = re.match(r'([^_]+)(?:_\d+)?_logo(?:_resized)?', name)
    if company_match:
        company_name = company_match.group(1)
    else:
        company_name = name

    # Convert to lowercase and remove special characters
    clean_name = re.sub(r'[^a-z0-9]', '', company_name.lower())

    # Return the cleaned name with the original extension
    return f"{clean_name}{ext.lower()}"


def process_logos(input_dir: str, output_dir: str, companies: List[str] = None) -> Dict[str, List[str]]:
    """
    Process logo files to make them web-friendly.

    Args:
        input_dir: Directory containing the resized logo files
        output_dir: Directory to save the web-friendly logo files
        companies: Optional list of specific companies to process

    Returns:
        Dictionary mapping company names to lists of processed file paths
    """
    # Ensure the output directory exists
    ensure_directory(output_dir)

    # Dictionary to store results
    results = {}

    # Dictionary to track file counts for each company and extension
    file_counts = {}

    # Get all files in the input directory
    files = os.listdir(input_dir)

    # Filter for image files
    image_files = [f for f in files if f.lower().endswith(('.svg', '.png', '.jpg', '.jpeg', '.gif'))]

    # Sort files to ensure consistent processing order
    image_files.sort()

    # Process each file
    for filename in image_files:
        # Extract company name from filename
        # Try different patterns to match various naming conventions
        company_match = re.match(r'([^_]+)(?:_\d+)?_logo(?:_resized)?', filename)

        if not company_match:
            # Try matching names with multiple words separated by underscores
            company_match = re.match(r'([^_]+(?:_[^_]+)*)_\d+_logo(?:_resized)?', filename)

        if not company_match:
            # Try matching just the first part before any underscore
            company_match = re.match(r'([^_]+)', filename)

        if not company_match:
            print(f"Skipping file with unrecognized format: {filename}")
            continue

        company_name = company_match.group(1)

        # Skip if we're only processing specific companies and this isn't one of them
        if companies and company_name not in companies:
            continue

        # Get the input path
        input_path = os.path.join(input_dir, filename)

        # Get file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Clean the company name
        clean_company = re.sub(r'[^a-z0-9]', '', company_name.lower())

        # Create a key for tracking file counts
        count_key = f"{clean_company}{ext}"

        # Get the current count for this company and extension
        count = file_counts.get(count_key, 0)

        # Increment the count
        file_counts[count_key] = count + 1

        # Create the output filename
        if count == 0:
            # First file for this company and extension
            output_filename = f"{clean_company}{ext}"
        else:
            # Additional files for this company and extension
            output_filename = f"{clean_company}{count + 1}{ext}"

        output_path = os.path.join(output_dir, output_filename)

        # Copy the file
        try:
            shutil.copy2(input_path, output_path)
            print(f"Copied {filename} to {output_filename}")

            # Add to results
            if company_name not in results:
                results[company_name] = []
            results[company_name].append(output_path)
        except Exception as e:
            print(f"Error copying {filename}: {str(e)}")

    return results


def main():
    """Main function to prepare logo files for website use."""
    args = parse_args()

    try:
        # Process the logo files
        results = process_logos(args.input_dir, args.output_dir, args.company)

        # Print summary
        print("\n=== Summary ===")
        if not results:
            print("No files were processed.")
        else:
            for company, files in results.items():
                print(f"{company}: {len(files)} files processed")
                for file in files:
                    print(f"  - {file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
