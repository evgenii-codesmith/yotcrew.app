ss# YotCrew.app - Comprehensive Technical Requirements Specification

## Executive Summary

**YotCrew.app** is a sophisticated yacht job aggregation platform that automatically scrapes and presents yacht crew positions from multiple sources including Yotspot.com, Daywork123.com, and MeridianGo.com. The platform features a modern, responsive web interface built with FastAPI, HTMX, Alpine.js, Tailwind CSS, and DaisyUI, providing real-time job discovery, interactive filtering, and advanced job comparison capabilities for yacht industry professionals.

## 1. System Architecture Overview

### 1.1 Technology Stack
- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL (primary), Redis (caching)
- **Frontend**: HTMX + Alpine.js for interactivity
- **Styling**: Tailwind CSS + DaisyUI component library
- **Task Queue**: Celery with Redis broker
- **Web Scraping**: Playwright + BeautifulSoup4
- **API Documentation**: OpenAPI/Swagger
- **Deployment**: Docker containers on Render/Fly.io

### 1.2 System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Browser] --> B[HTMX/Alpine.js]
        B --> C[Tailwind CSS/DaisyUI]
    end
    
    subgraph "API Layer"
        D[FastAPI] --> E[Authentication]
        D --> F[Rate Limiting]
        D --> G[Validation]
    end
    
    subgraph "Business Logic"
        
        H --> J[Yotspot Scraper]
        H --> K[Daywork123 Scraper]
        H --> L[MeridianGo Scraper]
        M[Job Processor] --> N[Duplicate Detection]
        M --> O[Category Classification]
        M --> P[Salary Extraction]
    end
    
    subgraph "Data Layer"
        Q[PostgreSQL] --> R[Jobs Table]
        Q --> S[Companies Table]
        Q --> T[Users Table]
        U[Redis] --> V[Cache]
        U --> W[Task Queue]
    end
    
    subgraph "External Services"
        
        Y[Yotspot.com]
        Z[Daywork123.com]
        AA[MeridianGo.com]
    end
```

## 2. Core Functional Requirements

### 2.1 Job Scraping & Aggregation

#### 2.1.1 Source Configuration
 
  - Support for private yacht crew groups
  - OAuth2 authentication flow
  - Rate limiting: 1 request per 3 seconds
  - Post filtering by keywords and date range
  
- **Yotspot.com**:
  - Public job listings scraping
  - Pagination support (up to 50 pages)
  - Job detail page extraction
  - Company profile enrichment
  
- **Daywork123.com**:
  - Daily job postings scraping
  - Location-based filtering
  - Position type categorization
  - Contact information extraction
  
- **MeridianGo.com**:
  - Real-time job updates
  - Vessel specifications extraction
  - Contract type identification
  - Salary range parsing

#### 2.1.2 Scraping Schedule

- **Hourly**: Daywork123.com updates
- **Daily**: Full Yotspot.com refresh
- **Weekly**: MeridianGo.com comprehensive scan

### 2.2 Job Classification System

#### 2.2.1 Primary Categories
1. **Chef**
   - Head Chef
   - Sous Chef
   - Crew Chef
   - Private Chef

2. **Stewardess**
   - Chief Stewardess
   - Second Stewardess
   - Junior Stewardess
   - Service Stewardess

3. **Engineer**
   - Chief Engineer
   - Second Engineer
   - Third Engineer
   - Junior Engineer

4. **ETO (Electro-Technical Officer)**
   - Senior ETO
   - Junior ETO
   - AV/IT Officer

5. **Captain**
   - Master
   - Relief Captain
   - Captain/Engineer

6. **Deckhand**
   - Bosun
   - Lead Deckhand
   - Senior Deckhand
   - Junior Deckhand

#### 2.2.2 Classification Algorithm
- **Keyword matching**: 85% accuracy threshold
- **ML-based classification**: BERT model for job descriptions
- **Manual override**: Admin panel for corrections
- **Confidence scoring**: Display reliability indicators

### 2.3 Job Card Component Specification

#### 2.3.1 Visual Design
- **Dimensions**: 350px x 280px (desktop), full-width (mobile)
- **Layout**: Card-based with glassmorphism effects
- **Colors**: Category-specific accent colors
- **Typography**: Inter font family with proper hierarchy

#### 2.3.2 Interactive Features
- **Hover effects**: Subtle elevation and shadow
- **Quick actions**: Save, share, apply buttons
- **Expandable details**: Full description on click
- **Source attribution**: Platform-specific styling
- **Real-time updates**: Live status indicators

## 3. Technical Requirements

### 3.1 Backend API Specification

#### 3.1.1 RESTful Endpoints

```yaml
GET /api/v1/jobs:
  parameters:
    - category: string (chef|stewardess|engineer|eto|captain|deckhand)
    - source: string (yotspot|daywork123|meridiango)
    - location: string
    - salary_min: integer
    - salary_max: integer
    - contract_type: string (permanent|temporary|rotational)
    - start_date_from: date
    - start_date_to: date
    - page: integer (default: 1)
    - limit: integer (default: 20)
  responses:
    200:
      schema:
        jobs: array[Job]
        pagination: PaginationInfo
        filters: ActiveFilters

GET /api/v1/jobs/{job_id}:
  responses:
    200:
      schema: JobDetail
    404:
      description: Job not found

GET /api/v1/categories:
  responses:
    200:
      schema:
        categories: array[Category]
        counts: object (category -> count)

