"""News repository interface following Dependency Inversion Principle."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.news_article import NewsArticle
from domain.value_objects.date_range import DateRange
from domain.value_objects.domain import Domain


class INewsRepository(ABC):
    """
    Repository interface for news articles.
    
    This interface belongs to the domain layer and defines the contract
    that infrastructure implementations must follow (Dependency Inversion Principle).
    """
    
    @abstractmethod
    def search(
        self,
        query: str,
        date_range: DateRange,
        domains: Optional[List[Domain]] = None,
        max_results: int = 25
    ) -> List[NewsArticle]:
        """
        Search for news articles within a date range.
        
        Args:
            query: Search query string
            date_range: Date range to search within
            domains: Optional list of domains to restrict search to
            max_results: Maximum number of results to return
            
        Returns:
            List of NewsArticle domain entities
            
        Raises:
            RepositoryException: If search fails
        """
        pass
