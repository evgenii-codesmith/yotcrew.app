from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uvicorn
import os
from contextlib import asynccontextmanager

from app.database import engine, get_db, Base
from app.models import Job, ScrapingJob
from app.scraper import YotspotScraper
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
    db: Session = Depends(get_db)
):
    """Get jobs with filtering and pagination"""
    query = db.query(Job)
    
    # Apply filters
    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if vessel_size:
        query = query.filter(Job.vessel_size.ilike(f"%{vessel_size}%"))
    if vessel_type:
        query = query.filter(Job.vessel_type.ilike(f"%{vessel_type}%"))
    if department:
        query = query.filter(Job.department.ilike(f"%{department}%"))
    if search:
        query = query.filter(
            Job.title.ilike(f"%{search}%") | 
            Job.description.ilike(f"%{search}%")
        )
    
    # Pagination
    offset = (page - 1) * limit
    jobs = query.order_by(Job.posted_at.desc()).offset(offset).limit(limit).all()
    total = query.count()
    
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
    source: str = "all",  # "all", "yotspot", "facebook"
    db: Session = Depends(get_db)
):
    """HTMX endpoint for jobs table - supports both Yotspot and Facebook jobs"""
    
    # Get regular Yotspot jobs
    yotspot_jobs_data = await get_jobs(page, limit, job_type, location, vessel_size, vessel_type, department, search, db)
    all_jobs = list(yotspot_jobs_data["jobs"])
    
    # Add Facebook jobs if requested
    if source in ["all", "facebook"]:
        try:
            fb_service = FacebookJobService(db, fb_config)
            fb_jobs = fb_service.get_recent_facebook_jobs(limit=limit)
            
            # Convert Facebook jobs to match regular job format
            for fb_job in fb_jobs:
                # Apply filters
                if search and search.lower() not in (fb_job.title or "").lower():
                    continue
                if location and location.lower() not in (fb_job.location or "").lower():
                    continue
                if job_type and job_type.lower() not in (fb_job.job_type or "").lower():
                    continue
                
                # Convert to dict format
                job_dict = {
                    'id': f"fb_{fb_job.id}",
                    'title': fb_job.title,
                    'company': fb_job.company,
                    'location': fb_job.location,
                    'department': fb_job.department,
                    'job_type': fb_job.job_type,
                    'salary': fb_job.salary,
                    'description': fb_job.description,
                    'posted_at': fb_job.posted_at,
                    'source': fb_job.group_name or 'Facebook',
                    'url': fb_job.post_url,
                    'source_type': 'facebook'
                }
                all_jobs.append(job_dict)
        except Exception as e:
            # If Facebook jobs fail, continue with just Yotspot jobs
            pass
    
    # Filter by source if specified
    if source == "yotspot":
        all_jobs = [job for job in all_jobs if job.get('source_type') != 'facebook']
    elif source == "facebook":
        all_jobs = [job for job in all_jobs if job.get('source_type') == 'facebook']
    
    # Dynamic sorting based on sort parameter
    def get_sort_key(job, sort_field):
        if sort_field == "title":
            return (job.get('title') or '').lower()
        elif sort_field == "salary":
            # Extract numeric value from salary string for sorting
            salary = job.get('salary') or ''
            import re
            numbers = re.findall(r'[\d,]+', str(salary))
            if numbers:
                try:
                    return int(numbers[0].replace(',', ''))
                except:
                    return 0
            return 0
        else:  # Default to posted_at
            posted_at = job.get('posted_at')
            if posted_at is None:
                return datetime.min
            if isinstance(posted_at, str):
                try:
                    return datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                except:
                    return datetime.min
            if isinstance(posted_at, datetime):
                return posted_at
            return datetime.min
    
    # Apply sorting
    if sort:
        reverse_sort = sort in ["posted_at", "salary"]  # Date and salary sort descending by default
        all_jobs.sort(key=lambda job: get_sort_key(job, sort), reverse=reverse_sort)
    else:
        # Default sort by posted date, newest first
        all_jobs.sort(key=lambda job: get_sort_key(job, "posted_at"), reverse=True)
    
    # Limit results
    all_jobs = all_jobs[:limit]
    
    # Calculate pagination (simplified for combined results)
    total = len(all_jobs)
    pages = (total + limit - 1) // limit if total > 0 else 1
    
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
async def trigger_scrape(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger job scraping"""
    # Create scraping job record
    scraping_job = ScrapingJob(
        status="started",
        started_at=datetime.now()
    )
    db.add(scraping_job)
    db.commit()
    
    # Add background task
    background_tasks.add_task(run_scrape_task, scraping_job.id)
    
    return {"message": "Scraping started", "job_id": scraping_job.id}

async def run_scrape_task(scraping_job_id: int):
    """Background task for scraping"""
    db = next(get_db())
    try:
        scraping_job = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job_id).first()
        
        # Run scraper
        jobs_found = await scraper.scrape_jobs()
        
        # Save jobs to database
        new_jobs = 0
        for job_data in jobs_found:
            existing_job = db.query(Job).filter(Job.external_id == job_data["external_id"]).first()
            if not existing_job:
                job = Job(**job_data)
                db.add(job)
                new_jobs += 1
        
        db.commit()
        
        # Update scraping job
        scraping_job.status = "completed"
        scraping_job.completed_at = datetime.now()
        scraping_job.jobs_found = len(jobs_found)
        scraping_job.new_jobs = new_jobs
        db.commit()
        
    except Exception as e:
        # Update scraping job with error
        scraping_job = db.query(ScrapingJob).filter(ScrapingJob.id == scraping_job_id).first()
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