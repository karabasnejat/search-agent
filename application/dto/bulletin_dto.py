"""BulletinDTO - Data Transfer Object for bulletins."""

from dataclasses import dataclass


@dataclass
class BulletinDTO:
    """DTO for transferring bulletin data."""
    
    content: str
    date_range: str
    article_count: int
