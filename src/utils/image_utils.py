"""
Utility functions for image processing.
"""
import os
import io
from typing import Tuple, Optional, List
from PIL import Image

# Try to import cairosvg, but make it optional
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    print("Warning: cairosvg is not available. SVG resizing will be limited.")
    print("To enable SVG support, install Cairo and then cairosvg:")
    print("  1. Install Cairo: https://www.cairographics.org/download/")
    print("  2. Install cairosvg: pip install cairosvg")


def resize_image(image_path: str, output_path: str, size: Tuple[int, int],
                 maintain_aspect_ratio: bool = True) -> Optional[str]:
    """
    Resize an image to the specified size.

    Args:
        image_path: Path to the input image
        output_path: Path to save the resized image
        size: Target size as (width, height)
        maintain_aspect_ratio: Whether to maintain the aspect ratio

    Returns:
        Path to the resized image or None if resizing failed
    """
    try:
        # Check if the file exists
        if not os.path.exists(image_path):
            print(f"Error: File {image_path} does not exist")
            return None

        # Try to determine if it's an SVG by checking file content
        is_svg = False
        try:
            with open(image_path, 'rb') as f:
                header = f.read(1024)  # Read first 1KB
                if b'<svg' in header:
                    is_svg = True
        except:
            # If we can't read the file, just continue and let PIL try to open it
            pass

        # Get file extension
        _, ext = os.path.splitext(image_path)
        ext = ext.lower() if ext else ''

        # Handle SVG files
        if ext == '.svg' or is_svg:
            return resize_svg(image_path, output_path, size, maintain_aspect_ratio)

        # Handle raster images (PNG, JPG, etc.)
        try:
            with Image.open(image_path) as img:
                # Convert to RGBA to ensure transparency is preserved
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                if maintain_aspect_ratio:
                    # Calculate new dimensions while maintaining aspect ratio
                    img_width, img_height = img.size
                    target_width, target_height = size

                    # Calculate aspect ratios
                    width_ratio = target_width / img_width
                    height_ratio = target_height / img_height

                    # Use the smaller ratio to ensure the image fits within the target size
                    ratio = min(width_ratio, height_ratio)

                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)

                    # Resize the image
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

                    # Create a transparent background
                    background = Image.new('RGBA', size, (0, 0, 0, 0))

                    # Calculate position to center the image
                    offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)

                    # Paste the resized image onto the background
                    background.paste(resized_img, offset, resized_img)
                    background.save(output_path)
                else:
                    # Resize without maintaining aspect ratio
                    resized_img = img.resize(size, Image.LANCZOS)
                    resized_img.save(output_path)

                return output_path
        except Exception as e:
            print(f"Error opening image {image_path} with PIL: {str(e)}")

            # If it's not an SVG and PIL can't open it, just copy the file
            import shutil
            shutil.copy(image_path, output_path)
            print(f"Copied file to {output_path} without resizing")
            return output_path

    except Exception as e:
        print(f"Error resizing image {image_path}: {str(e)}")
        return None


def resize_svg(svg_path: str, output_path: str, size: Tuple[int, int],
               maintain_aspect_ratio: bool = True) -> Optional[str]:
    """
    Resize an SVG image to the specified size.

    Args:
        svg_path: Path to the input SVG
        output_path: Path to save the resized image
        size: Target size as (width, height)
        maintain_aspect_ratio: Whether to maintain the aspect ratio

    Returns:
        Path to the resized image or None if resizing failed
    """
    # Check if cairosvg is available
    if not CAIROSVG_AVAILABLE:
        print(f"Warning: Cannot resize SVG {svg_path} - cairosvg is not available")
        # Just copy the SVG file to the output path
        try:
            import shutil
            output_path = output_path.replace('.png', '.svg')
            shutil.copy(svg_path, output_path)
            print(f"Copied SVG file to {output_path} without resizing")
            return output_path
        except Exception as e:
            print(f"Error copying SVG {svg_path}: {str(e)}")
            return None

    # If cairosvg is available, use it to resize the SVG
    try:
        target_width, target_height = size

        # Read the SVG file
        with open(svg_path, 'r') as f:
            svg_content = f.read()

        # Convert SVG to PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=target_width,
            output_height=target_height
        )

        # Save as PNG
        output_path = output_path.replace('.svg', '.png')
        with open(output_path, 'wb') as f:
            f.write(png_data)

        return output_path

    except Exception as e:
        print(f"Error resizing SVG {svg_path}: {str(e)}")
        return None


def resize_for_carousel(image_paths: List[str], output_dir: str,
                        carousel_size: Tuple[int, int] = (200, 100)) -> List[str]:
    """
    Resize multiple images for a logo carousel.

    Args:
        image_paths: List of paths to the input images
        output_dir: Directory to save the resized images
        carousel_size: Target size for the carousel images

    Returns:
        List of paths to the resized images
    """
    os.makedirs(output_dir, exist_ok=True)

    resized_paths = []
    for image_path in image_paths:
        try:
            # Check if the file exists and has a valid extension
            if not os.path.exists(image_path):
                print(f"Warning: File {image_path} does not exist, skipping")
                continue

            # Generate output path
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)

            # Ensure we have a valid extension
            if not ext or len(ext) <= 1:
                # Try to determine extension from the file content
                with open(image_path, 'rb') as f:
                    header = f.read(10)  # Read first few bytes

                if header.startswith(b'\x89PNG'):
                    ext = '.png'
                elif header.startswith(b'\xff\xd8'):
                    ext = '.jpg'
                elif b'<svg' in header:
                    ext = '.svg'
                else:
                    # Default to png
                    ext = '.png'

                # Update the name to include the extension
                name = filename

            output_path = os.path.join(output_dir, f"{name}_resized{ext}")

            # Resize the image
            resized_path = resize_image(image_path, output_path, carousel_size)
            if resized_path:
                resized_paths.append(resized_path)
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")

    return resized_paths
