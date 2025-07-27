# YotCrew.app - Simple Implementation Plan

## Core Philosophy: Start Simple, Stay Extensible

### 1. Database Setup (SQLite + SQLAlchemy)
- Single SQLite file: `yacht_jobs.db`
- SQLAlchemy ORM for easy PostgreSQL migration later
- No migration scripts needed initially

### 2. Simple Classification System
- Keyword-based classification (regex/simple matching)
- Easy to extend with NLTK later
- Pluggable architecture for new categories

### 3. Scraping Architecture
- Modular scraper classes
- Easy to add new Facebook groups
- Simple configuration-based approach

### 4. Tech Stack (Minimal)
- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: HTMX + Tailwind CSS
- **Database**: SQLite
- **Scraping**: requests + BeautifulSoup

## Implementation Phases

### Phase 1: Core Database (Day 1)
```python
# app/models.py - Simple models
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///yacht_jobs.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(Text)
    category = Column(String, index=True)
    company = Column(String)
    location = Column(String)
    salary = Column(String)
    source = Column(String, index=True)
    url = Column(String)
    posted_date = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### Phase 2: Simple Classifier (Day 2)
```python
# app/classifier.py - Keyword-based
CATEGORY_KEYWORDS = {
    "chef": ["chef", "cook", "culinary", "galley"],
    "stewardess": ["stewardess", "stew", "interior", "service"],
    "engineer": ["engineer", "engineering", "mechanical"],
    "deckhand": ["deckhand", "deck", "bosun", "exterior"],
    "captain": ["captain", "master", "skipper"]
}

def classify_job(title, description):
    text = f"{title} {description}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "other"
```

### Phase 3: Pluggable Scrapers (Day 3-4)
```python
# app/scrapers/base.py
class BaseScraper:
    def __init__(self, source_name):
        self.source_name = source_name
    
    def scrape(self):
        raise NotImplementedError
    
    def parse_job(self, raw_data):
        raise NotImplementedError

# app/scrapers/yotspot.py
class YotspotScraper(BaseScraper):
    def __init__(self):
        super().__init__("yotspot")
    
    def scrape(self):
        # Yotspot-specific scraping
        pass

# app/scrapers/facebook.py
class FacebookScraper(BaseScraper):
    def __init__(self, group_url):
        super().__init__(f"facebook_{group_url.split('/')[-1]}")
        self.group_url = group_url
    
    def scrape(self):
        # Facebook group scraping
        pass
```

### Phase 4: FastAPI Backend (Day 5)
```python
# main.py - Simple FastAPI
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.models import Job, Base
from app.database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/jobs")
def get_jobs(category: str = None, db: Session = Depends(get_db)):
    query = db.query(Job)
    if category:
        query = query.filter(Job.category == category)
    return query.all()
```

### Phase 5: Simple Frontend (Day 6)
```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>YotCrew - Yacht Jobs</title>
    <script src="https://unpkg.com/htmx.org"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mx-auto p-4">
        <h1 class="text-3xl font-bold mb-4">YotCrew Jobs</h1>
        
        <select hx-get="/api/jobs" hx-target="#jobs">
            <option value="">All Categories</option>
            <option value="chef">Chef</option>
            <option value="stewardess">Stewardess</option>
            <option value="engineer">Engineer</option>
        </select>
        
        <div id="jobs" hx-get="/api/jobs" hx-trigger="load">
            <!-- Jobs loaded here -->
        </div>
    </div>
</body>
</html>
```

## Extensibility Points

### 1. Adding New Facebook Groups
```python
# config/groups.py
FACEBOOK_GROUPS = [
    "https://facebook.com/groups/yachtcrewjobs",
    "https://facebook.com/groups/yachtjobs",
    # Add new groups here
]

# Usage
for group_url in FACEBOOK_GROUPS:
    scraper = FacebookScraper(group_url)
    jobs = scraper.scrape()
```

### 2. Adding New Categories
```python
# Just extend CATEGORY_KEYWORDS
CATEGORY_KEYWORDS["first_officer"] = ["first officer", "chief officer", "mate"]
```

### 3. Adding New Sources
```python
# Create new scraper class
class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__("new_source")
    
    def scrape(self):
        # Implementation
        pass
```

## File Structure
```
yotcrew/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── classifier.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── yotspot.py
│   │   ├── daywork123.py
│   │   └── facebook.py
│   └── database.py
├── templates/
│   └── index.html
├── static/
├── main.py
├── requirements.txt
└── yacht_jobs.db
```

## Next Steps
1. Set up basic database models
2. Implement first scraper (Yotspot)
3. Add simple classification
4. Create basic FastAPI endpoints
5. Build simple frontend
6. Add Facebook group scraping (when you provide URLs)

This plan keeps everything simple but extensible. Each component can be enhanced later without breaking existing functionality.