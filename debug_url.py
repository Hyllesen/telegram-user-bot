#!/usr/bin/env python3
"""
Debug script to investigate the redirect behavior of the Temu URL.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
import re


def debug_url_structure():
    """Debug the URL structure to understand how redirects work."""
    url = "https://share.temu.com/wpzbYxO8LSA"
    print(f"Debugging URL: {url}")
    
    # Create a session with headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Make request without allowing redirects to see what happens
    response_no_redirect = session.get(url, allow_redirects=False, timeout=10)
    print(f"Status code without redirect: {response_no_redirect.status_code}")
    if 'Location' in response_no_redirect.headers:
        print(f"Redirect location: {response_no_redirect.headers['Location']}")
    
    # Now make request with redirects allowed
    response_with_redirect = session.get(url, allow_redirects=True, timeout=10)
    print(f"Status code with redirect: {response_with_redirect.status_code}")
    print(f"Final URL after redirect: {response_with_redirect.url}")
    
    print("\nHTML content (first 1000 chars):")
    print(response_with_redirect.text[:1000])
    
    # Look for any URLs or links in the HTML
    soup = BeautifulSoup(response_with_redirect.content, 'html.parser')
    
    # Find all links
    links = soup.find_all('a')
    print(f"\nFound {len(links)} <a> elements:")
    for i, link in enumerate(links):
        print(f"Link {i+1}: {link}")
        print(f"  Href: {link.get('href')}")
        print(f"  Text: {link.get_text()}")
    
    # Look for any script tags that might contain URLs
    scripts = soup.find_all('script')
    print(f"\nFound {len(scripts)} <script> elements")
    for i, script in enumerate(scripts):
        script_content = script.string
        if script_content:
            # Look for URLs in the script content
            urls_in_script = re.findall(r'https?://[^\s"<>\']+', script_content)
            if urls_in_script:
                print(f"  Script {i+1} contains URLs: {urls_in_script}")
            
            # Look for share_title in the script
            share_title_matches = re.findall(r'share_title=([^&\'\"<>\s]+)', script_content)
            if share_title_matches:
                print(f"  Script {i+1} contains share_title values: {share_title_matches}")
                for match in share_title_matches:
                    decoded = unquote(match)
                    first_word = decoded.split()[0] if decoded.split() else None
                    print(f"    Decoded: {decoded}, First word: {first_word}")


if __name__ == "__main__":
    debug_url_structure()