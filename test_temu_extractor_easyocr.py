#!/usr/bin/env python3
"""
Test script to run ImageProcessor on all images in the group_images folder.
"""

import os
from pathlib import Path
from temu_extractor_easyocr import ImageProcessor


def test_all_images():
    """Test all images in the group_images folder."""
    # Initialize the image processor
    processor = ImageProcessor()

    # Define the images directory
    images_dir = Path("group_images")

    # Check if the directory exists
    if not images_dir.exists():
        print(f"Directory {images_dir} does not exist.")
        return

    # Get all image files in the directory
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    image_files = []

    for ext in image_extensions:
        image_files.extend(images_dir.glob(f"*{ext}"))
        image_files.extend(images_dir.glob(f"*{ext.upper()}"))  # Also check uppercase extensions

    if not image_files:
        print(f"No images found in {images_dir}")
        return

    print(f"Found {len(image_files)} images to process:\n")

    # Process each image
    for image_path in sorted(image_files):
        print(f"Processing: {image_path.name}")

        try:
            # Process the image and extract store name
            store_name = processor.process_image(str(image_path))
            print(f"  ✓ Store name extracted: {store_name}")

        except Exception as e:
            print(f"  ✗ Error processing {image_path.name}: {str(e)}")

        print()  # Empty line for readability


if __name__ == "__main__":
    test_all_images()