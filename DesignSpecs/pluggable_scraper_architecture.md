# Pluggable Scraping Architecture Specification
## Multi-Source Yacht Job Scraping System

### Overview
This specification redesigns the scraping system to support pluggable scrapers for multiple sources: Yotspot.com (existing), Daywork123.com, and MeridianGo.com. Each scraper is a self-contained module that implements a common interface.

---

## 1. Pluggable Architecture Design

### 1.1 Core Interface Definition
```python
# app/scrapers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator
from datetime import datetime
from pydantic import BaseModel

class ScrapingResult(BaseModel):
    """Standardized scraping result"""
    source: str
    jobs_found: int
    new_jobs: int
    updated_jobs: int
    errors: List[str]
    duration: float
    timestamp: datetime

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this scraper"""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL of the source website"""
        pass
    
    @abstractmethod
    async def scrape_jobs(self, 
                         max_pages: int = 5,
                         filters: Dict[str, Any] = None) -> AsyncIterator[Dict[str, Any]]:
        """Scrape jobs and yield standardized job data"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the source is accessible"""
        pass
    
    @abstractmethod
    def get_supported_filters(self) -> List[str]:
        """Return list of supported filter parameters"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring"""
        return {
            "source": self.source_name,
            "accessible": await self.test_connection(),
            "last_scrape": None,  # To be implemented by subclasses
            "status": "healthy"
        }
```

### 1.2 Plugin Registration System
```python
# app/scrapers/registry.py
from typing import Dict, Type
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
```

---

## 2. Standardized Data Models

### 2.1 Universal Job Schema
```python
# app/scrapers/models.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobSource(str, Enum):
    YOTSPOT = "yotspot"
    DAYWORK123 = "daywork123"
    MERIDIAN_GO = "meridian_go"

class EmploymentType(str, Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    ROTATIONAL = "rotational"
    DAYWORK = "daywork"
    SEASONAL = "seasonal"
    CONTRACT = "contract"

class Department(str, Enum):
    DECK = "deck"
    INTERIOR = "interior"
    ENGINEERING = "engineering"
    GALLEY = "galley"
    BRIDGE = "bridge"
    OTHER = "other"

class VesselType(str, Enum):
    MOTOR_YACHT = "motor_yacht"
    SAILING_YACHT = "sailing_yacht"
    CATAMARAN = "catamaran"
    SUPER_YACHT = "super_yacht"
    EXPEDITION = "expedition"
    CHASE_BOAT = "chase_boat"

class UniversalJob(BaseModel):
    """Standardized job format across all sources"""
    
    # Required fields
    external_id: str = Field(..., description="Unique ID from source")
    title: str = Field(..., min_length=3, max_length=200)
    company: str = Field(..., max_length=100)
    source: JobSource
    source_url: HttpUrl
    
    # Location
    location: str = Field(..., max_length=100)
    country: Optional[str] = None
    region: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    
    # Vessel information
    vessel_type: Optional[VesselType] = None
    vessel_size: Optional[str] = None  # e.g., "40m", "50-75m"
    vessel_name: Optional[str] = None
    
    # Employment details
    employment_type: Optional[EmploymentType] = None
    department: Optional[Department] = None
    position_level: Optional[str] = None  # Junior, Senior, Chief, etc.
    
    # Compensation
    salary_range: Optional[str] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None  # hourly, daily, monthly, yearly
    
    # Timing
    start_date: Optional[str] = None
    posted_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    
    # Content
    description: str = Field(..., min_length=10)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_data: Optional[Dict[str, Any]] = None  # Original data for debugging
    
    class Config:
        use_enum_values = True
```

---

## 3. Refactored Scraper Implementations

