#!/usr/bin/env python3
"""
Sample data creation script for YotCrew.app
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import Job, ScrapingJob

# Create tables
Base.metadata.create_all(bind=engine)

# Sample job data
SAMPLE_JOBS = [
    {
        "external_id": "yot_001",
        "title": "Captain",
        "company": "Elite Yacht Management",
        "location": "Mediterranean",
        "vessel_type": "Motor Yacht",
        "vessel_size": "65m (213ft)",
        "job_type": "Permanent",
        "department": "Deck",
        "salary_range": "€8,500",
        "salary_per": "month",
        "start_date": "Starting 15th Mar 2025",
        "description": "Experienced Captain required for a 65m private/charter motor yacht. The ideal candidate will have extensive experience on similar sized vessels, strong leadership skills, and commercial yacht qualifications. Excellent salary and benefits package offered.",
        "source_url": "https://www.yotspot.com/job-detail/001",
        "posted_at": datetime.now() - timedelta(days=1)
    },
    {
        "external_id": "yot_002", 
        "title": "Chief Stewardess",
        "company": "Superyacht Solutions",
        "location": "French Riviera",
        "vessel_type": "Motor Yacht",
        "vessel_size": "80m (262ft)",
        "job_type": "Rotational",
        "department": "Interior",
        "salary_range": "$6,000",
        "salary_per": "month",
        "start_date": "Starting 20th Mar 2025",
        "description": "Chief Stewardess position available for an 80m motor yacht. Seeking an experienced professional with excellent guest service skills, strong team leadership abilities, and attention to detail. Rotational schedule 2:2.",
        "source_url": "https://www.yotspot.com/job-detail/002",
        "posted_at": datetime.now() - timedelta(hours=12)
    },
    {
        "external_id": "yot_003",
        "title": "Chief Engineer", 
        "company": "Ocean Elite Crew",
        "location": "Caribbean",
        "vessel_type": "Motor Yacht",
        "vessel_size": "90m (295ft)",
        "job_type": "Permanent",
        "department": "Engineering",
        "salary_range": "$9,200",
        "salary_per": "month",
        "start_date": "Starting 1st Apr 2025",
        "description": "Chief Engineer required for a 90m superyacht operating in the Caribbean. Must have extensive experience with large yacht systems, strong technical background, and relevant certifications. Competitive salary and benefits.",
        "source_url": "https://www.yotspot.com/job-detail/003", 
        "posted_at": datetime.now() - timedelta(hours=6)
    },
    {
        "external_id": "yot_004",
        "title": "Deckhand",
        "company": "Riviera Yachting",
        "location": "Italy",
        "vessel_type": "Sailing Yacht",
        "vessel_size": "45m (148ft)",
        "job_type": "Seasonal",
        "department": "Deck",
        "salary_range": "€3,200",
        "salary_per": "month",
        "start_date": "Starting 10th Apr 2025",
        "description": "Deckhand position for a beautiful 45m sailing yacht for the Mediterranean season. Perfect opportunity for someone looking to gain experience in the yachting industry. Good seamanship skills required.",
        "source_url": "https://www.yotspot.com/job-detail/004",
        "posted_at": datetime.now() - timedelta(hours=3)
    },
    {
        "external_id": "yot_005",
        "title": "Sous Chef",
        "company": "Mediterranean Yacht Services", 
        "location": "Monaco",
        "vessel_type": "Motor Yacht",
        "vessel_size": "55m (180ft)",
        "job_type": "Permanent",
        "department": "Galley",
        "salary_range": "$5,500",
        "salary_per": "month",
        "start_date": "Starting 25th Mar 2025",
        "description": "Sous Chef position on a busy 55m motor yacht. Looking for a creative and experienced chef to support the Head Chef in delivering exceptional cuisine to demanding guests. High standards expected.",
        "source_url": "https://www.yotspot.com/job-detail/005",
        "posted_at": datetime.now() - timedelta(minutes=45)
    },
    {
        "external_id": "yot_006",
        "title": "2nd Stewardess",
        "company": "Azure Yacht Crew",
        "location": "Spain", 
        "vessel_type": "Motor Yacht",
        "vessel_size": "70m (230ft)",
        "job_type": "Temporary",
        "department": "Interior",
        "salary_range": "€4,200",
        "salary_per": "month",
        "start_date": "Starting 5th Apr 2025",
        "description": "2nd Stewardess required for a 70m motor yacht for a 3-month charter season. Excellent guest service skills essential, along with housekeeping and table service experience.",
        "source_url": "https://www.yotspot.com/job-detail/006",
        "posted_at": datetime.now() - timedelta(minutes=30)
    },
    {
        "external_id": "yot_007",
        "title": "First Mate",
        "company": "Premier Yacht Crew",
        "location": "Greece",
        "vessel_type": "Motor Yacht", 
        "vessel_size": "50m (164ft)",
        "job_type": "Permanent",
        "department": "Deck",
        "salary_range": "$6,800",
        "salary_per": "month",
        "start_date": "Starting 18th Mar 2025",
        "description": "First Mate position available on a well-maintained 50m motor yacht. Strong navigation, seamanship, and leadership skills required. OOW 3000GT minimum qualification needed.",
        "source_url": "https://www.yotspot.com/job-detail/007",
        "posted_at": datetime.now() - timedelta(minutes=15)
    },
    {
        "external_id": "yot_008",
        "title": "ETO (Electro Technical Officer)",
        "company": "Superyacht Technical Solutions",
        "location": "United States",
        "vessel_type": "Motor Yacht",
        "vessel_size": "100m (328ft)",
        "job_type": "Rotational",
        "department": "Engineering",
        "salary_range": "$8,000", 
        "salary_per": "month",
        "start_date": "Starting 2nd Apr 2025",
        "description": "ETO position on a state-of-the-art 100m superyacht. Responsible for all electrical and electronic systems. Advanced technical qualifications and experience with complex yacht systems required.",
        "source_url": "https://www.yotspot.com/job-detail/008",
        "posted_at": datetime.now()
    }
]

def create_sample_data():
    """Create sample job and scraping data"""
    db = SessionLocal()
    
    try:
        print("Creating sample job data...")
        
        # Add sample jobs
        for job_data in SAMPLE_JOBS:
            existing_job = db.query(Job).filter(Job.external_id == job_data["external_id"]).first()
            if not existing_job:
                job = Job(**job_data)
                db.add(job)
                print(f"Added job: {job_data['title']} at {job_data['company']}")
        
        # Add a sample scraping job
        scraping_job = ScrapingJob(
            status="completed",
            started_at=datetime.now() - timedelta(minutes=30),
            completed_at=datetime.now() - timedelta(minutes=25),
            jobs_found=len(SAMPLE_JOBS),
            new_jobs=len(SAMPLE_JOBS),
            scraper_type="yotspot_sample"
        )
        db.add(scraping_job)
        
        db.commit()
        print(f"\n✅ Successfully created {len(SAMPLE_JOBS)} sample jobs!")
        print("🚀 Your YotCrew.app is ready!")
        print("\nTo start the application:")
        print("  uvicorn main:app --reload")
        print("\nThen visit: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data() 