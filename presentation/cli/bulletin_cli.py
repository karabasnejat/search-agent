"""BulletinCLI - Command Line Interface for the bulletin generator."""

from datetime import datetime
from typing import Optional

from application.dto.bulletin_dto import BulletinDTO
from application.use_cases.generate_bulletin_use_case import GenerateBulletinUseCase
from domain.value_objects.date_range import DateRange
from domain.value_objects.domain import Domain


class BulletinCLI:
    """
    Command Line Interface for bulletin generation.
    
    Follows Single Responsibility Principle - handles only CLI interaction.
    Part of presentation layer - coordinates use cases and handles I/O.
    """
    
    def __init__(self, generate_bulletin_use_case: GenerateBulletinUseCase):
        """
        Initialize CLI with use case.
        
        Args:
            generate_bulletin_use_case: Use case for generating bulletins
        """
        self._generate_bulletin_use_case = generate_bulletin_use_case
    
    def run(self, end_date_str: Optional[str] = None) -> BulletinDTO:
        """
        Run the CLI application.
        
        Args:
            end_date_str: Optional end date string (if None, prompts user)
            
        Returns:
            Generated BulletinDTO
        """
        print("Haber b?lteni olu?turucu")
        print("=" * 40)
        
        # Get end date
        if not end_date_str:
            end_date_str = input("Biti? tarihini girin (?rn: 31 A?ustos 2025): ").strip()
        
        if not end_date_str:
            end_date_str = datetime.now().strftime("%d %B %Y")
            print(f"Varsay?lan tarih kullan?l?yor: {end_date_str}")
        
        # Parse date range
        try:
            date_range = DateRange.parse_from_turkish_date(end_date_str, days=7)
        except ValueError as e:
            print(f"Hata: {e}")
            raise
        
        print(f"\nTarih aral???: {date_range.format_for_display()}")
        
        # Get default domains
        domains = Domain.create_default_domains()
        print(f"Kaynaklar: {len(domains)} domain")
        print("-" * 40)
        
        # Generate bulletin
        print("\nB?lten olu?turuluyor...")
        bulletin = self._generate_bulletin_use_case.execute(
            query="artificial intelligence AI machine learning deep learning GPT ChatGPT OpenAI Google Microsoft Meta yapay zeka",
            date_range=date_range,
            domains=domains,
            max_results=25
        )
        
        return bulletin
    
    def display_bulletin(self, bulletin: BulletinDTO):
        """
        Display bulletin to console.
        
        Args:
            bulletin: BulletinDTO to display
        """
        print("\n" + "=" * 50)
        print("OLU?TURULAN HABER B?LTEN?")
        print("=" * 50)
        print(f"\n?? Tarih Aral???: {bulletin.date_range}")
        print(f"?? Haber Say?s?: {bulletin.article_count}\n")
        print(bulletin.content)
    
    def save_bulletin(self, bulletin: BulletinDTO, filepath: Optional[str] = None):
        """
        Save bulletin to file.
        
        Args:
            bulletin: BulletinDTO to save
            filepath: Optional filepath (if None, generates timestamped filename)
        """
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"haber_bulteni_{timestamp}.txt"
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Haftal?k AI B?lteni\n")
                f.write(f"{bulletin.date_range}\n")
                f.write(f"Haber Say?s?: {bulletin.article_count}\n\n")
                f.write(bulletin.content)
            print(f"\n? B?lten kaydedildi: {filepath}")
        except Exception as e:
            print(f"\n? Dosya kaydetme hatas?: {e}")
