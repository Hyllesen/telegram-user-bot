#!/usr/bin/env python3
"""
Test script for the TemuKeywordExtractor module.
"""

import sys
from temu_keyword_extractor import TemuKeywordExtractor, extract_first_keyword_from_url


def test_extractor():
    """Test the TemuKeywordExtractor with a URL."""
    if len(sys.argv) < 2:
        print("Usage: python test_temu_keyword_extractor.py <URL>")
        print("Example: python test_temu_keyword_extractor.py https://share.temu.com/zeyuA5c0HxA")
        return
    
    url = sys.argv[1]
    print(f"Testing URL: {url}")
    
    try:
        # Test using the convenience function
        keyword = extract_first_keyword_from_url(url)
        if keyword:
            print(f"First keyword extracted: {keyword}")
        else:
            print("No keyword found in the meta tag")
    
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"Error: {e}")


def test_class_directly():
    """Test the TemuKeywordExtractor class directly."""
    if len(sys.argv) < 2:
        print("Usage: python test_temu_keyword_extractor.py <URL>")
        return
    
    url = sys.argv[1]
    print(f"\nTesting class directly with URL: {url}")
    
    try:
        extractor = TemuKeywordExtractor(timeout=15)
        keyword = extractor.extract_first_keyword(url)
        if keyword:
            print(f"First keyword extracted: {keyword}")
        else:
            print("No keyword found in the meta tag")
    
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_extractor()
    test_class_directly()