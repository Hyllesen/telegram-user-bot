"""
Module to extract the store name from Temu share URLs by parsing the href attribute of the a element.
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote


class TemuKeywordExtractor:
    """Extracts the store name from the href attribute of the a element in Temu share URLs."""
    
    def __init__(self, timeout=10):
        """
        Initialize the extractor.
        
        Args:
            timeout (int): Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_first_keyword(self, url):
        """
        Extract the store name from the share_title parameter in the redirect URL.
        
        Args:
            url (str): The Temu share URL
            
        Returns:
            str: The store name from the share_title parameter, or None if not found
        """
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.netloc or not parsed.scheme:
            raise ValueError(f"Invalid URL: {url}")
        
        # Check if it's a Temu share URL
        if 'share.temu.com' not in parsed.netloc:
            raise ValueError(f"Not a Temu share URL: {url}")
        
        try:
            # Make HTTP request without following redirects to get the redirect URL
            response = self.session.get(url, timeout=self.timeout, allow_redirects=False)
            
            # Check if there's a redirect
            if response.status_code in [301, 302, 307, 308]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    # Extract the share_title from the redirect URL
                    match = re.search(r'share_title=([^&]+)', redirect_url)
                    if match:
                        share_title_encoded = match.group(1)
                        
                        # Decode URL encoding (e.g., %20 becomes space)
                        share_title_decoded = unquote(share_title_encoded)
                        
                        # Get the first word, ignoring %20 and anything after
                        # Split by spaces and take the first part
                        first_word = share_title_decoded.split()[0] if share_title_decoded.split() else None
                        
                        return first_word
                else:
                    # If no redirect location, try to follow redirects and parse the final page
                    response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                    response.raise_for_status()
                    
                    # Parse the HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find the single a element in the response HTML
                    a_element = soup.find('a')
                    
                    if not a_element:
                        return None
                    
                    # Get the href attribute
                    href = a_element.get('href')
                    if not href:
                        return None
                    
                    # Extract the store name from share_title parameter using regex
                    # Look for share_title= followed by URL-encoded text
                    match = re.search(r'share_title=([^&]+)', href)
                    if not match:
                        return None
                    
                    # Get the share_title value
                    share_title_encoded = match.group(1)
                    
                    # Decode URL encoding (e.g., %20 becomes space)
                    share_title_decoded = unquote(share_title_encoded)
                    
                    # Get the first word, ignoring %20 and anything after
                    # Split by spaces and take the first part
                    first_word = share_title_decoded.split()[0] if share_title_decoded.split() else None
                    
                    return first_word
            else:
                # If no redirect, process the page normally
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the single a element in the response HTML
                a_element = soup.find('a')
                
                if not a_element:
                    return None
                
                # Get the href attribute
                href = a_element.get('href')
                if not href:
                    return None
                
                # Extract the store name from share_title parameter using regex
                # Look for share_title= followed by URL-encoded text
                match = re.search(r'share_title=([^&]+)', href)
                if not match:
                    return None
                
                # Get the share_title value
                share_title_encoded = match.group(1)
                
                # Decode URL encoding (e.g., %20 becomes space)
                share_title_decoded = unquote(share_title_encoded)
                
                # Get the first word, ignoring %20 and anything after
                # Split by spaces and take the first part
                first_word = share_title_decoded.split()[0] if share_title_decoded.split() else None
                
                return first_word
        
        except requests.RequestException as e:
            raise Exception(f"Error making request to {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error extracting keyword from {url}: {str(e)}")


def extract_first_keyword_from_url(url):
    """
    Convenience function to extract the store name from a Temu share URL.
    
    Args:
        url (str): The Temu share URL
        
    Returns:
        str: The store name from the share_title parameter, or None if not found
    """
    extractor = TemuKeywordExtractor()
    return extractor.extract_first_keyword(url)