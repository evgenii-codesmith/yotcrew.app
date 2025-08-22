from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, func, JSON
from datetime import datetime
from .database import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String, unique=True, index=True)  # ID from source website
    title = Column(String, nullable=False)
    company = Column(String)
    location = Column(String)
    
    # Vessel information
    vessel_type = Column(String)  # Motor Yacht, Sailing Yacht, etc.
    vessel_size = Column(String)  # 40m+, 50-74m, etc.
    vessel_name = Column(String)
    
    # Employment details
    job_type = Column(String)     # Permanent, Temporary, Rotational  
    employment_type = Column(String)  # For compatibility with UniversalJob
    department = Column(String)   # Deck, Interior, Engineering, etc.
    position_level = Column(String)
    
    # Compensation
    salary_range = Column(String)
    salary_currency = Column(String)
    salary_per = Column(String)   # per day, per month, per year
    salary_period = Column(String)  # For compatibility with UniversalJob
    
    # Timing
    start_date = Column(String)
    posted_at = Column(DateTime)
    posted_date = Column(DateTime)  # For compatibility with UniversalJob
    
    # Content
    description = Column(Text)
    requirements = Column(JSON)  # Store as JSON array
    benefits = Column(JSON)      # Store as JSON array
    
    # Location details
    country = Column(String)
    region = Column(String)
    
    # Metadata
    source_url = Column(String)
    source = Column(String, default="yotspot")
    is_featured = Column(Boolean, default=False)
    quality_score = Column(Float, default=0.0)
    raw_data = Column(JSON)  # Store raw scraping data
    scraped_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "country": self.country,
            "region": self.region,
            "vessel_type": self.vessel_type,
            "vessel_size": self.vessel_size,
            "vessel_name": self.vessel_name,
            "job_type": self.job_type,
            "employment_type": self.employment_type,
            "department": self.department,
            "position_level": self.position_level,
            "salary_range": self.salary_range,
            "salary_currency": self.salary_currency,
            "salary_per": self.salary_per,
            "salary_period": self.salary_period,
            "start_date": self.start_date,
            "description": self.description,
            "requirements": self.requirements,
            "benefits": self.benefits,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "source_url": self.source_url,
            "source": self.source,
            "is_featured": self.is_featured,
            "quality_score": self.quality_score,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")  # pending, started, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    jobs_found = Column(Integer, default=0)
    new_jobs = Column(Integer, default=0)
    error_message = Column(Text)
    scraper_type = Column(String, default="yotspot")
    
    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "jobs_found": self.jobs_found,
            "new_jobs": self.new_jobs,
            "error_message": self.error_message,
            "scraper_type": self.scraper_type
        } 