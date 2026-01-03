"""
通用网页数据抓取器
Universal Web Scraper
"""

from .scraper import (
    UniversalScraper,
    ScraperConfig,
    FieldConfig,
    create_scraper_config
)
from .tools import get_universal_scraping_tools

__all__ = [
    'UniversalScraper',
    'ScraperConfig',
    'FieldConfig',
    'create_scraper_config',
    'get_universal_scraping_tools'
]
