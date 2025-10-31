"""GenerateBulletinUseCase - Application use case for generating bulletins."""

from typing import List, Optional

from application.dto.bulletin_dto import BulletinDTO
from domain.entities.news_article import NewsArticle
from domain.repositories.inews_repository import INewsRepository
from domain.value_objects.date_range import DateRange
from domain.value_objects.domain import Domain


class IBulletinWriter:
    """
    Interface for bulletin writing service.
    
    Follows Interface Segregation Principle - focused interface.
    """
    
    def write_bulletin(
        self,
        articles: List[NewsArticle],
        date_range: DateRange
    ) -> str:
        """
        Write a bulletin from news articles.
        
        Args:
            articles: List of news articles
            date_range: Date range for the bulletin
            
        Returns:
            Formatted bulletin content
        """
        raise NotImplementedError


class GenerateBulletinUseCase:
    """
    Use case for generating weekly AI bulletins.
    
    Follows Single Responsibility Principle - handles only bulletin generation logic.
    Uses Dependency Inversion Principle by depending on abstractions.
    """
    
    def __init__(
        self,
        news_repository: INewsRepository,
        bulletin_writer: IBulletinWriter
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            news_repository: Repository for news articles
            bulletin_writer: Service for writing bulletins
        """
        self._news_repository = news_repository
        self._bulletin_writer = bulletin_writer
    
    def execute(
        self,
        query: str,
        date_range: DateRange,
        domains: Optional[List[Domain]] = None,
        max_results: int = 25
    ) -> BulletinDTO:
        """
        Execute bulletin generation use case.
        
        Args:
            query: Search query string
            date_range: Date range to search within
            domains: Optional list of domains to restrict search to
            max_results: Maximum number of results to return
            
        Returns:
            BulletinDTO instance
        """
        # Search for news articles
        articles = self._news_repository.search(
            query=query,
            date_range=date_range,
            domains=domains,
            max_results=max_results
        )
        
        # Filter articles by date range (domain logic)
        filtered_articles = [
            article for article in articles
            if article.is_in_date_range(date_range.start_date, date_range.end_date)
        ]
        
        # Generate bulletin content
        bulletin_content = self._bulletin_writer.write_bulletin(
            articles=filtered_articles,
            date_range=date_range
        )
        
        return BulletinDTO(
            content=bulletin_content,
            date_range=date_range.format_for_display(),
            article_count=len(filtered_articles)
        )
