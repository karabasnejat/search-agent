"""TavilyNewsRepository - Infrastructure implementation of INewsRepository."""

from typing import List, Optional

from tavily import TavilyClient

from domain.entities.news_article import NewsArticle
from domain.exceptions import RepositoryException
from domain.repositories.inews_repository import INewsRepository
from domain.value_objects.article_category import ArticleCategory
from domain.value_objects.date_range import DateRange
from domain.value_objects.domain import Domain


class TavilyNewsRepository(INewsRepository):
    """
    Tavily API implementation of news repository.
    
    Follows Dependency Inversion Principle by implementing domain interface.
    Belongs to infrastructure layer - handles external API communication.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize repository with Tavily API key.
        
        Args:
            api_key: Tavily API key
        """
        self._client = TavilyClient(api_key=api_key)
    
    def search(
        self,
        query: str,
        date_range: DateRange,
        domains: Optional[List[Domain]] = None,
        max_results: int = 25
    ) -> List[NewsArticle]:
        """
        Search for news articles using Tavily API.
        
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
        try:
            # Convert Domain value objects to strings for API
            domain_strings = [str(domain) for domain in domains] if domains else None
            
            # Search using Tavily API
            response = self._client.search(
                query=query,
                search_depth="advanced",
                topic="news",
                days=date_range.to_days(),
                max_results=max_results,
                include_raw_content=True,
                include_domains=domain_strings
            )
            
            # Convert API response to domain entities
            return self._to_domain_entities(response)
            
        except Exception as e:
            raise RepositoryException(f"Failed to search news: {str(e)}") from e
    
    def _to_domain_entities(self, api_response: dict) -> List[NewsArticle]:
        """
        Convert Tavily API response to domain entities.
        
        Args:
            api_response: Response from Tavily API
            
        Returns:
            List of NewsArticle domain entities
        """
        if not api_response or 'results' not in api_response:
            return []
        
        articles = []
        for result in api_response.get('results', []):
            try:
                article = self._map_to_entity(result)
                articles.append(article)
            except (ValueError, KeyError) as e:
                # Skip invalid articles but log error
                continue
        
        return articles
    
    def _map_to_entity(self, result: dict) -> NewsArticle:
        """
        Map API result to NewsArticle domain entity.
        
        Args:
            result: Single result from Tavily API
            
        Returns:
            NewsArticle domain entity
            
        Raises:
            ValueError: If mapping fails
        """
        from datetime import datetime
        
        title = result.get('title', '').strip()
        url = result.get('url', '').strip()
        content = result.get('content', '').strip()
        published_date_str = result.get('published_date', '')
        
        # Extract source from URL
        source = self._extract_source_from_url(url)
        
        # Parse published date
        published_date = None
        if published_date_str:
            try:
                published_date = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        # Categorize article
        category = self._categorize_article(title, content)
        
        return NewsArticle(
            title=title,
            source=source,
            url=url,
            summary=content[:500] if content else "No summary available",  # Limit summary length
            category=category,
            published_date=published_date
        )
    
    def _extract_source_from_url(self, url: str) -> str:
        """
        Extract source name from URL.
        
        Args:
            url: Article URL
            
        Returns:
            Source name
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            return domain.replace('www.', '')
        except Exception:
            return "Unknown Source"
    
    def _categorize_article(self, title: str, content: str) -> ArticleCategory:
        """
        Categorize article based on title and content.
        
        Args:
            title: Article title
            text: Article content
            
        Returns:
            ArticleCategory enum value
        """
        text = (title + " " + content).lower()
        
        # Model releases
        if any(keyword in text for keyword in ['model', 'gpt', 'claude', 'gemini', 'release', 'launch', 'announce']):
            return ArticleCategory.MODEL_RELEASE
        
        # Investments
        if any(keyword in text for keyword in ['investment', 'funding', 'million', 'billion', 'raise', 'capital']):
            return ArticleCategory.INVESTMENT
        
        # Research
        if any(keyword in text for keyword in ['research', 'benchmark', 'study', 'paper', 'academic']):
            return ArticleCategory.RESEARCH_BREAKTHROUGH
        
        # Ethics
        if any(keyword in text for keyword in ['ethics', 'bias', 'fairness', 'regulation', 'safety']):
            return ArticleCategory.ETHICS_INCIDENT
        
        # Competitive
        if any(keyword in text for keyword in ['competition', 'versus', 'vs', 'battle', 'rival']):
            return ArticleCategory.COMPETITIVE_DYNAMICS
        
        # Creative
        if any(keyword in text for keyword in ['creative', 'art', 'music', 'generation', 'synthesis']):
            return ArticleCategory.CREATIVE_APPLICATION
        
        return ArticleCategory.GENERAL
