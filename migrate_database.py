#!/usr/bin/env python3
"""
Database migration script to update schema with new fields
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine, Base, DATABASE_URL
from app.models import Job, ScrapingJob

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_existing_data():
    """Backup existing job data"""
    logger.info("Backing up existing job data...")
    
    try:
        with engine.connect() as conn:
            # Check if jobs table exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"))
            if not result.fetchone():
                logger.info("No existing jobs table found, skipping backup")
                return []
            
            # Get existing jobs
            result = conn.execute(text("SELECT * FROM jobs"))
            jobs = result.fetchall()
            logger.info(f"Found {len(jobs)} existing jobs to preserve")
            return jobs
    except Exception as e:
        logger.warning(f"Could not backup data: {e}")
        return []

def migrate_database():
    """Migrate database to new schema"""
    logger.info("Starting database migration...")
    
    # Backup existing data
    existing_jobs = backup_existing_data()
    
    # Drop and recreate tables with new schema
    logger.info("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    logger.info("Creating new tables with updated schema...")
    Base.metadata.create_all(bind=engine)
    
    # Restore compatible data
    if existing_jobs:
        logger.info("Restoring existing job data with new schema...")
        restore_job_data(existing_jobs)
    
    logger.info("✅ Database migration completed successfully!")

def restore_job_data(old_jobs):
    """Restore job data with new schema"""
    from app.database import SessionLocal
    
    restored_count = 0
    
    with SessionLocal() as db:
        for old_job in old_jobs:
            try:
                # Create job with old data, setting new fields to defaults
                new_job = Job(
                    id=old_job[0] if len(old_job) > 0 else None,
                    external_id=old_job[1] if len(old_job) > 1 else None,
                    title=old_job[2] if len(old_job) > 2 else "Unknown Title",
                    company=old_job[3] if len(old_job) > 3 else None,
                    location=old_job[4] if len(old_job) > 4 else None,
                    vessel_type=old_job[5] if len(old_job) > 5 else None,
                    vessel_size=old_job[6] if len(old_job) > 6 else None,
                    vessel_name=None,  # New field
                    job_type=old_job[7] if len(old_job) > 7 else None,
                    employment_type=old_job[7] if len(old_job) > 7 else None,  # Map from job_type
                    department=old_job[8] if len(old_job) > 8 else None,
                    position_level=None,  # New field
                    salary_range=old_job[9] if len(old_job) > 9 else None,
                    salary_currency=None,  # New field
                    salary_per=old_job[10] if len(old_job) > 10 else None,
                    salary_period=old_job[10] if len(old_job) > 10 else None,  # Map from salary_per
                    start_date=old_job[11] if len(old_job) > 11 else None,
                    description=old_job[12] if len(old_job) > 12 else "",
                    posted_at=old_job[13] if len(old_job) > 13 else None,
                    posted_date=old_job[13] if len(old_job) > 13 else None,  # Map from posted_at
                    requirements=[],  # New field (JSON)
                    benefits=[],  # New field (JSON)
                    country=None,  # New field
                    region=None,  # New field
                    source_url=old_job[14] if len(old_job) > 14 else None,
                    source=old_job[15] if len(old_job) > 15 else "unknown",
                    is_featured=old_job[16] if len(old_job) > 16 else False,
                    quality_score=0.5,  # Default quality score
                    raw_data=None,  # New field (JSON)
                    scraped_at=old_job[18] if len(old_job) > 18 else None,
                    created_at=old_job[17] if len(old_job) > 17 else None,
                    updated_at=old_job[18] if len(old_job) > 18 else None
                )
                
                db.add(new_job)
                restored_count += 1
                
            except Exception as e:
                logger.warning(f"Could not restore job {old_job[0] if old_job else 'unknown'}: {e}")
                continue
        
        try:
            db.commit()
            logger.info(f"✅ Restored {restored_count} jobs with new schema")
        except Exception as e:
            logger.error(f"Error committing restored jobs: {e}")
            db.rollback()

def verify_migration():
    """Verify migration was successful"""
    logger.info("Verifying migration...")
    
    with engine.connect() as conn:
        # Check that new columns exist
        result = conn.execute(text("PRAGMA table_info(jobs)"))
        columns = [row[1] for row in result.fetchall()]
        
        required_columns = [
            'vessel_name', 'employment_type', 'position_level', 
            'salary_currency', 'salary_period', 'posted_date',
            'requirements', 'benefits', 'country', 'region',
            'quality_score', 'raw_data', 'scraped_at'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            logger.error(f"❌ Migration incomplete. Missing columns: {missing_columns}")
            return False
        else:
            logger.info("✅ All required columns present")
            
        # Check job count
        result = conn.execute(text("SELECT COUNT(*) FROM jobs"))
        job_count = result.fetchone()[0]
        logger.info(f"Database now contains {job_count} jobs")
        
        return True

if __name__ == "__main__":
    print("🔄 Database Migration for YotCrew.app")
    print("This will update the database schema to support enhanced job features")
    print("=" * 60)
    
    try:
        migrate_database()
        
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("✅ Database schema updated")
            print("✅ Existing job data preserved")
            print("✅ New features ready to use")
            print("\nYou can now start the application with: python main.py")
        else:
            print("\n❌ Migration verification failed")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