### 3.1 Yotspot Scraper (Refactored)
```python
# app/scrapers/yotspot.py
from .base import BaseScraper, register_scraper
from .models import UniversalJob, JobSource
import asyncio
import aiohttp
from bs4 import BeautifulSoup

@register_scraper
class YotspotScraper(BaseScraper):
    """Refactored Yotspot scraper implementing pluggable interface"""
    
    @property
    def source_name(self) -> str:
        return JobSource.YOTSPOT
    
    @property
    def base_url(self) -> str:
        return "https://www.yotspot.com"
    
    async def scrape_jobs(self, max_pages=5, filters=None):
        """Implement standardized scraping interface"""
        async with aiohttp.ClientSession() as session:
            for page in range(1, max_pages + 1):
                jobs = await self._scrape_page(session, page, filters)
                for job in jobs:
                    yield self._normalize_job(job)
    
    async def test_connection(self) -> bool:
        """Test Yotspot accessibility"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url) as response:
                    return response.status == 200
        except:
            return False
    
    def get_supported_filters(self) -> List[str]:
        return ["location", "department", "vessel_type", "salary_range"]
    
    async def _scrape_page(self, session, page, filters):
        """Scrape individual page"""
        # Implementation here
        pass
    
    def _normalize_job(self, raw_job):
        """Convert raw job to UniversalJob format"""
        return UniversalJob(
            external_id=raw_job.get("id"),
            title=raw_job.get("title"),
            company=raw_job.get("company"),
            source=self.source_name,
            source_url=raw_job.get("url"),
            location=raw_job.get("location", ""),
            vessel_type=raw_job.get("vessel_type"),
            employment_type=raw_job.get("job_type"),
            department=raw_job.get("department"),
            salary_range=raw_job.get("salary_range"),
            description=raw_job.get("description", ""),
            posted_date=raw_job.get("posted_at"),
            raw_data=raw_job
        )
```

### 3.2 Daywork123 Scraper
```python
# app/scrapers/daywork123.py
from .base import BaseScraper, register_scraper
from .models import UniversalJob, JobSource
import asyncio
from playwright.async_api import async_playwright

@register_scraper
class Daywork123Scraper(BaseScraper):
    """Daywork123.com scraper with anti-detection"""
    
    @property
    def source_name(self) -> str:
        return JobSource.DAYWORK123
    
    @property
    def base_url(self) -> str:
        return "https://www.daywork123.com"
    
    async def scrape_jobs(self, max_pages=5, filters=None):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Anti-detection setup
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            try:
                for page_num in range(1, max_pages + 1):
                    jobs = await self._scrape_page_with_browser(page, page_num, filters)
                    for job in jobs:
                        yield self._normalize_job(job)
            finally:
                await browser.close()
    
    async def test_connection(self) -> bool:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                response = await page.goto(self.base_url)
                await browser.close()
                return response.status == 200
        except:
            return False
    
    def get_supported_filters(self) -> List[str]:
        return ["location", "date_range", "job_type", "vessel_size"]
```

### 3.3 MeridianGo Scraper
```python
# app/scrapers/meridian_go.py
from .base import BaseScraper, register_scraper
from .models import UniversalJob, JobSource
import aiohttp
from bs4 import BeautifulSoup

@register_scraper
class MeridianGoScraper(BaseScraper):
    """MeridianGo.com scraper"""
    
    @property
    def source_name(self) -> str:
        return JobSource.MERIDIAN_GO
    
    @property
    def base_url(self) -> str:
        return "https://www.meridiango.com"
    
    async def scrape_jobs(self, max_pages=5, filters=None):
        async with aiohttp.ClientSession() as session:
            for page in range(1, max_pages + 1):
                jobs = await self._scrape_page(session, page, filters)
                for job in jobs:
                    yield self._normalize_job(job)
    
    async def test_connection(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url) as response:
                    return response.status == 200
        except:
            return False
    
    def get_supported_filters(self) -> List[str]:
        return ["location", "category", "experience_level"]
```

---

## 4. Orchestrator Service

### 4.1 Unified Scraping Service
```python
# app/services/scraping_service.py
from typing import List, Dict, Any
from app.scrapers.registry import ScraperRegistry
from app.scrapers.models import UniversalJob
from app.database import SessionLocal
from sqlalchemy.orm import Session

class ScrapingService:
    """Unified service for managing all scrapers"""
    
    def __init__(self):
        self.registry = ScraperRegistry()
    
    async def scrape_source(self, source_name: str, max_pages: int = 5) -> Dict[str, Any]:
        """Scrape a specific source"""
        scraper = self.registry.get_scraper(source_name)
        
        jobs = []
        async for job in scraper.scrape_jobs(max_pages=max_pages):
            jobs.append(job)
        
        # Save to database
        saved_count = await self._save_jobs(jobs)
        
        return {
            "source": source_name,
            "jobs_found": len(jobs),
            "jobs_saved": saved_count,
            "timestamp": datetime.utcnow()
        }
    
    async def scrape_all_sources(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Scrape all registered sources"""
        results = []
        for source_name in self.registry.list_scrapers():
            result = await self.scrape_source(source_name, max_pages)
            results.append(result)
        return results
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Health check for all scrapers"""
        health_status = {}
        for scraper in self.registry.get_all_scrapers():
            health_status[scraper.source_name] = await scraper.health_check()
        return health_status
    
    async def _save_jobs(self, jobs: List[UniversalJob]) -> int:
        """Save jobs to database with deduplication"""
        # Implementation for database saving
        pass
```

