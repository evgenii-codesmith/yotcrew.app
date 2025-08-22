# Frontend Database Integration

This document describes the implementation of frontend integration with the database for displaying scraped yacht jobs in the YotCrew.app project.

## Overview

The frontend has been enhanced to display jobs from the SQLite database with full support for:
- Multiple job sources (Yotspot, Daywork123, etc.)
- Advanced filtering and search
- Enhanced job cards with quality scores, requirements, and benefits
- Real-time job statistics
- Source-specific filtering

## Changes Made

### 1. Enhanced API Endpoints (`main.py`)

#### Updated `/api/jobs` endpoint:
- ✅ Added `source` parameter for filtering by job source
- ✅ Enhanced filtering to support new database fields
- ✅ Improved search to include company names
- ✅ Better ordering by multiple date fields

#### New `/api/jobs/stats` endpoint:
- ✅ Returns job statistics by source
- ✅ Shows recent activity (last 7 days)
- ✅ HTMX-compatible template rendering
- ✅ JSON API support for programmatic access

#### Enhanced `/htmx/jobs-table` endpoint:
- ✅ Integrated with enhanced `/api/jobs` endpoint
- ✅ Removed Facebook integration complexity
- ✅ Added client-side sorting options
- ✅ Support for quality score sorting

### 2. Enhanced Job Card Templates (`templates/partials/jobs_table.html`)

#### Visual Enhancements:
- ✅ **Source badges** with color coding
- ✅ **Quality score indicators** (★0.8+ green, ★0.6+ yellow, <0.6 red)
- ✅ **Enhanced job metadata** (employment type, department, vessel type)
- ✅ **Vessel information** display (size, name)
- ✅ **Currency and salary period** support

#### Expandable Content:
- ✅ **Requirements** list (expandable, shows first 3)
- ✅ **Benefits** list (expandable, shows first 3)
- ✅ **Enhanced timestamps** (posted date + scraped date)

#### Interactive Features:
- ✅ **External source links** to original job postings
- ✅ **Source-specific styling** for different job sources
- ✅ **Enhanced apply buttons** with external links

### 3. Enhanced Main Template (`templates/jobs.html`)

#### New Filter Options:
- ✅ **Source filter dropdown** in header
- ✅ **Source filter select** in main filters
- ✅ **Real-time job statistics** display
- ✅ **Enhanced quick actions** with source breakdown

#### JavaScript Enhancements:
- ✅ Added `source` field to filters object
- ✅ Updated `applyFilters()` to include source parameter
- ✅ Updated `clearAllFilters()` to reset source filter

### 4. Job Statistics Template (`templates/partials/job_stats.html`)

#### Features:
- ✅ **Total job count** display
- ✅ **Source breakdown** with colored badges
- ✅ **Recent activity** indicator
- ✅ **HTMX auto-refresh** every 30 seconds

## Database Schema Compatibility

The frontend now fully supports all enhanced database fields:

### Core Fields:
- ✅ `external_id`, `title`, `company`, `description`
- ✅ `location`, `country`, `region`
- ✅ `source`, `source_url`

### Enhanced Fields:
- ✅ `vessel_type`, `vessel_size`, `vessel_name`
- ✅ `employment_type`, `job_type`, `department`, `position_level`
- ✅ `salary_range`, `salary_currency`, `salary_period`
- ✅ `requirements` (JSON), `benefits` (JSON)
- ✅ `quality_score`, `raw_data` (JSON)
- ✅ `posted_date`, `scraped_at`, `created_at`, `updated_at`

## Frontend Features

### 1. Source Filtering

```javascript
// Filter by specific source
filters.source = 'daywork123';
applyFilters();

// Show all sources
filters.source = 'all';
applyFilters();
```

### 2. Enhanced Job Cards

Each job card now displays:
- **Source badge** (color-coded by source)
- **Quality score** (star rating with color coding)
- **Employment type and department** badges
- **Vessel information** (type, size, name)
- **Salary with currency** and payment period
- **Requirements and benefits** (expandable lists)
- **Posted and scraped dates**
- **Direct links** to original job postings

### 3. Real-time Statistics

The header displays:
- **Total job count**
- **Source breakdown** (Yotspot: X, Daywork123: Y)
- **Recent activity** (jobs added this week)
- **Auto-refreshing** every 30 seconds

### 4. Advanced Search

