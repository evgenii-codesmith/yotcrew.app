"""Base scraper interface for pluggable architecture"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class JobSource(str, Enum):
    """Supported job sources"""
    YOTSPOT = "yotspot"
    DAYWORK123 = "daywork123"
    MERIDIAN_GO = "meridian_go"

class EmploymentType(str, Enum):
    """Employment types across all sources"""
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    ROTATIONAL = "rotational"
    DAYWORK = "daywork"
    SEASONAL = "seasonal"
    CONTRACT = "contract"

class Department(str, Enum):
    """Yacht departments"""
    DECK = "deck"
    INTERIOR = "interior"
    ENGINEERING = "engineering"
    GALLEY = "galley"
    BRIDGE = "bridge"
    OTHER = "other"

class VesselType(str, Enum):
    """Types of vessels"""
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
    
    # Vessel information
    vessel_type: Optional[VesselType] = None
    vessel_size: Optional[str] = None
    vessel_name: Optional[str] = None
    
    # Employment details
    employment_type: Optional[EmploymentType] = None
    department: Optional[Department] = None
    position_level: Optional[str] = None
    
    # Compensation
    salary_range: Optional[str] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    
    # Timing
    start_date: Optional[str] = None
    posted_date: Optional[datetime] = None
    
    # Content
    description: str = Field(..., min_length=10)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_data: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True

class ScrapingResult(BaseModel):
    """Result from scraping operation"""
    source: str
    jobs_found: int
    new_jobs: int
    updated_jobs: int
    errors: List[str] = Field(default_factory=list)
    duration: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

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
                         filters: Optional[Dict[str, Any]] = None) -> AsyncIterator[UniversalJob]:
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
            "last_scrape": None,
            "status": "healthy" if await self.test_connection() else "unhealthy"
        }