---

## 5. Scheduler Integration

### 5.1 Updated Scheduler
```python
# app/scheduler.py (updated)
from app.services.scraping_service import ScrapingService

class ScrapingScheduler:
    def __init__(self):
        self.service = ScrapingService()
    
    async def scrape_all_sources(self):
        """Scrape all sources with staggered timing"""
        sources = ["yotspot", "daywork123", "meridian_go"]
        
        for source in sources:
            try:
                result = await self.service.scrape_source(source, max_pages=5)
                logger.info(f"Scraped {result['jobs_found']} jobs from {source}")
            except Exception as e:
                logger.error(f"Failed to scrape {source}: {e}")
            
            # Stagger requests to avoid overwhelming sources
            await asyncio.sleep(30)
```

---

## 6. Configuration Management

### 6.1 Source-Specific Configuration
```python
# app/config/scraping.py
from pydantic import BaseSettings, Field

class ScrapingConfig(BaseSettings):
    # Global settings
    max_concurrent_requests: int = 3
    request_delay: float = 2.5
    max_retries: int = 3
    
    # Source-specific settings
    yotspot_enabled: bool = True
    yotspot_max_pages: int = 5
    
    daywork123_enabled: bool = True
    daywork123_max_pages: int = 5
    daywork123_use_playwright: bool = True
    
    meridian_go_enabled: bool = True
    meridian_go_max_pages: int = 5
    
    class Config:
        env_prefix = "SCRAPER_"
```

---

## 7. Testing Framework

### 7.1 Unified Testing
```python
# tests/test_pluggable_scrapers.py
import pytest
from app.scrapers.registry import ScraperRegistry
from app.scrapers.models import UniversalJob

@pytest.mark.asyncio
async def test_all_scrapers():
    """Test all registered scrapers"""
    registry = ScraperRegistry()
    
    for source_name in registry.list_scrapers():
        scraper = registry.get_scraper(source_name)
        
        # Test connection
        assert await scraper.test_connection(), f"{source_name} not accessible"
        
        # Test scraping
        jobs = []
        async for job in scraper.scrape_jobs(max_pages=1):
            assert isinstance(job, UniversalJob)
            jobs.append(job)
        
        assert len(jobs) > 0, f"No jobs found for {source_name}"
```

---

## 8. Migration Strategy

### 8.1 Gradual Rollout
1. **Phase 1**: Keep existing Yotspot scraper as-is
2. **Phase 2**: Add new pluggable Yotspot scraper alongside existing
3. **Phase 3**: Switch to pluggable system for all sources
4. **Phase 4**: Deprecate old scrapers

### 8.2 Backward Compatibility
```python
# app/scrapers/legacy.py
from app.scrapers.yotspot import YotspotScraper

# Temporary compatibility layer
class LegacyYotspotScraper(YotspotScraper):
    """Backward-compatible scraper during transition"""
    async def scrape_jobs_old(self, *args, **kwargs):
        """Old interface for compatibility"""
        jobs = []
        async for job in self.scrape_jobs(*args, **kwargs):
            jobs.append(job.dict())
        return jobs
```

---

## 9. Quick Start Commands

### 9.1 Register All Scrapers
```python
# app/scrapers/__init__.py
from .yotspot import YotspotScraper
from .daywork123 import Daywork123Scraper
from .meridian_go import MeridianGoScraper

# Auto-registration happens via decorators
```

### 9.2 Usage Examples
```python
# Single source scraping
from app.services.scraping_service import ScrapingService

service = ScrapingService()
result = await service.scrape_source("daywork123", max_pages=3)

# All sources
results = await service.scrape_all_sources(max_pages=5)

# Health check
health = await service.health_check_all()
```

This pluggable architecture allows easy addition of new scrapers while maintaining a consistent interface across all sources.