"""Browser service for managing browser connections and configurations."""

import sys
import requests
from typing import Optional

from browser_use import Browser, BrowserConfig

from src.config.constants import (
    CHROME_DEBUG_URL,
    DEFAULT_MIN_WAIT_PAGE_LOAD_TIME,
    DEFAULT_WAIT_FOR_NETWORK_IDLE_PAGE_LOAD_TIME
)


class BrowserService:
    """Service for managing browser connections."""
    
    @staticmethod
    def check_debug_chrome_connection() -> bool:
        """
        Check if Chrome is running in debug mode.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = requests.get(f'{CHROME_DEBUG_URL}/json/version')
            if response.status_code != 200:
                print(f"Error: Chrome debug port returned status code {response.status_code}")
                print("Please run './launch_chrome_debug.sh' in a separate terminal first.")
                return False
                
            print(f"Successfully connected to Chrome debug instance at {CHROME_DEBUG_URL}")
            print(f"Chrome version: {response.json().get('Browser')}")
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to Chrome debug port at {CHROME_DEBUG_URL}")
            print("Please run './launch_chrome_debug.sh' in a separate terminal first.")
            return False
    
    @staticmethod
    def create_browser(headless: bool = True) -> Optional[Browser]:
        """
        Create and configure a browser instance.
        
        Args:
            headless: Whether to run the browser in headless mode
            
        Returns:
            Browser: Configured browser instance or None if connection failed
        """
        if not BrowserService.check_debug_chrome_connection():
            sys.exit(1)
            
        config = BrowserConfig(
            cdp_url=CHROME_DEBUG_URL,
            headless=headless,
            minimum_wait_page_load_time=DEFAULT_MIN_WAIT_PAGE_LOAD_TIME,
            wait_for_network_idle_page_load_time=DEFAULT_WAIT_FOR_NETWORK_IDLE_PAGE_LOAD_TIME
        )
        
        return Browser(config=config)
