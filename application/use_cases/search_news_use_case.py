"""SearchNewsUseCase - Application use case for searching news."""

from typing import List, Optional

from application.dto.news_article_dto import NewsArticleDTO
from domain.entities.news_article import NewsArticle
from domain.repositories.inews_repository import INewsRepository
from domain.value_objects.date_range import DateRange
from domain.value_objects.domain import Domain


class SearchNewsUseCase:
    """
    Use case for searching AI news articles.
    
    Follows Single Responsibility Principle - handles only news searching logic.
    Depends on abstraction (INewsRepository) following Dependency Inversion Principle.
    """
    
    def __init__(self, news_repository: INewsRepository):
        """
        Initialize use case with news repository.
        
        Args:
            news_repository: Repository implementation for news articles
        """
        self._news_repository = news_repository
    
    def execute(
        self,
        query: str,
        date_range: DateRange,
        domains: Optional[List[Domain]] = None,
        max_results: int = 25
    ) -> List[NewsArticleDTO]:
        """
        Execute news search use case.
        
        Args:
            query: Search query string
            date_range: Date range to search within
            domains: Optional list of domains to restrict search to
            max_results: Maximum number of results to return
            
        Returns:
            List of NewsArticleDTO objects
        """
        # Call repository (domain layer)
        articles = self._news_repository.search(
            query=query,
            date_range=date_range,
            domains=domains,
            max_results=max_results
        )
        
        # Convert domain entities to DTOs (application layer mapping)
        return [self._to_dto(article) for article in articles]
    
    def _to_dto(self, article: NewsArticle) -> NewsArticleDTO:
        """
        Convert domain entity to DTO.
        
        Args:
            article: NewsArticle domain entity
            
        Returns:
            NewsArticleDTO instance
        """
        return NewsArticleDTO(
            title=article.title,
            source=article.source,
            date=article.published_date.strftime("%Y-%m-%d") if article.published_date else None,
            summary=article.summary,
            category=article.category.value,
            url=article.url
        )
