#!/usr/bin/env python3
"""
Simple test for the TemuKeywordExtractor module.
"""

from temu_keyword_extractor import TemuKeywordExtractor


def test_meta_parsing():
    """Test the meta tag parsing functionality."""
    # Create a mock HTML with the expected meta tag
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="keywords" content="Crystal   shop" />
        <title>Test Page</title>
    </head>
    <body>
        <p>This is a test page</p>
    </body>
    </html>
    '''
    
    # Create a mock response object
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.status_code = 200
        
        def raise_for_status(self):
            pass
    
    # Create an instance of the extractor
    extractor = TemuKeywordExtractor()
    
    # Patch the session.get method to return our mock HTML
    original_get = extractor.session.get
    def mock_get(url, **kwargs):
        return MockResponse(html_content.encode('utf-8'))
    
    extractor.session.get = mock_get
    
    # Test the extraction
    try:
        result = extractor.extract_first_keyword("https://share.temu.com/test123")
        print(f"Test result: {result}")
        if result == "Crystal":
            print("✓ Test passed: Correctly extracted 'Crystal' from meta tag")
        else:
            print(f"✗ Test failed: Expected 'Crystal', got '{result}'")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
    
    # Restore original method
    extractor.session.get = original_get


def test_invalid_url():
    """Test with an invalid URL."""
    extractor = TemuKeywordExtractor()
    
    try:
        result = extractor.extract_first_keyword("https://example.com/not-a-temu-url")
        print(f"Invalid URL test result: {result}")
        print("✗ Test failed: Should have raised an error for non-Temu URL")
    except ValueError as e:
        print(f"✓ Invalid URL test passed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("Testing TemuKeywordExtractor module...")
    test_meta_parsing()
    print()
    test_invalid_url()