Enhanced search functionality:
- **Job titles** and **descriptions**
- **Company names**
- **Multiple location fields** (location, country, region)
- **Employment types** (permanent, temporary, rotational, etc.)

## Testing

### 1. Run the Test Script

```bash
cd /home/swordfish/Downloads/ProjectYachtJobs
python test_frontend_db.py
```

This script will:
- ✅ Set up the database
- ✅ Check existing job content
- ✅ Add sample jobs if database is empty
- ✅ Test API endpoints
- ✅ Provide testing instructions

### 2. Start the Application

```bash
# Activate the yachtjobs conda environment
conda activate yachtjobs

# Start the FastAPI server
python main.py
```

### 3. Test Frontend Features

Open your browser to `http://localhost:8000` and test:

#### Source Filtering:
- ✅ Use the "📊 Sources" dropdown in the header
- ✅ Use the "Source" select in the main filters
- ✅ Verify jobs filter correctly by source

#### Enhanced Job Cards:
- ✅ Check source badges are color-coded
- ✅ Look for quality score stars
- ✅ Expand job cards to see requirements/benefits
- ✅ Click external links to verify they work

#### Real-time Statistics:
- ✅ Check the header shows current job counts
- ✅ Verify source breakdown is accurate
- ✅ Wait 30 seconds to see auto-refresh

#### Search and Filtering:
- ✅ Test search by job title, company, description
- ✅ Filter by employment type, department, vessel type
- ✅ Combine multiple filters
- ✅ Test the "Clear All Filters" functionality

## API Endpoints

### GET `/api/jobs`
Enhanced job retrieval with filtering:
```
GET /api/jobs?source=daywork123&job_type=permanent&location=monaco&page=1&limit=20
```

### GET `/api/jobs/stats`
Job statistics by source:
```
GET /api/jobs/stats
```
Returns:
```json
{
  "total": 150,
  "sources": {
    "yotspot": 80,
    "daywork123": 70
  },
  "recent_week": 25,
  "available_sources": ["yotspot", "daywork123"]
}
```

### GET `/htmx/jobs-table`
HTMX-compatible job table with enhanced filtering:
```
GET /htmx/jobs-table?source=all&search=captain&job_type=permanent
```

## Performance Considerations

### Database Queries:
- ✅ **Indexed fields** for fast filtering (external_id, source)
- ✅ **Optimized ordering** with null handling
- ✅ **Pagination** to limit result sets

### Frontend Performance:
- ✅ **HTMX partial updates** for fast filtering
- ✅ **Auto-refreshing statistics** without full page reload
- ✅ **Debounced search** to prevent excessive API calls
- ✅ **Expandable content** to reduce initial load

### Caching:
- ✅ **Template caching** for repeated renders
- ✅ **Database connection pooling**
- ✅ **Static asset caching**

## Troubleshooting

### Common Issues:

1. **No jobs displayed**
   - Run `python test_frontend_db.py` to add sample data
   - Check database has jobs: `python -c "from app.database import SessionLocal; from app.models import Job; print(SessionLocal().query(Job).count())"`

2. **Source filter not working**
   - Check browser console for JavaScript errors
   - Verify `/api/jobs` endpoint includes source parameter

3. **Statistics not loading**
   - Check `/api/jobs/stats` endpoint in browser
   - Verify HTMX is loading properly

4. **Quality scores not showing**
   - Ensure jobs have been scraped with new enhanced scraper
   - Check `quality_score` field in database

### Debug Mode:

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check specific endpoints:
```bash
curl "http://localhost:8000/api/jobs?source=daywork123&limit=5"
curl "http://localhost:8000/api/jobs/stats"
```

## Future Enhancements

### Planned Features:

1. **Advanced Filtering**
   - Salary range sliders
   - Date range pickers
   - Location-based mapping

2. **Job Comparison**
   - Side-by-side job comparison
   - Saved job collections
   - Job alerts and notifications

3. **Analytics Dashboard**
   - Job market trends
   - Salary analytics
   - Source performance metrics

4. **User Features**
   - User accounts and profiles
   - Job application tracking
   - Personalized recommendations

## Contributing

When contributing to the frontend integration:

1. **Follow existing patterns** in templates and API design
2. **Test thoroughly** with multiple job sources
3. **Update documentation** as needed
4. **Maintain performance** considerations
5. **Handle errors gracefully** with proper user feedback

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Compatible With**: YotCrew.app v1.0+  
**Frontend**: HTMX + Alpine.js + DaisyUI + Tailwind CSS

