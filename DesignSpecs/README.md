# 🛥️ Yacht Jobs Dashboard

A modern, real-time yacht job monitoring dashboard built with **FastAPI**, **HTMX**, **Tailwind CSS**, and **DaisyUI**. Automatically scrapes and displays yacht crew positions from top industry platforms.

![Yacht Jobs Dashboard](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-334155?style=for-the-badge&logo=html5&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white)

## ✨ Features

- **🔄 Real-time Job Scraping**: Automatically scrapes yacht jobs from Yotspot every 45 minutes
- **⚡ HTMX-Powered UI**: Smooth, interactive interface without JavaScript frameworks
- **🎨 Modern Design**: Beautiful responsive design with Tailwind CSS and DaisyUI
- **🔍 Advanced Filtering**: Search by job type, location, vessel size, department, and more
- **📊 Dashboard Analytics**: Real-time statistics and job market insights
- **🛥️ Yacht-Specific Categories**: Deck, Interior, Engineering, and Galley positions
- **📱 Mobile Responsive**: Works perfectly on all devices
- **🌙 Theme Support**: Multiple themes including light/dark modes

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ProjectYachtJobs
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create sample data** (optional but recommended for testing)
   ```bash
   python create_sample_data.py
   ```

4. **Start the application**
   ```bash
   python run.py
   # OR
   uvicorn main:app --reload
   ```

5. **Open your browser**
   ```
   http://localhost:8000
   ```

## 📁 Project Structure

```
ProjectYachtJobs/
├── app/
│   ├── __init__.py
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── scraper.py           # Yotspot scraper
│   └── scheduler.py         # Background job scheduler
├── templates/
│   ├── base.html           # Base template with HTMX/Tailwind
│   ├── dashboard.html      # Main dashboard
│   ├── jobs.html           # Jobs listing page
│   └── partials/           # HTMX partial templates
│       ├── jobs_table.html
│       ├── job_card.html
│       └── dashboard_stats.html
├── static/                 # Static files (CSS, JS)
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── create_sample_data.py   # Sample data script
├── test_scraper.py        # Scraper testing
└── run.py                 # Application runner
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Default database (easily configurable)
- **APScheduler**: Background job scheduling
- **Beautiful Soup**: Web scraping
- **Requests**: HTTP client

### Frontend
- **HTMX**: Dynamic HTML without JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **DaisyUI**: Tailwind CSS component library
- **Jinja2**: Template engine

### Features
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: HTMX-powered live updates
- **Rate-Limited Scraping**: Respectful scraping with delays
- **Background Processing**: Scheduled scraping jobs

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

### Scraping Configuration

The application is configured to scrape respectfully:
- **45-minute intervals** between scraping runs
- **2-5 second delays** between requests
- **Maximum 5 pages** per scraping session
- **User-agent rotation** to appear more human-like

## 📊 API Endpoints

### Web Pages
- `GET /` - Dashboard
- `GET /jobs` - Jobs listing
- `GET /health` - Health check

### API Endpoints
- `GET /api/jobs` - Get jobs with filtering
- `GET /api/jobs/{job_id}` - Get specific job
- `POST /api/scrape` - Trigger manual scraping
- `GET /api/scrape/status` - Get scraping status

### HTMX Endpoints
- `GET /htmx/jobs-table` - Jobs table partial
- `GET /htmx/job-card/{job_id}` - Job detail modal
- `GET /htmx/dashboard-stats` - Dashboard statistics

## 🔍 Job Categories

The dashboard organizes jobs by yacht industry categories:

- **⚓ Deck**: Captain, First Mate, Bosun, Deckhand
- **🏠 Interior**: Chief Stewardess, Stewardess, Butler
- **🔧 Engineering**: Chief Engineer, Engineer, ETO
- **👨‍🍳 Galley**: Head Chef, Sous Chef, Cook

## 🐳 Docker Deployment

### Build and run with Docker

```bash
# Build the image
docker build -t yacht-jobs .

# Run the container
docker run -p 8000:8000 yacht-jobs
```

### Docker Compose (with Redis)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## 🧪 Testing

### Test the scraper
```bash
python test_scraper.py
```

### Create sample data
```bash
python create_sample_data.py
```

### Run health check
```bash
curl http://localhost:8000/health
```

## 🔄 Scraping Details

The scraper targets [Yotspot.com](https://www.yotspot.com/job-search.html) and extracts:

- Job titles and descriptions
- Company names
- Vessel types and sizes
- Locations and start dates
- Salary information
- Job types (Permanent, Temporary, Rotational)
- Department categories

### Scraping Ethics
- ✅ Respectful rate limiting (2-5s delays)
- ✅ User-agent headers
- ✅ No excessive requests
- ✅ Public data only
- ✅ Proper error handling

## 🎨 UI Features

### Dashboard
- Real-time job statistics
- Quick action buttons
- Recent jobs preview
- Job category navigation
- Market insights

### Jobs Page
- Advanced filtering system
- Real-time search (HTMX)
- Pagination support
- Detailed job cards
- Modal job details

### Design Elements
- Modern yacht-themed design
- Responsive grid layouts
- Interactive components
- Smooth animations
- Theme switching support

## 🚀 Production Deployment

### Environment Setup
1. Set `DEBUG=False`
2. Configure production database
3. Set proper `SECRET_KEY`
4. Configure Redis for caching
5. Set up reverse proxy (nginx)

### Security Considerations
- Use environment variables for secrets
- Enable HTTPS in production
- Configure CORS properly
- Set up rate limiting
- Monitor scraping activities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Yotspot](https://www.yotspot.com) for yacht job listings
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework
- [HTMX](https://htmx.org/) for modern web interactions
- [Tailwind CSS](https://tailwindcss.com/) for utility-first styling
- [DaisyUI](https://daisyui.com/) for beautiful components

---

Made with ❤️ for the yacht industry professionals worldwide 🛥️ 