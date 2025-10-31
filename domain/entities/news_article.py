"""NewsArticle domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.value_objects.article_category import ArticleCategory


@dataclass(frozen=True)
class NewsArticle:
    """
    Domain entity representing a news article.
    
    This is an immutable value object following DDD principles.
    All business rules and invariants should be enforced here.
    """
    
    title: str
    source: str
    url: str
    summary: str
    category: ArticleCategory
    published_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate entity invariants."""
        if not self.title or not self.title.strip():
            raise ValueError("Article title cannot be empty")
        if not self.source or not self.source.strip():
            raise ValueError("Article source cannot be empty")
        if not self.url or not self.url.strip():
            raise ValueError("Article URL cannot be empty")
        if not self.summary or not self.summary.strip():
            raise ValueError("Article summary cannot be empty")
        
        # URL validation
        if not (self.url.startswith("http://") or self.url.startswith("https://")):
            raise ValueError("Article URL must be a valid HTTP/HTTPS URL")
    
    def is_in_date_range(self, start_date: datetime, end_date: datetime) -> bool:
        """
        Check if article is within the specified date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            True if article is within range, False otherwise
        """
        if self.published_date is None:
            return False
        
        return start_date <= self.published_date <= end_date
