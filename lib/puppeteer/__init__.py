"""
Puppeteer integration for LangChain Agent
Provides browser automation capabilities to the agent.
"""

from .puppeteer_tools import get_browser_tools
from .table_scraper.table_scraper import TableScraper, TableData, PaginationConfig
from .table_scraper.table_tools import get_table_scraping_tools

__all__ = [
    'get_browser_tools',
    'get_table_scraping_tools',
    'TableScraper',
    'TableData',
    'PaginationConfig',
]