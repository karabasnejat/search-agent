"""Domain value object for source domains."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Domain:
    """
    Immutable value object representing a source domain.
    
    Follows DDD principles for domain modeling.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate domain invariants."""
        if not self.value or not self.value.strip():
            raise ValueError("Domain cannot be empty")
        
        # Basic domain validation
        if " " in self.value:
            raise ValueError("Domain cannot contain spaces")
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value
    
    @classmethod
    def create_default_domains(cls) -> List["Domain"]:
        """
        Factory method to create default list of trusted domains.
        
        Returns:
            List of Domain value objects
        """
        domain_strings = [
            "techcrunch.com",
            "venturebeat.com",
            "theverge.com",
            "wired.com",
            "semafor.com",
            "openai.com/blog",
            "anthropic.com/news",
            "google.ai/blog",
            "meta.ai/news",
            "huggingface.co/blog",
            "microsoft.com/blog",
            "nvidia.com/newsroom",
            "stability.ai/blog",
            "midjourney.com",
            "deepmind.google",
            "artificialintelligence-news.com",
            "donanimhaber.com/yapay-zeka"
        ]
        
        return [cls(value=domain) for domain in domain_strings]
