from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, func
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
    vessel_type = Column(String)  # Motor Yacht, Sailing Yacht, etc.
    vessel_size = Column(String)  # 40m+, 50-74m, etc.
    job_type = Column(String)     # Permanent, Temporary, Rotational
    department = Column(String)   # Deck, Interior, Engineering, etc.
    salary_range = Column(String)
    salary_per = Column(String)   # per day, per month, per year
    start_date = Column(String)
    description = Column(Text)
    posted_at = Column(DateTime)
    source_url = Column(String)
    source = Column(String, default="yotspot")
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "vessel_type": self.vessel_type,
            "vessel_size": self.vessel_size,
            "job_type": self.job_type,
            "department": self.department,
            "salary_range": self.salary_range,
            "salary_per": self.salary_per,
            "start_date": self.start_date,
            "description": self.description,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "source_url": self.source_url,
            "source": self.source,
            "is_featured": self.is_featured,
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