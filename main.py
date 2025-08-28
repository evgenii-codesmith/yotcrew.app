from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from datetime import datetime, timedelta
import uvicorn
import os
from contextlib import asynccontextmanager

from app.database import engine, get_db, Base
from app.models import Job, ScrapingJob
from app.scrapers.yotspot import YotspotScraper
from app.scheduler import start_scheduler, stop_scheduler

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(
    title="YotCrew.app",
    description="Real-time yacht job monitoring with HTMX and Tailwind CSS",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize scrapers
scraper = YotspotScraper()

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """Main interactive jobs page with Alpine.js features"""
    return templates.TemplateResponse("jobs.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def simple_dashboard(request: Request, db: Session = Depends(get_db)):
    """Simple dashboard page (legacy)"""
    # Get recent jobs
    recent_jobs = db.query(Job).order_by(Job.posted_at.desc()).limit(10).all()
    
    # Get stats
    total_jobs = db.query(Job).count()
    today_jobs = db.query(Job).filter(
        Job.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "recent_jobs": recent_jobs,
        "total_jobs": total_jobs,
        "today_jobs": today_jobs
    })

@app.get("/api/jobs")
async def get_jobs(
    page: int = 1,
    limit: int = 20,
    job_type: str = None,
    location: str = None,
    vessel_size: str = None,
    vessel_type: str = None,
    department: str = None,
    search: str = None,
    source: str = None,
    db: Session = Depends(get_db)
):
    """Get jobs with filtering and pagination - includes all scraped sources"""
    query = db.query(Job)
    
    # Apply source filter
    if source and source != "all":
        query = query.filter(Job.source == source)
    
    # Apply filters (check both job_type and employment_type for compatibility)
    if job_type:
        query = query.filter(
            (Job.job_type.ilike(f"%{job_type}%")) | 
            (Job.employment_type.ilike(f"%{job_type}%"))
        )
    if location:
        query = query.filter(
            (Job.location.ilike(f"%{location}%")) |
            (Job.country.ilike(f"%{location}%")) |
            (Job.region.ilike(f"%{location}%"))
        )
    if vessel_size:
        query = query.filter(Job.vessel_size.ilike(f"%{vessel_size}%"))
    if vessel_type:
        query = query.filter(Job.vessel_type.ilike(f"%{vessel_type}%"))
    if department:
        query = query.filter(Job.department.ilike(f"%{department}%"))
    if search:
        query = query.filter(
            (Job.title.ilike(f"%{search}%")) | 
            (Job.description.ilike(f"%{search}%")) |
            (Job.company.ilike(f"%{search}%"))
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination and ordering
    offset = (page - 1) * limit
    
    # Special sorting for Daywork123 by their original website ID
    if source == "daywork123":
        # Extract numeric ID from external_id (e.g., "dw123_172381" -> 172381) and sort descending
        jobs = query.order_by(
            func.cast(func.substr(Job.external_id, 7), Integer).desc()  # Skip "dw123_" prefix
        ).offset(offset).limit(limit).all()
    else:
        # Default sorting for other sources
        jobs = query.order_by(
            Job.posted_date.desc().nullslast(),
            Job.posted_at.desc().nullslast(),
            Job.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get job details"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()

@app.get("/api/jobs/stats")
async def get_job_stats(request: Request, db: Session = Depends(get_db)):
    """Get job statistics by source (HTMX-compatible)"""
    total_jobs = db.query(Job).count()
    
    # Count by source
    source_stats = db.query(Job.source, func.count(Job.id)).group_by(Job.source).all()
    source_counts = {source: count for source, count in source_stats}
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_jobs = db.query(Job).filter(Job.created_at >= week_ago).count()
    
    # Return HTMX template if requested from frontend
    if "HX-Request" in request.headers:
        return templates.TemplateResponse("partials/job_stats.html", {
            "request": request,
            "total": total_jobs,
            "sources": source_counts,
            "recent_week": recent_jobs
        })
    
    # Return JSON for API calls
    return {
        "total": total_jobs,
        "sources": source_counts,
        "recent_week": recent_jobs,
        "available_sources": list(source_counts.keys())
    }

@app.get("/htmx/jobs-table")
async def htmx_jobs_table(
    request: Request,
    page: int = 1,
    limit: int = 20,
    job_type: str = None,
    location: str = None,
    vessel_size: str = None,
    vessel_type: str = None,  # Motor Yacht, Sailing Yacht
    department: str = None,   # Deck, Interior, Engineering, Galley
    search: str = None,
    sort: str = None,  # "posted_at", "title", "salary"
    source: str = "all",  # "all", "yotspot", "daywork123", "facebook"
    db: Session = Depends(get_db)
):
    """HTMX endpoint for jobs table - supports all scraped job sources"""
    
    # Get jobs from database with enhanced filtering
    jobs_data = await get_jobs(page, limit, job_type, location, vessel_size, vessel_type, department, search, source, db)
    all_jobs = list(jobs_data["jobs"])
    total = jobs_data["total"]
    pages = jobs_data["pages"]
    
    # Apply client-side sorting if specified (database already handles basic ordering)
    if sort and sort != "posted_at":  # posted_at is already handled by database
        def get_sort_key(job, sort_field):
            if sort_field == "title":
                return (job.get('title') or '').lower()
            elif sort_field == "salary":
                # Extract numeric value from salary string for sorting
                salary = job.get('salary_range') or job.get('salary') or ''
                import re
                numbers = re.findall(r'[\d,]+', str(salary))
                if numbers:
                    try:
                        return int(numbers[0].replace(',', ''))
                    except:
                        return 0
                return 0
            elif sort_field == "quality":
                return job.get('quality_score', 0)
            return (job.get('title') or '').lower()
        
        reverse_sort = sort in ["salary", "quality"]  # These sort descending
        all_jobs.sort(key=lambda job: get_sort_key(job, sort), reverse=reverse_sort)
    
    return templates.TemplateResponse("partials/jobs_table.html", {
        "request": request,
        "jobs": all_jobs,
        "total": total,
        "page": page,
        "pages": pages
    })

@app.get("/htmx/job-card/{job_id}")
async def htmx_job_card(request: Request, job_id: str, db: Session = Depends(get_db)):
    """HTMX endpoint for job card details"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return templates.TemplateResponse("partials/job_card.html", {
        "request": request,
        "job": job
    })

@app.get("/htmx/dashboard-stats")
async def htmx_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    """HTMX endpoint for dashboard statistics"""
    total_jobs = db.query(Job).count()
    today_jobs = db.query(Job).filter(
        Job.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    week_jobs = db.query(Job).filter(
        Job.created_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    # Get latest scraping status
    latest_scrape = db.query(ScrapingJob).order_by(ScrapingJob.started_at.desc()).first()
    
    return templates.TemplateResponse("partials/dashboard_stats.html", {
        "request": request,
        "total_jobs": total_jobs,
        "today_jobs": today_jobs,
        "week_jobs": week_jobs,
        "latest_scrape": latest_scrape
    })

@app.post("/api/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    source: str = "all",
    max_pages: int = 5
):
    """Manually trigger job scraping"""
    # Create scraping job record
    scraping_job = ScrapingJob(
        status="started",
        started_at=datetime.now(),
        scraper_type=source
    )
    db.add(scraping_job)
    db.commit()
    
    # Add background task
    background_tasks.add_task(run_scrape_task, scraping_job.id, source, max_pages)
    
    return {"message": f"Scraping started for {source}", "job_id": scraping_job.id}

async def run_scrape_task(scraping_job_id: int, source: str = "all", max_pages: int = 5):
    """Background task for scraping using new scraping service"""
    from app.services.scraping_service import ScrapingService
    
    db = next(get_db())
    try:
        scraping_job = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job_id).first()
        service = ScrapingService()
        
        if source == "all":
            # Scrape all sources
            results = await service.scrape_all_sources(max_pages=max_pages)
            total_found = sum(r.get("jobs_found", 0) for r in results)
            total_new = sum(r.get("new_jobs", 0) for r in results)
        elif source == "daywork123":
            # Scrape only Daywork123
            from app.scrapers.daywork123 import Daywork123Scraper
            daywork_scraper = Daywork123Scraper()
            result = await daywork_scraper.scrape_and_save_jobs(max_pages=max_pages)
            total_found = result.get("jobs_found", 0)
            total_new = result.get("jobs_saved", 0)
        else:
            # Scrape specific source
            result = await service.scrape_source(source, max_pages=max_pages)
            total_found = result.get("jobs_found", 0)
            total_new = result.get("new_jobs", 0)
        
        # Update scraping job
        scraping_job.status = "completed"
        scraping_job.completed_at = datetime.now()
        scraping_job.jobs_found = total_found
        scraping_job.new_jobs = total_new
        db.commit()
        
    except Exception as e:
        # Update scraping job with error
        scraping_job = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job_id).first()
        if scraping_job:
            scraping_job.status = "failed"
            scraping_job.completed_at = datetime.now()
            scraping_job.error_message = str(e)
            db.commit()
    finally:
        db.close()

@app.get("/api/scrape/status")
async def scrape_status(db: Session = Depends(get_db)):
    """Get latest scraping status"""
    latest_scrape = db.query(ScrapingJob).order_by(ScrapingJob.started_at.desc()).first()
    if not latest_scrape:
        return {"status": "no_jobs"}
    
    return {
        "status": latest_scrape.status,
        "started_at": latest_scrape.started_at.isoformat(),
        "completed_at": latest_scrape.completed_at.isoformat() if latest_scrape.completed_at else None,
        "jobs_found": latest_scrape.jobs_found,
        "new_jobs": latest_scrape.new_jobs,
        "error_message": latest_scrape.error_message
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 