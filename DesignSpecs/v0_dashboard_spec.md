# Vercel v0 Component Specifications

## **1. Main Dashboard Layout**

**v0 Prompt:**
```
Create a modern real-time social media monitoring dashboard with dark theme. Include:
- Top navigation bar with logo "FB Monitor" and connection status indicator
- Sidebar with navigation: Dashboard, Job Posts, All Posts, Analytics, Settings
- Main content area with grid layout for widgets
- Real-time status badge (online/offline)
- Notification bell icon with badge count
- User avatar dropdown in top right
- Use glassmorphism effects and subtle animations
- Modern typography with proper spacing
- Responsive design for mobile/desktop
```

**Key Features:**
- Sidebar navigation with active states
- Real-time connection status indicator
- Notification center
- Responsive grid layout
- Dark/light theme toggle
- Glassmorphism UI elements

---

## **2. Live Post Feed Component**

**v0 Prompt:**
```
Design a live social media post feed component with:
- Post cards with gradient borders
- Author avatar, name, and timestamp
- Post content with expandable text (show more/less)
- Job post badge with special styling (gradient, pulse animation)
- Engagement metrics (likes, comments, shares)
- Real-time "NEW" indicator for fresh posts
- Smooth fade-in animations for new posts
- Loading skeleton states
- Infinite scroll capability
- Post type indicators (job/regular)
- Action buttons: View on Facebook, Save, Share
```

**Key Features:**
- Animated post cards
- Job post highlighting
- Real-time indicators
- Skeleton loading states
- Expandable content
- Social engagement metrics

---

## **3. Job Post Alert Component**

**v0 Prompt:**
```
Create an urgent job post alert component with:
- Prominent alert card with red/orange gradient background
- Pulsing animation border
- "🚨 NEW JOB POST" header with icon
- Job title extraction and highlighting
- Company name if detected
- Salary range if mentioned
- Location (remote/on-site) badges
- "Apply Now" CTA button
- Dismiss/Save for later actions
- Slide-in animation from right
- Auto-dismiss after 10 seconds option
- Sound notification toggle
```

**Key Features:**
- Urgent visual treatment
- Pulsing animations
- Job detail extraction
- CTA buttons
- Auto-dismiss functionality
- Slide animations

---

## **4. Statistics Dashboard Widget**

**v0 Prompt:**
```
Build a comprehensive statistics dashboard with:
- 4 main metric cards: Total Posts, Job Posts, Today's Posts, Active Connections
- Each card with icon, large number, and percentage change
- Mini line charts showing trends
- Color-coded positive/negative changes
- Real-time updating counters with smooth number transitions
- Hover effects with subtle shadows
- Responsive grid layout
- Loading states for each metric
- Time range selector (24h, 7d, 30d)
- Export data button
```

**Key Features:**
- Animated counters
- Trend indicators
- Mini charts
- Time range filtering
- Hover effects
- Real-time updates

---

## **5. Search & Filter Interface**

**v0 Prompt:**
```
Design a powerful search and filter interface featuring:
- Search bar with autocomplete and recent searches
- Filter chips for: Job Posts, Date Range, Author, Post Type
- Sort options: Newest, Oldest, Most Relevant
- Advanced filters panel (collapsible)
- Real-time search results with highlighting
- Search history with clear all option
- Saved searches functionality
- Quick filter buttons for common searches
- Search suggestions based on keywords
- Clear all filters button
```

**Key Features:**
- Advanced search functionality
- Filter chips and tags
- Autocomplete suggestions
- Search history
- Real-time filtering
- Collapsible panels

---

## **6. Real-time Activity Feed**

**v0 Prompt:**
```
Create a real-time activity feed sidebar showing:
- Live stream of activities with timestamps
- Different icons for: New Post, Job Post, Comment, Like
- Activity items with fade-in animations
- Grouping similar activities (e.g., "3 new posts in last 5 minutes")
- Clickable activities to jump to related content
- Activity type color coding
- Compact list view with avatars
- Auto-scroll to latest activity
- Pause/resume feed option
- Activity density indicator
```

**Key Features:**
- Real-time activity stream
- Activity grouping
- Color-coded events
- Auto-scrolling
- Pause/resume controls
- Density indicators

---

## **7. Connection Status Component**

**v0 Prompt:**
```
Build a connection status indicator showing:
- WebSocket connection status with colored dot (green/red/yellow)
- Connection quality indicator (excellent/good/poor)
- Last update timestamp
- Reconnection attempts counter
- Manual reconnect button
- Connection history (connected/disconnected events)
- Ping/latency display
- Network quality visualization
- Offline mode indicator
- Connection troubleshooting tips
```

**Key Features:**
- Real-time status updates
- Connection quality metrics
- Manual reconnection
- Troubleshooting guidance
- Network visualization
- Offline handling

---

## **8. Settings & Configuration Panel**

**v0 Prompt:**
```
Design a settings configuration panel with:
- Notification preferences (sound, desktop, email)
- Job keywords management (add/remove/edit)
- Alert thresholds and filters
- Theme selection (dark/light/auto)
- Language preferences
- Data export options
- Privacy settings
- Account management
- Integration settings (Facebook, webhooks)
- Performance preferences
- Backup and restore options
```

