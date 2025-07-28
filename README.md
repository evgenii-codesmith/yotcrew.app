# 🛥️ YotCrew.app

A modern, interactive yacht job platform built with **FastAPI**, **Alpine.js**, **HTMX**, **Tailwind CSS**, and **DaisyUI**. Automatically scrapes and displays yacht crew positions from top industry platforms with enhanced user interactivity.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)
![Alpine.js](https://img.shields.io/badge/Alpine.js-8BC34A?style=for-the-badge&logo=Alpine.js&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-334155?style=for-the-badge&logo=html5&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white)

## ✨ Features

### 🚀 Interactive Frontend
- **🎯 Alpine.js Integration**: Reactive components for job cards, filters, and search
- **📱 Expandable Job Cards**: Click to expand descriptions with smooth animations
- **⭐ Save/Bookmark System**: Mark favorite jobs for later review
- **☑️ Multi-select Comparison**: Select multiple jobs to compare side-by-side
- **🔍 Real-time Filtering**: Instant search and filter without page reloads
- **🏷️ Quick Filter Tags**: One-click filtering by department and vessel type
- **📊 Dynamic Sorting**: Sort by title, salary, or posting date

### 🔧 Backend Capabilities
- **🔄 Automated Scraping**: Scrapes yacht jobs from Yotspot every 45 minutes
- **⚡ HTMX-Powered**: Seamless partial page updates
- **🎨 Modern Themes**: Beautiful DaisyUI themes (currently: Cupcake)
- **🛥️ Yacht-Specific Categories**: Deck, Interior, Engineering, and Galley positions
- **📱 Mobile Responsive**: Perfect experience across all devices
- **🌈 Theme Switching**: Easy theme customization

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Conda** (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/evgenii-codesmith/yotcrew.app.git
   cd yotcrew.app
   ```

2. **Set up environment**
   ```bash
   # Using Conda (recommended)
   conda create -n yachtjobs python=3.11
   conda activate yachtjobs
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Create sample data** (optional but recommended)
   ```bash
   python create_sample_data.py
   ```

4. **Start the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   ```
   http://localhost:8000
   ```

## 📁 Project Structure

```
yotcrew.app/
├── app/
│   ├── __init__.py
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models (Job, ScrapingJob)
│   ├── scraper.py           # Yotspot scraper
│   └── scheduler.py         # Background job scheduler
├── templates/
│   ├── base.html           # Base template with Alpine.js/HTMX/Tailwind
│   ├── dashboard.html      # Simple dashboard overview
│   ├── jobs.html           # Main interactive jobs page
│   └── partials/           # HTMX partial templates
│       ├── jobs_table.html # Interactive job cards with Alpine.js
│       ├── job_card.html   # Individual job card
│       └── dashboard_stats.html
├── static/                 # Static assets
│   ├── logo.png           # YotCrew.app logo
│   ├── favicon.svg        # Site favicon
│   └── favicon.ico        # Alternative favicon
├── DesignSpecs/           # Project documentation
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── run.py                # Application runner
└── yacht_jobs.db         # SQLite database
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with async support
- **SQLAlchemy**: Database ORM with relationship management
- **SQLite**: Lightweight database (production-ready for small to medium loads)
- **APScheduler**: Background job scheduling for automated scraping
- **Beautiful Soup**: Web scraping and HTML parsing
- **Requests**: HTTP client with session management

### Frontend
- **Alpine.js**: Lightweight reactive framework for interactivity
- **HTMX**: Dynamic HTML updates without full page reloads
- **Tailwind CSS**: Utility-first CSS framework
- **DaisyUI**: Beautiful component library with theme support
- **Jinja2**: Server-side template engine

### Interactive Features (Alpine.js)
- **Job Cards**: Expandable descriptions, save/bookmark functionality
- **Multi-select**: Compare multiple jobs with floating panel
- **Real-time Filters**: Search, department, vessel type, location
- **Dynamic Sorting**: Client-side sorting with server validation
- **Quick Actions**: Copy job links, share functionality
- **Filter Status**: Visual feedback on active filters with clear options

## 🎯 Pages & Routes

### Main Routes
- **`/`** - Interactive jobs page (Alpine.js powered)
- **`/dashboard`** - Simple dashboard overview
- **`/health`** - Health check endpoint

### API Endpoints
- **`GET /api/jobs`** - Get jobs with filtering and sorting
- **`POST /api/scrape`** - Trigger manual scraping
- **`GET /api/scrape/status`** - Get scraping status

### HTMX Endpoints
- **`GET /htmx/jobs-table`** - Jobs table with interactive cards
- **`GET /htmx/dashboard-stats`** - Dashboard statistics

## 🎨 Current Theme: Cupcake

YotCrew.app uses the **Cupcake** DaisyUI theme featuring:
- Soft pastel colors (pinks and creams)
- Light, friendly background
- Professional yet approachable design
- Excellent readability and contrast

### Theme Customization
Easily change themes by modifying `templates/base.html`:
```html
<html lang="en" data-theme="cupcake">
```

Available themes: `cupcake`, `nord`, `abyss`, `coffee`, `dark`, `light`, and more.

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=sqlite:///./yacht_jobs.db

# Application
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Scraping
SCRAPER_INTERVAL_MINUTES=45
MAX_SCRAPING_PAGES=5
MIN_REQUEST_DELAY=2.0
MAX_REQUEST_DELAY=5.0
```

## 🔍 Job Categories & Filtering

### Department Categories
- **⚓ Deck**: Captain, First Mate, Bosun, Deckhand, Navigation
- **🏠 Interior**: Chief Stewardess, Stewardess, Butler, Housekeeping
- **🔧 Engineering**: Chief Engineer, Engineer, ETO, Mechanical
- **👨‍🍳 Galley**: Head Chef, Sous Chef, Cook, Galley Assistant

### Vessel Types
- Motor Yacht
- Sailing Yacht
- Explorer Yacht
- Catamaran
- Superyacht
- Expedition Vessel

### Advanced Filtering
- **Real-time Search**: Instant results as you type
- **Location Filtering**: By region, country, or city
- **Salary Range**: Filter by compensation levels
- **Job Type**: Permanent, Temporary, Rotational
- **Experience Level**: Entry, Junior, Senior, Executive

## 🎮 Interactive Features

### Alpine.js Components

#### Job Cards (`jobFilters` component)
```javascript
// Real-time filtering and search
x-data="jobFilters()"
x-model="filters.search"
@change="applyFilters()"
```

#### Expandable Content
```javascript
// Expandable job descriptions
x-data="{ expanded: false }"
x-show="expanded"
x-transition
```

#### Save/Bookmark System
```javascript
// Job bookmarking
x-data="{ saved: false }"
@click="toggleSave(jobId)"
```

#### Multi-select Comparison
```javascript
// Compare multiple jobs
x-model="selectedJobs"
x-show="selectedJobs.length > 0"
```

## 🔄 Scraping Details

### Source
- **Primary**: [Yotspot.com](https://www.yotspot.com/job-search.html)
- **Categories**: All yacht crew positions
- **Update Frequency**: Every 45 minutes
- **Data Extracted**: Title, company, location, salary, description, vessel type

### Ethical Scraping
- ✅ **Rate Limited**: 2-5 second delays between requests
- ✅ **Respectful**: Maximum 5 pages per session
- ✅ **User-Agent**: Proper browser identification
- ✅ **Public Data**: Only publicly available job listings
- ✅ **Error Handling**: Graceful failure management

## 🐳 Docker Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  yotcrew:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - HOST=0.0.0.0
    volumes:
      - ./yacht_jobs.db:/app/yacht_jobs.db
```

### Build and Run
```bash
docker build -t yotcrew-app .
docker run -p 8000:8000 yotcrew-app
```

## 🧪 Testing & Development

### Test Scraper
```bash
python test_scraper.py
```

### Create Sample Data
```bash
python create_sample_data.py
```

### Development Mode
```bash
# With auto-reload
python run.py
# OR
uvicorn main:app --reload
```

## 🚀 Production Deployment

### Render.com (Recommended)
The project includes `render.yaml` for easy deployment to Render:

1. Connect your GitHub repository
2. Render will automatically detect the configuration
3. Environment variables are pre-configured
4. Automatic deployments on git push

### Manual Production Setup
1. Set `DEBUG=False`
2. Configure production database (PostgreSQL recommended)
3. Set up proper secrets management
4. Configure reverse proxy (nginx)
5. Enable HTTPS

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **[Yotspot](https://www.yotspot.com)** - Primary source for yacht job listings
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Alpine.js](https://alpinejs.dev/)** - Lightweight reactive framework
- **[HTMX](https://htmx.org/)** - Modern web interactions
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first styling
- **[DaisyUI](https://daisyui.com/)** - Beautiful component library

---

**Made with ❤️ for yacht crew professionals worldwide** 🛥️

**Repository**: [https://github.com/evgenii-codesmith/yotcrew.app](https://github.com/evgenii-codesmith/yotcrew.app) 