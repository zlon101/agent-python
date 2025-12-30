# --- Custom Tools ---

from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b