"""Registry for managing pluggable scrapers"""
from typing import Dict, Type, List
from .base import BaseScraper

class ScraperRegistry:
    """Registry for managing pluggable scrapers"""
    
    _scrapers: Dict[str, Type[BaseScraper]] = {}
    
    @classmethod
    def register(cls, scraper_class: Type[BaseScraper]):
        """Register a new scraper"""
        instance = scraper_class()
        cls._scrapers[instance.source_name] = scraper_class
    
    @classmethod
    def get_scraper(cls, source_name: str) -> BaseScraper:
        """Get scraper instance by source name"""
        if source_name not in cls._scrapers:
            raise ValueError(f"Unknown scraper: {source_name}")
        return cls._scrapers[source_name]()
    
    @classmethod
    def list_scrapers(cls) -> List[str]:
        """List all registered scrapers"""
        return list(cls._scrapers.keys())
    
    @classmethod
    def get_all_scrapers(cls) -> List[BaseScraper]:
        """Get instances of all scrapers"""
        return [scraper_class() for scraper_class in cls._scrapers.values()]

# Auto-registration decorator
def register_scraper(cls):
    """Decorator to automatically register scrapers"""
    ScraperRegistry.register(cls)
    return cls