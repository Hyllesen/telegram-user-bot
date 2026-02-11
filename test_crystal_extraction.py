#!/usr/bin/env python3
"""
Test script for the TemuKeywordExtractor module with a specific URL.
"""

from temu_keyword_extractor import TemuKeywordExtractor


def test_crystal_extraction():
    """Test the TemuKeywordExtractor with the specific URL to ensure it returns 'Crystal'."""
    url = "https://share.temu.com/wpzbYxO8LSA"
    print(f"Testing URL: {url}")
    
    extractor = TemuKeywordExtractor()
    
    try:
        result = extractor.extract_first_keyword(url)
        print(f"Result: {result}")
        
        # Assert that the result is 'Crystal'
        if result == "Crystal":
            print("✓ Test PASSED: Result is 'Crystal' as expected")
        else:
            print(f"✗ Test FAILED: Expected 'Crystal', but got '{result}'")
            print("Possible reasons:")
            print("1. The URL might redirect to a page with different content than expected")
            print("2. The HTML structure might be different than anticipated")
            print("3. The share_title parameter might have different content")
            print("4. Network issues prevented proper retrieval of the page")
            
            # Let's debug by fetching the page and printing its content
            import requests
            from bs4 import BeautifulSoup
            
            try:
                response = extractor.session.get(url, timeout=10)
                print(f"Status code: {response.status_code}")
                print("HTML content:")
                print(response.text[:1000])  # Print first 1000 characters
                
                # Parse and look for the a element
                soup = BeautifulSoup(response.content, 'html.parser')
                a_element = soup.find('a')
                if a_element:
                    print(f"Found <a> element: {a_element}")
                    href = a_element.get('href')
                    print(f"Href attribute: {href}")
                    
                    # Look for share_title in the href
                    import re
                    from urllib.parse import unquote
                    match = re.search(r'share_title=([^&]+)', href)
                    if match:
                        share_title_encoded = match.group(1)
                        share_title_decoded = unquote(share_title_encoded)
                        print(f"Encoded share_title: {share_title_encoded}")
                        print(f"Decoded share_title: {share_title_decoded}")
                        first_word = share_title_decoded.split()[0] if share_title_decoded.split() else None
                        print(f"First word: {first_word}")
                    else:
                        print("No share_title parameter found in href")
                else:
                    print("No <a> element found in the HTML")
                    
            except Exception as e:
                print(f"Error during debugging: {e}")
    
    except Exception as e:
        print(f"Error during extraction: {e}")


if __name__ == "__main__":
    test_crystal_extraction()