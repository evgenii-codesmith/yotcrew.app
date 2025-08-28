# Real-Time Job Detection Integration

## Overview
Integrate real-time job detection into existing scraping architecture using MutationObserver with Playwright, leveraging current project structure and components.

## Existing Components to Reuse
- `app/scrapers/daywork123.py` - Daywork123Scraper with Playwright integration
- `app/scrapers/base.py` - BaseScraper and UniversalJob model
- `app/scrapers/registry.py` - Scraper registry system
- `app/services/scheduler_service.py` - Background service framework
- Database models and SessionLocal for job storage
- Notification service (referenced in existing code)

## Implementation Steps

### Step 1: Extend Daywork123Scraper
- Add real-time monitoring capability to existing `Daywork123Scraper` class
- Create new method `start_real_time_monitoring()` that uses existing Playwright setup
- Reuse existing `_extract_job_from_element()` method for job data extraction
- Leverage existing `_normalize_job()` and `save_jobs_to_db()` methods

### Step 2: Implement MutationObserver Integration
- Create JavaScript MutationObserver code to monitor job table element
- Target existing selector: `#ContentPlaceHolder1_RepJobAnnouncement`
- Configure observer to watch for childList, subtree, and characterData changes
- Expose callback function to Python using `page.expose_function()`
- Reuse existing job detection logic from `_extract_job_from_element()`

### Step 3: Real-Time Detection Logic
- Implement job comparison using existing UniversalJob model
- Reuse existing database query pattern to check for duplicate jobs
- Leverage existing quality scoring logic from `_calculate_quality_score()`
- Use existing notification service for immediate alerts

### Step 4: Background Service Integration
- Create new `RealTimeMonitorService` class similar to `SchedulerService`
- Reuse existing service start/stop pattern and signal handling
- Integrate with existing logging configuration
- Add simple health check using existing patterns

### Step 5: Database Integration
- Reuse existing Job model and SessionLocal pattern
- Add flag to distinguish between scraped and real-time detected jobs
- Leverage existing duplicate detection logic
- Use existing transaction management for job storage

### Step 6: Notification Enhancement
- Extend existing notification service to support real-time alerts
- Implement email notification functionality triggered when changes are detected
- Add priority levels for real-time vs periodic notifications
- Reuse existing notification log model for tracking
- Support multiple channels using existing notification infrastructure
- Create email notification templates for job alerts
- Implement error handling for email delivery failures

### Step 7: Configuration Management
- Add real-time monitoring settings to existing config structure
- Reuse existing environment variable pattern
- Add email configuration to .env file:
  - `NOTIFICATION_EMAIL`: Email address to receive notifications
  - `SMTP_SERVER`: SMTP server for sending emails
  - `SMTP_PORT`: Port for SMTP server
  - `SMTP_USERNAME`: Username for SMTP authentication
  - `SMTP_PASSWORD`: Password for SMTP authentication
- Add real-time specific settings (observer sensitivity, notification priority)
- Integrate with existing scheduler configuration

### Step 8: Render Deployment
- Create new background worker service in render.yaml
- Reuse existing database connection configuration
- Share environment variables with existing services
- Add real-time specific environment variables including email configuration
- Ensure .env file with email settings is properly deployed

### Step 9: Service Coordination
- Implement coordination between real-time and periodic scrapers
- Add simple mutex mechanism to prevent conflicts
- Reuse existing scraper registry for coordination
- Add basic status reporting to existing monitoring system

### Step 10: Testing and Validation
- Test real-time detection alongside existing periodic scraping
- Verify no duplicate jobs are created
- Test email notification delivery when changes are detected
- Validate email notifications contain correct job information
- Validate database integrity with mixed scraping methods

## Integration Points

### With Existing Daywork123Scraper
- Extend existing class rather than creating new one
- Share browser context and page management
- Reuse existing job extraction and normalization
- Maintain existing error handling patterns

### With Scheduler Service
- Add real-time service to existing service registry
- Use similar startup/shutdown procedures
- Share health check infrastructure
- Integrate with existing logging system

### With Database Layer
- Use existing Job model without modification
- Leverage existing session management
- Reuse existing query patterns
- Maintain existing transaction handling

### With Notification System
- Extend existing notification service to include email notifications
- Implement email sending functionality using SMTP
- Use existing notification templates as basis for email templates
- Share notification log model for tracking email deliveries
- Maintain existing error handling for email-specific failures

## Email Notification Implementation

### Email Configuration
- Store recipient email address in .env file as `NOTIFICATION_EMAIL`
- Configure SMTP settings in .env file:
  - `SMTP_SERVER`: SMTP server address
  - `SMTP_PORT`: SMTP server port
  - `SMTP_USERNAME`: SMTP authentication username
  - `SMTP_PASSWORD`: SMTP authentication password
- Load email configuration at service startup

### Email Content
- Format email subject to indicate real-time job detection
- Include job details in email body (title, company, location, description)
- Add direct link to job posting
- Include timestamp of detection
- Format for readability on both desktop and mobile

### Email Delivery
- Send email immediately when new job is detected
- Implement retry logic for failed email deliveries
- Log email delivery status in notification log
- Handle email delivery errors gracefully

## Deployment Considerations

### Resource Management
- Monitor browser memory usage in real-time mode
- Implement graceful restart using existing patterns
- Add basic real-time specific metrics
- Consider single instance resource limits

### Error Handling
- Reuse existing error logging framework
- Add real-time specific error codes
- Implement fallback to periodic scraping if real-time fails
- Use existing alert system for critical failures
- Add specific error handling for email delivery failures

### Performance Optimization
- Optimize MutationObserver for specific job table changes
- Reuse existing browser session management
- Implement efficient job comparison algorithms
- Consider single browser instance for monitoring
- Optimize email sending to not block detection process

## Maintenance Considerations

### Monitoring
- Add real-time specific metrics to existing dashboard
- Create alerts for real-time service failures
- Monitor detection latency and accuracy
- Track notification delivery times
- Monitor email delivery success rate

### Updates
- Update real-time logic when website structure changes
- Maintain compatibility with existing scrapers
- Regularly update Playwright browser version
- Test real-time detection after any scraper updates
- Update email templates as needed

### Coordination
- Ensure real-time and periodic scrapers don't interfere
- Use existing database constraints to prevent duplicates
- Maintain consistent job data format
- Keep notification channels synchronized
- Ensure email notifications are sent only for new, unique job postings
