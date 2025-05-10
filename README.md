# Download Company Logos

A Python tool to download company logos using the Google Custom Search API.

## Features

- Search for company logos using Google Custom Search API
- Download high-quality logo images
- Simple command-line interface
- Configurable search parameters

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/mathew-kollamala/download-company-logos.git
   cd download-company-logos
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

   **Optional**: For SVG support (resizing SVGs to PNGs), you need to install Cairo and cairosvg:
   - First, install Cairo graphics library:
     - macOS: `brew install cairo`
     - Ubuntu/Debian: `sudo apt-get install libcairo2-dev`
     - Windows: Download from [Cairo website](https://www.cairographics.org/download/)
   - Then install cairosvg:
     ```
     pip install cairosvg
     ```

   Without Cairo/cairosvg, the script will still work but will only copy SVG files without resizing them.

3. Configure your Google API credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Custom Search API
   - Create API credentials
   - Create a Custom Search Engine at [cse.google.com/cse](https://cse.google.com/cse)
   - Set your credentials in one of two ways:
     - **Option 1**: Update the `.env` file with your API key and Search Engine ID:
       ```
       GOOGLE_API_KEY=your_google_api_key_here
       GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
       ```
     - **Option 2**: Update the `config/config.json` file with your API key and Search Engine ID

## Usage

### Downloading Multiple Company Logos

Run the script with a list of company names:

```
python scripts/download_logos.py "Apple" "Microsoft" "Google"
```

### Testing with Just Google (to limit API costs)

For testing purposes, you can use the test script that only downloads Google logos:

```
python scripts/test_google_logo.py
```

### Command Line Options

The script supports various options:

```
python scripts/download_logos.py --help
```

Key options include:

- `--formats`: File formats to download (default: svg png)
- `--num-per-format`: Number of logos to download per format (default: 5)
- `--carousel-size`: Size for carousel images as width height (default: 200 100)
- `--skip-resize`: Skip resizing images for carousel
- `--output-dir`: Directory to save downloaded logos (default: data/logos)

## Features

- Download company logos in multiple formats (SVG, PNG)
- Search for transparent logos that include both company name and logo
- Resize logos to fit a logo carousel on a website
- Maintain aspect ratio during resizing
- Preserve transparency in resized images
- Command-line interface with various options

## Project Structure

- `src/` - Main source code
  - `api/` - API integration code
  - `downloader/` - Image downloading functionality
  - `utils/` - Utility functions
    - `file_utils.py` - File handling utilities
    - `image_utils.py` - Image processing utilities
- `config/` - Configuration files
- `data/` - Directory for downloaded logos
  - `carousel/` - Resized images for carousel
- `tests/` - Test files
- `scripts/` - Utility scripts
  - `download_logos.py` - Main script for downloading logos
  - `test_google_logo.py` - Test script using only Google
- `.env` - Environment variables for API credentials (not tracked by git)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
