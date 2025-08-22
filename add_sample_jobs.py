#!/usr/bin/env python3
"""
Add sample jobs to the database for demonstration
"""
import sys
import os
import asyncio
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal
from app.models import Job

def add_sample_jobs():
    """Add sample jobs to database"""
    print("Adding sample jobs to database...")
    
    sample_jobs = [
        {
            'external_id': 'sample_001',
            'title': 'Captain - 50m Motor Yacht',
            'company': 'Elite Yacht Management',
            'location': 'Monaco',
            'country': 'Monaco',
            'vessel_type': 'motor_yacht',
            'vessel_size': '50-74m',
            'vessel_name': 'M/Y Excellence',
            'employment_type': 'permanent',
            'job_type': 'permanent',
            'department': 'deck',
            'position_level': 'senior',
            'salary_range': '€8,000 - €12,000/month',
            'salary_currency': 'EUR',
            'salary_period': 'month',
            'description': 'Experienced Captain sought for 50m+ motor yacht. Must have extensive Mediterranean experience and excellent leadership skills.',
            'requirements': ['Valid MCA certificates', '5+ years captain experience', 'Mediterranean knowledge', 'Leadership skills'],
            'benefits': ['Competitive salary', 'Health insurance', 'Travel opportunities', 'Professional development'],
            'source': 'daywork123',
            'source_url': 'https://www.daywork123.com/sample/001',
            'quality_score': 0.95,
            'raw_data': {'sample': True, 'source': 'demo'},
            'posted_date': datetime.utcnow(),
            'scraped_at': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'external_id': 'sample_002',
            'title': 'Chief Engineer - Superyacht',
            'company': 'Prestige Yachts',
            'location': 'Fort Lauderdale',
            'country': 'United States',
            'region': 'Florida',
            'vessel_type': 'super_yacht',
            'vessel_size': '75m+',
            'vessel_name': 'S/Y Innovation',
            'employment_type': 'rotational',
            'job_type': 'rotational',
            'department': 'engineering',
            'position_level': 'chief',
            'salary_range': '$9,000 - $13,000/month',
            'salary_currency': 'USD',
            'salary_period': 'month',
            'description': 'Chief Engineer required for 80m superyacht. Rotational position with excellent package.',
            'requirements': ['Engineering degree', 'Marine engineering experience', 'Leadership skills', 'Y4 Engineering certification'],
            'benefits': ['Rotation schedule', 'Excellent package', 'Career development', 'Travel allowance'],
            'source': 'daywork123',
            'source_url': 'https://www.daywork123.com/sample/002',
            'quality_score': 0.88,
            'raw_data': {'sample': True, 'source': 'demo'},
            'posted_date': datetime.utcnow(),
            'scraped_at': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'external_id': 'sample_003',
            'title': 'Interior Manager - Private Yacht',
            'company': 'Ocean Luxury',
            'location': 'Antibes',
            'country': 'France',
            'region': 'French Riviera',
            'vessel_type': 'motor_yacht',
            'vessel_size': '40-49m',
            'vessel_name': 'M/Y Serenity',
            'employment_type': 'permanent',
            'job_type': 'permanent',
            'department': 'interior',
            'position_level': 'manager',
            'salary_range': '€4,500 - €6,500/month',
            'salary_currency': 'EUR',
            'salary_period': 'month',
            'description': 'Interior Manager for high-end private yacht. Attention to detail essential.',
            'requirements': ['Interior management experience', 'Attention to detail', 'Guest service focus', 'STCW certification'],
            'benefits': ['Beautiful locations', 'Professional development', 'Competitive salary', 'Tips'],
            'source': 'yotspot',
            'source_url': 'https://www.yotspot.com/sample/003',
            'quality_score': 0.82,
            'raw_data': {'sample': True, 'source': 'demo'},
            'posted_date': datetime.utcnow(),
            'scraped_at': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    
    with SessionLocal() as db:
        for job_data in sample_jobs:
            job = Job(**job_data)
            db.add(job)
        
        db.commit()
        print(f"✅ Added {len(sample_jobs)} sample jobs to database")
        
        # Verify
        total_jobs = db.query(Job).count()
        print(f"Database now contains {total_jobs} jobs")

if __name__ == "__main__":
    add_sample_jobs()

