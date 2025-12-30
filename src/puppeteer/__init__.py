"""
Puppeteer integration for LangChain Agent
Provides browser automation capabilities to the agent.
"""

from .puppeteer_tools import get_browser_tools

__all__ = [
    'get_browser_tools',
]