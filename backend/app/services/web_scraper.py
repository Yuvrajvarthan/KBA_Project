import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import logging
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class WebScraper:
    """Service for scraping web content"""
    
    @staticmethod
    async def scrape_website(url: str) -> Dict[str, Any]:
        """Extract text content from a website"""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    "success": False,
                    "error": "Invalid URL format",
                    "text": "",
                    "metadata": {}
                }
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Make request with timeout
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract metadata
            metadata = {
                "title": "",
                "description": "",
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(response.content)
            }
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata["title"] = title_tag.get_text().strip()
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata["description"] = meta_desc.get('content', '').strip()
            
            # Extract main content
            # Try to find main content areas
            main_content = ""
            
            # Look for common content containers
            content_selectors = [
                'main', 'article', '[role="main"]', 
                '.content', '.post-content', '.entry-content',
                '#content', '#main', '.main-content'
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    main_content = content_element.get_text()
                    break
            
            # If no specific content found, use body
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content = body.get_text()
            
            # Clean up text
            if main_content:
                # Remove excessive whitespace
                main_content = re.sub(r'\s+', ' ', main_content)
                # Remove multiple newlines
                main_content = re.sub(r'\n\s*\n', '\n\n', main_content)
                main_content = main_content.strip()
            
            return {
                "success": True,
                "text": main_content,
                "metadata": metadata
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error scraping {url}: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "text": "",
                "metadata": {}
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "metadata": {}
            }
