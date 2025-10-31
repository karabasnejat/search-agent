"""ArticleCategory value object."""

from enum import Enum


class ArticleCategory(str, Enum):
    """Enumeration of article categories following DDD value object pattern."""
    
    MODEL_RELEASE = "Model Release"
    INVESTMENT = "Investment / Government Policy"
    COMPETITIVE_DYNAMICS = "Competitive Dynamics"
    RESEARCH_BREAKTHROUGH = "Research / Benchmark"
    ETHICS_INCIDENT = "Ethics / Societal Impact"
    CREATIVE_APPLICATION = "Creative Application"
    GENERAL = "General"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value
