"""
🧩 AI Researcher & Bulletin Writer Multi-Agent System

Main entry point with dependency injection container.

This system follows Domain Driven Design principles with Clean Architecture:
- Domain Layer: Core business logic, entities, value objects, repository interfaces
- Application Layer: Use cases, DTOs
- Infrastructure Layer: External API implementations, repository implementations
- Presentation Layer: CLI interface, formatters

SOLID Principles:
- Single Responsibility: Each class has one reason to change
- Open/Closed: Open for extension via interfaces, closed for modification
- Liskov Substitution: Implementations are substitutable via interfaces
- Interface Segregation: Focused interfaces (INewsRepository, IBulletinWriter)
- Dependency Inversion: Depend on abstractions, not concretions
"""

import os
from typing import Optional

from application.use_cases.generate_bulletin_use_case import GenerateBulletinUseCase
from domain.value_objects.domain import Domain
from infrastructure.ai.openai_bulletin_writer import OpenAIBulletinWriter
from infrastructure.repositories.tavily_news_repository import TavilyNewsRepository
from presentation.cli.bulletin_cli import BulletinCLI


class DependencyContainer:
    """
    Dependency Injection Container.
    
    Centralizes object creation and dependency management following
    Dependency Inversion Principle.
    """
    
    def __init__(self, tavily_api_key: str, openai_api_key: str):
        """
        Initialize container with API keys.
        
        Args:
            tavily_api_key: Tavily API key
            openai_api_key: OpenAI API key
        """
        # Infrastructure layer - external services
        self._news_repository = TavilyNewsRepository(api_key=tavily_api_key)
        self._bulletin_writer = OpenAIBulletinWriter(api_key=openai_api_key)
        
        # Application layer - use cases
        self._generate_bulletin_use_case = GenerateBulletinUseCase(
            news_repository=self._news_repository,
            bulletin_writer=self._bulletin_writer
        )
        
        # Presentation layer - CLI
        self._cli = BulletinCLI(
            generate_bulletin_use_case=self._generate_bulletin_use_case
        )
    
    @property
    def cli(self) -> BulletinCLI:
        """Get CLI instance."""
        return self._cli
    
    @property
    def generate_bulletin_use_case(self) -> GenerateBulletinUseCase:
        """Get bulletin generation use case."""
        return self._generate_bulletin_use_case


def main():
    """Main entry point."""
    # Load API keys from environment or use empty strings
    tavily_api_key = os.getenv("TAVILY_API_KEY", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    
    # Validate API keys
    if not tavily_api_key:
        print("⚠️  UYARI: TAVILY_API_KEY environment variable not set")
        tavily_api_key = input("Tavily API anahtarını girin (veya Enter'a basın): ").strip()
    
    if not openai_api_key:
        print("⚠️  UYARI: OPENAI_API_KEY environment variable not set")
        openai_api_key = input("OpenAI API anahtarını girin (veya Enter'a basın): ").strip()
    
    if not tavily_api_key or not openai_api_key:
        print("❌ Hata: API anahtarları gerekli!")
        return
    
    # Initialize dependency container
    container = DependencyContainer(
        tavily_api_key=tavily_api_key,
        openai_api_key=openai_api_key
    )
    
    # Run CLI
    try:
        bulletin = container.cli.run()
        container.cli.display_bulletin(bulletin)
        container.cli.save_bulletin(bulletin)
    except Exception as e:
        print(f"❌ Hata: {e}")
        raise


if __name__ == "__main__":
    main()
