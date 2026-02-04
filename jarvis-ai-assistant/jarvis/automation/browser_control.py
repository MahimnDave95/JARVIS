"""
Browser control for web navigation and searches.
"""

import webbrowser
import urllib.parse
from loguru import logger

class BrowserControl:
    """Control browser actions."""
    
    def __init__(self):
        self._browser = None
    
    def open_url(self, url: str) -> tuple[bool, str]:
        """
        Open a URL in the default browser.
        
        Args:
            url: URL to open
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Ensure proper URL format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url, new=2)  # new=2 opens in new tab if possible
            logger.info(f"Opened URL: {url}")
            return True, f"Opening {url}"
            
        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}")
            return False, f"Couldn't open that link. 😅"
    
    def google_search(self, query: str) -> tuple[bool, str]:
        """
        Search Google for a query.
        
        Args:
            query: Search query
            
        Returns:
            Tuple of (success, message)
        """
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            webbrowser.open(url, new=2)
            logger.info(f"Google search: {query}")
            return True, f"Searching Google for '{query}'"
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False, "Search didn't work. Try again?"
    
    def open_youtube_search(self, query: str) -> tuple[bool, str]:
        """
        Search YouTube for a query.
        
        Args:
            query: Search query
            
        Returns:
            Tuple of (success, message)
        """
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            webbrowser.open(url, new=2)
            logger.info(f"YouTube search: {query}")
            return True, f"Looking up '{query}' on YouTube 🔥"
            
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return False, "Couldn't search YouTube. 😅"
    
    def open_youtube_video(self, video_id: str) -> tuple[bool, str]:
        """Open specific YouTube video."""
        return self.open_url(f"https://youtube.com/watch?v={video_id}")

# Global instance
browser_control = BrowserControl()