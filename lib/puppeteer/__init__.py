"""
Puppeteer integration for LangChain Agent
Provides browser automation capabilities to the agent.
"""

from .puppeteer_tools import get_browser_tools
from .table_scraper.table_scraper import TableScraper, TableData, PaginationConfig
from .table_scraper.table_tools import get_table_scraping_tools
from .universal_scraper import (
    UniversalScraper,
    ScraperConfig,
    FieldConfig,
    create_scraper_config,
    get_universal_scraping_tools
)
from .browser_steps import (
    BrowserStepExecutor,
    StepConfig,
    StepType,
    create_navigate_step,
    create_click_step,
    create_input_step,
    create_select_step,
    create_extract_step,
    create_press_key_step,
    create_wait_step
)

__all__ = [
    'get_browser_tools',
    'get_table_scraping_tools',
    'get_universal_scraping_tools',
    'TableScraper',
    'TableData',
    'PaginationConfig',
    'UniversalScraper',
    'ScraperConfig',
    'FieldConfig',
    'create_scraper_config',
    'BrowserStepExecutor',
    'StepConfig',
    'StepType',
    'create_navigate_step',
    'create_click_step',
    'create_input_step',
    'create_select_step',
    'create_extract_step',
    'create_press_key_step',
    'create_wait_step',
]