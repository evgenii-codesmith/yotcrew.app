"""Unified scraping service for managing all scrapers"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.scrapers.registry import ScraperRegistry
from app.scrapers.base import UniversalJob
from app.database import SessionLocal
from app.models import Job

logger = logging.getLogger(__name__)

class ScrapingService:
    """Unified service for managing all scrapers"""
    
    def __init__(self):
        self.registry = ScraperRegistry()
    
    async def scrape_source(self, source_name: str, max_pages: int = 5) -> Dict[str, Any]:
        """Scrape a specific source"""
        try:
            scraper = self.registry.get_scraper(source_name)
            
            start_time = datetime.utcnow()
            jobs_found = 0
            new_jobs = 0
            updated_jobs = 0
            errors = []
            
            # Collect all jobs
            jobs = []
            async for job in scraper.scrape_jobs(max_pages=max_pages):
                jobs.append(job)
                jobs_found += 1
            
            # Save to database
            if jobs:
                new_jobs, updated_jobs = await self._save_jobs(jobs)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                "source": source_name,
                "jobs_found": jobs_found,
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs,
                "errors": errors,
                "duration": duration,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Scraped {source_name}: {jobs_found} found, {new_jobs} new, {updated_jobs} updated")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
            return {
                "source": source_name,
                "jobs_found": 0,
                "new_jobs": 0,
                "updated_jobs": 0,
                "errors": [str(e)],
                "duration": 0,
                "timestamp": datetime.utcnow()
            }
    
    async def scrape_all_sources(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Scrape all registered sources"""
        results = []
        sources = self.registry.list_scrapers()
        
        for source_name in sources:
            result = await self.scrape_source(source_name, max_pages)
            results.append(result)
            
            # Add delay between sources to be respectful
            if source_name != sources[-1]:
                await asyncio.sleep(30)
        
        return results
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Health check for all scrapers"""
        health_status = {}
        
        for scraper in self.registry.get_all_scrapers():
            try:
                health_status[scraper.source_name] = await scraper.health_check()
            except Exception as e:
                health_status[scraper.source_name] = {
                    "source": scraper.source_name,
                    "accessible": False,
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status
    
    async def _save_jobs(self, jobs: List[UniversalJob]) -> tuple[int, int]:
        """Save jobs to database with deduplication"""
        new_jobs_count = 0
        updated_jobs_count = 0
        
        with SessionLocal() as db:
            for job in jobs:
                try:
                    # Check if job already exists
                    existing_job = db.query(Job).filter(
                        Job.external_id == job.external_id,
                        Job.source == job.source
                    ).first()
                    
                    if existing_job:
                        # Update existing job
                        existing_job.title = job.title
                        existing_job.company = job.company
                        existing_job.location = job.location
                        existing_job.description = job.description
                        existing_job.salary_range = job.salary_range
                        existing_job.employment_type = job.employment_type
                        existing_job.department = job.department
                        existing_job.vessel_type = job.vessel_type
                        existing_job.quality_score = job.quality_score
                        existing_job.updated_at = datetime.utcnow()
                        
                        updated_jobs_count += 1
                    else:
                        # Create new job
                        db_job = Job(
                            external_id=job.external_id,
                            title=job.title,
                            company=job.company,
                            location=job.location,
                            description=job.description,
                            source=job.source,
                            source_url=str(job.source_url),
                            salary_range=job.salary_range,
                            employment_type=job.employment_type,
                            department=job.department,
                            vessel_type=job.vessel_type,
                            posted_date=job.posted_date,
                            quality_score=job.quality_score,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(db_job)
                        new_jobs_count += 1
                
                except Exception as e:
                    logger.error(f"Error saving job {job.title}: {e}")
                    continue
            
            try:
                db.commit()
            except Exception as e:
                logger.error(f"Error committing jobs to database: {e}")
                db.rollback()
                return 0, 0
        
        return new_jobs_count, updated_jobs_count
    
    def get_scraper_stats(self) -> Dict[str, Any]:
        """Get statistics for all scrapers"""
        stats = {
            "total_scrapers": len(self.registry.list_scrapers()),
            "available_scrapers": self.registry.list_scrapers(),
            "health_status": {}
        }
        
        # Get health status for each scraper
        for scraper in self.registry.get_all_scrapers():
            stats["health_status"][scraper.source_name] = {
                "supported_filters": scraper.get_supported_filters(),
                "base_url": scraper.base_url
            }
        
        return stats

# Convenience functions for backward compatibility
async def scrape_daywork123(max_pages: int = 5) -> Dict[str, Any]:
    """Convenience function to scrape Daywork123.com"""
    service = ScrapingService()
    return await service.scrape_source("daywork123", max_pages)

async def scrape_yotspot(max_pages: int = 5) -> Dict[str, Any]:
    """Convenience function to scrape Yotspot.com"""
    service = ScrapingService()
    return await service.scrape_source("yotspot", max_pages)

async def scrape_all_sources(max_pages: int = 5) -> List[Dict[str, Any]]:
    """Convenience function to scrape all sources"""
    service = ScrapingService()
    return await service.scrape_all_sources(max_pages)