GET /api/v1/scraping/status:
  responses:
    200:
      schema:
        sources: array[SourceStatus]
        last_update: datetime
        next_update: datetime
```

#### 3.1.2 WebSocket Events
```yaml
events:
  job_created:
    payload: Job
  job_updated:
    payload: Job
  scraping_started:
    payload: { source: string }
  scraping_completed:
    payload: { source: string, count: integer }
  connection_status:
    payload: { status: string, timestamp: datetime }
```

### 3.2 Database Schema

#### 3.2.1 Core Tables

```sql
-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100),
    company_name VARCHAR(255),
    company_logo_url TEXT,
    location VARCHAR(255),
    vessel_name VARCHAR(255),
    vessel_type VARCHAR(100),
    vessel_size INTEGER,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3),
    contract_type VARCHAR(50),
    start_date DATE,
    posted_date TIMESTAMP,
    application_url TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    scraped_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    icon VARCHAR(50),
    color VARCHAR(7),
    sort_order INTEGER
);

-- Sources table
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    base_url TEXT,
    is_active BOOLEAN DEFAULT true,
    last_scraped TIMESTAMP,
    scrape_interval_minutes INTEGER
);

-- Saved jobs table
CREATE TABLE saved_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES jobs(id),
    saved_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, job_id)
);
```

### 3.3 Frontend Specifications

#### 3.3.1 HTMX Integration
```html
<!-- Job listing with HTMX -->
<div id="jobs-container" 
     hx-get="/htmx/jobs"
     hx-trigger="load, every 30s"
     hx-target="#jobs-container"
     hx-swap="innerHTML">
</div>

<!-- Filter form -->
<form hx-get="/htmx/jobs" 
      hx-target="#jobs-container"
      hx-push-url="true"
      hx-indicator="#loading">
  <select name="category" hx-get="/htmx/jobs" hx-target="#jobs-container">
    <option value="">All Categories</option>
    <option value="chef">Chef</option>
    <option value="stewardess">Stewardess</option>
    <option value="engineer">Engineer</option>
    <option value="eto">ETO</option>
    <option value="captain">Captain</option>
    <option value="deckhand">Deckhand</option>
  </select>
</form>
```

#### 3.3.2 Alpine.js Components
```javascript
// Job card component
<div x-data="jobCard({
    job: jobData,
    isSaved: false,
    isExpanded: false
})">
  <div @click="toggleExpand" 
       :class="{ 'shadow-lg': isExpanded }"
       class="job-card transition-all duration-300">
    <!-- Card content -->
  </div>
</div>
```

### 3.4 Responsive Design Specifications

#### 3.4.1 Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px - 1440px
- **Large Desktop**: 1440px+

#### 3.4.2 Grid System
```css
/* Mobile: 1 column */
.job-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
  .job-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) {
  .job-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Large Desktop: 4 columns */
@media (min-width: 1440px) {
  .job-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

## 4. Performance Requirements

### 4.1 Response Times
- **Initial page load**: < 2 seconds
- **Job search/filter**: < 500ms
- **Real-time updates**: < 1 second
- **Image loading**: Lazy loading with blur-up effect

### 4.2 Caching Strategy
- **Redis caching**: Job listings (5-minute TTL)
- **CDN integration**: Static assets and images
- **Database query caching**: Complex aggregations
- **Browser caching**: Static resources (1-year TTL)

### 4.3 Scalability Targets
- **Concurrent users**: 1,000+
- **Jobs per day**: 10,000+
- **Scraping frequency**: Every 15 minutes
- **Database size**: 1M+ jobs capacity

## 5. Security Requirements

### 5.1 Authentication & Authorization
- **JWT tokens**: Stateless authentication

- **Rate limiting**: 100 requests per minute per IP
- **API key management**: For third-party integrations

### 5.2 Data Protection
- **HTTPS enforcement**: All endpoints
- **Input validation**: SQL injection prevention
- **XSS protection**: Content sanitization
- **CORS configuration**: Whitelist domains

### 5.3 Scraping Ethics
- **Robots.txt compliance**: Respect site policies
- **Rate limiting**: Maximum 1 request per 2 seconds
- **User-agent identification**: Clear bot identification
- **Data retention**: 90-day automatic cleanup

## 6. Monitoring & Analytics

### 6.1 Application Monitoring
- **Error tracking**: Sentry integration
- **Performance monitoring**: APM metrics
- **Uptime monitoring**: 99.9% SLA
- **Log aggregation**: Structured logging

### 6.2 Business Analytics
- **Job posting trends**: Category-wise analytics
- **User engagement**: Click-through rates
- **Source performance**: Scraping success rates
- **Geographic insights**: Location-based analytics

## 7. Deployment & Infrastructure

### 7.1 Container Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Environment Configuration
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/yotcrew
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=yotcrew
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7-alpine
```

## 8. Testing Strategy

### 8.1 Test Coverage Requirements
- **Unit tests**: 80% minimum coverage
- **Integration tests**: API endpoints
- **E2E tests**: Critical user flows
- **Performance tests**: Load testing

## 9. Success Metrics

### 9.1 Key Performance Indicators
- **Daily active users**: 500+ within 3 months
- **Job discovery rate**: 100+ new jobs daily
- **User engagement**: 5+ page views per session
- **Search success rate**: 70% click-through
- **System uptime**: 99.9% availability

---

This comprehensive specification provides the foundation for building YotCrew.app as a world-class yacht job aggregation platform.