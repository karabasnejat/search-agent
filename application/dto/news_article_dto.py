"""NewsArticleDTO - Data Transfer Object for news articles."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class NewsArticleDTO:
    """DTO for transferring news article data across application boundaries."""
    
    title: str
    source: str
    date: Optional[str]
    summary: str
    category: str
    url: str