**Key Features:**
- Tabbed interface
- Toggle switches
- Keyword management
- Theme selection
- Data export
- Account settings

---

## **9. Mobile-First Responsive Design**

**v0 Prompt:**
```
Create mobile-optimized versions of all components with:
- Collapsible sidebar that slides over content
- Bottom navigation for mobile
- Swipe gestures for post interactions
- Pull-to-refresh functionality
- Thumb-friendly button sizes
- Optimized touch targets
- Mobile-specific animations
- Reduced motion for battery saving
- Offline indicator and caching
- Mobile notification integration
```

**Key Features:**
- Mobile-first approach
- Touch-friendly interactions
- Swipe gestures
- Pull-to-refresh
- Offline support
- Battery optimization

---

## **10. Loading & Error States**

**v0 Prompt:**
```
Design comprehensive loading and error states:
- Skeleton loading for post cards
- Shimmer effects for data loading
- Progress bars for long operations
- Error boundaries with retry options
- Empty states with helpful illustrations
- Network error messages
- Timeout handling
- Graceful degradation
- Loading state variations
- Success/error toast notifications
```

**Key Features:**
- Skeleton screens
- Shimmer effects
- Error boundaries
- Empty state illustrations
- Toast notifications
- Retry mechanisms

---

## **11. Job Scraping & Aggregation Components**

**v0 Prompt:**
```
Create a job scraping management dashboard with:
- Job source toggle switches (Indeed, LinkedIn, AngelList, Remote.co, etc.)
- Active scraping status indicators with progress bars
- Scraped job cards with source badges and comparison features
- Duplicate job detection and merging interface
- Job matching confidence scores and similarity indicators
- Source reliability ratings and success rates
- Scraping schedule configuration (hourly, daily, custom)
- Job alert rules and keyword management
- Scraped job analytics and trends
- Manual scraping trigger buttons
- Failed scrape retry options
- Data freshness indicators
```

**Key Features:**
- Multi-source job aggregation
- Duplicate detection interface
- Scraping status monitoring
- Job matching algorithms
- Source management
- Analytics dashboard

---

## **12. Job Comparison & Matching Interface**

**v0 Prompt:**
```
Design a job comparison interface featuring:
- Side-by-side job comparison cards
- Similarity score visualization with progress rings
- Highlighted matching keywords and requirements
- Salary comparison charts and ranges
- Company comparison with ratings and reviews
- Location preference matching
- Skills requirement overlap visualization
- Experience level compatibility indicators
- Job application tracking across sources
- Bookmark and save functionality
- Export comparison reports
- Smart recommendation engine results
```

**Key Features:**
- Job comparison matrix
- Similarity scoring
- Salary comparisons
- Skills matching
- Company insights
- Application tracking

---

## **13. Multi-Source Job Feed**

**v0 Prompt:**
```
Create a unified job feed combining multiple sources:
- Unified job cards with source badges (Facebook, Indeed, LinkedIn, etc.)
- Advanced filtering by source, salary, location, date posted
- Job source credibility indicators
- Duplicate job grouping with "Show similar" expandable sections
- Source-specific styling and branding
- Job freshness indicators (new, updated, stale)
- Quick apply buttons with source-specific actions
- Job saving across all sources
- Source performance metrics
- Feed customization preferences
- Bulk actions for multiple jobs
```

**Key Features:**
- Multi-source aggregation
- Duplicate handling
- Source credibility
- Unified interface
- Bulk operations
- Performance tracking

---

## **14. Scraping Configuration Panel**

**v0 Prompt:**
```
Build a comprehensive scraping configuration interface:
- Job site toggle switches with logos (Indeed, LinkedIn, AngelList, etc.)
- Scraping frequency sliders and schedule pickers
- Keyword and location input fields with autocomplete
- Scraping rate limiting and delay settings
- Proxy configuration and rotation options
- Success rate monitoring and alerts
- Error handling and retry logic settings
- Data quality thresholds and validation rules
- Scraping budget and cost tracking
- Performance optimization settings
- Backup and failover configurations
```

**Key Features:**
- Source configuration
- Schedule management
- Rate limiting controls
- Proxy settings
- Performance monitoring
- Cost tracking

---

## **Component Integration Guidelines**

### **State Management Requirements:**
```javascript
// Global state structure for components
{
  posts: [],
  jobPosts: [],
  connectionStatus: 'connected',
  notifications: [],
  filters: {},
  settings: {},
  realTimeEnabled: true
}
```

### **WebSocket Event Handlers:**
```javascript
// Events to handle in components
- 'new_post': Update post feed
- 'new_job_post': Show job alert
- 'connection_status': Update status indicator
- 'statistics_update': Refresh metrics
- 'error': Show error notification
```

### **Animation Libraries:**
- **Framer Motion** for complex animations
- **Tailwind CSS** for utility-based styling
- **Lucide React** for consistent icons
- **React Hot Toast** for notifications

### **Performance Considerations:**
- Virtual scrolling for large post lists
- Lazy loading for images and media
- Debounced search inputs
- Memoized expensive computations
- Efficient WebSocket message handling

### **Accessibility Features:**
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode
- Focus indicators
- ARIA labels and roles
- Reduced motion preferences