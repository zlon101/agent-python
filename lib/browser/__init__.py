"""
Browser management package
"""

from .manager import BrowserManager
from .detector import find_chrome_cdp_url, check_cdp_connection, get_chrome_pages

__all__ = [
    'BrowserManager',
    'find_chrome_cdp_url',
    'check_cdp_connection',
    'get_chrome_pages'
]