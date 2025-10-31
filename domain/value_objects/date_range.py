"""DateRange value object."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class DateRange:
    """
    Immutable value object representing a date range.
    
    Follows DDD principles and ensures invariants are maintained.
    """
    
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        """Validate date range invariants."""
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        
        # Prevent unreasonable date ranges
        days_diff = (self.end_date - self.start_date).days
        if days_diff > 30:
            raise ValueError("Date range cannot exceed 30 days")
    
    @classmethod
    def create_last_n_days(cls, end_date: datetime, days: int = 7) -> "DateRange":
        """
        Factory method to create a date range for the last N days.
        
        Args:
            end_date: The end date of the range
            days: Number of days to look back (default: 7)
            
        Returns:
            A new DateRange instance
        """
        if days < 1:
            raise ValueError("Days must be at least 1")
        if days > 30:
            raise ValueError("Days cannot exceed 30")
        
        start_date = end_date - timedelta(days=days)
        return cls(start_date=start_date, end_date=end_date)
    
    @classmethod
    def parse_from_turkish_date(cls, end_date_str: str, days: int = 7) -> "DateRange":
        """
        Parse date range from Turkish date string.
        
        Args:
            end_date_str: Turkish date string (e.g., "31 A?ustos 2025")
            days: Number of days to look back (default: 7)
            
        Returns:
            A new DateRange instance
        """
        end_date = cls._parse_turkish_date(end_date_str)
        return cls.create_last_n_days(end_date, days)
    
    @staticmethod
    def _parse_turkish_date(date_str: str) -> datetime:
        """
        Parse Turkish date string to datetime.
        
        Args:
            date_str: Turkish date string (e.g., "31 A?ustos 2025")
            
        Returns:
            Parsed datetime object
        """
        turkish_months = {
            'Ocak': 'January',
            '?ubat': 'February',
            'Mart': 'March',
            'Nisan': 'April',
            'May?s': 'May',
            'Haziran': 'June',
            'Temmuz': 'July',
            'A?ustos': 'August',
            'Eyl?l': 'September',
            'Ekim': 'October',
            'Kas?m': 'November',
            'Aral?k': 'December'
        }
        
        normalized_date = date_str
        for tr_month, en_month in turkish_months.items():
            normalized_date = normalized_date.replace(tr_month, en_month)
        
        try:
            return datetime.strptime(normalized_date, "%d %B %Y")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}") from e
    
    def to_days(self) -> int:
        """Get the number of days in this range."""
        return (self.end_date - self.start_date).days
    
    def format_for_display(self) -> str:
        """Format date range for display."""
        return f"{self.start_date.strftime('%d %B %Y')} ? {self.end_date.strftime('%d %B %Y')}"
