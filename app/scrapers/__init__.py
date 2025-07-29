"""Pluggable scrapers package for yacht job sources"""
from .base import BaseScraper, ScrapingResult, UniversalJob
from .registry import ScraperRegistry, register_scraper

# Import all scrapers - they auto-register via decorators
from .yotspot import YotspotScraper
from .daywork123 import Daywork123Scraper

__all__ = [
    'BaseScraper',
    'ScrapingResult', 
    'UniversalJob',
    'ScraperRegistry',
    'register_scraper'
]