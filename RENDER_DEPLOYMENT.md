# Deploying Yacht Jobs Monitor to Render

This guide explains how to deploy the Yacht Jobs Monitor application to Render hosting platform.

## 🚀 **Deployment Options**

### **Option 1: Blueprint Deployment (Recommended)**
Deploy all services at once using the `render.yaml` blueprint.

### **Option 2: Manual Service Creation**
Create each service individually through Render dashboard.

### **Option 3: Docker Deployment**
Deploy using Docker containers (limited support on Render).

## **Option 1: Blueprint Deployment**

### **Step 1: Prepare Your Repository**
1. Push your code to GitHub/GitLab
2. Ensure `render.yaml` is in the root directory
3. Commit all changes

### **Step 2: Create Render Account**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub/GitLab
3. Connect your repository

### **Step 3: Deploy Blueprint**
1. In Render dashboard, click "New +"
2. Select "Blueprint"
3. Connect your repository
4. Render will detect `render.yaml` automatically
5. Click "Apply"

### **Step 4: Configure Environment Variables**
After deployment, set these environment variables in the backend service:

```env
FB_ACCESS_TOKEN=your_facebook_access_token
FB_GROUP_ID=your_facebook_group_id
FB_APP_SECRET=your_facebook_app_secret
FB_VERIFY_TOKEN=your_custom_verify_token
```

### **Step 5: Update Facebook Webhook**
Update your Facebook app webhook URL to:
```
https://yacht-jobs-backend.onrender.com/facebook/webhook
```

## **Option 2: Manual Service Creation**

### **Backend Service**
1. **Create Web Service**
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - Start Command: `python main.py`

2. **Environment Variables**
   ```env
   DATABASE_URL=sqlite:///./yacht_jobs.db
   FB_ACCESS_TOKEN=your_token
   FB_GROUP_ID=your_group_id
   FB_APP_SECRET=your_secret
   FB_VERIFY_TOKEN=your_verify_token
   CORS_ORIGINS=https://your-frontend-url.onrender.com
   ```

### **Frontend Service**
1. **Create Web Service**
   - Runtime: Node.js
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`

2. **Environment Variables**
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   NEXT_PUBLIC_WS_URL=wss://your-backend-url.onrender.com
   ```

### **Redis Service**
1. **Create Redis Service**
   - Plan: Starter (Free tier available)
   - Copy the connection string for backend configuration

## **Option 3: Docker Deployment**

⚠️ **Note**: Render has limited Docker support. Use native runtimes when possible.

### **Backend Docker Service**
1. **Create Web Service**
   - Runtime: Docker
   - Dockerfile path: `./Dockerfile`
   - Build context: `.`

2. **Environment Variables**
   ```env
   DATABASE_URL=sqlite:///./yacht_jobs.db
   FB_ACCESS_TOKEN=your_token
   FB_GROUP_ID=your_group_id
   FB_APP_SECRET=your_secret
   FB_VERIFY_TOKEN=your_verify_token
   ```

### **Frontend Docker Service**
1. **Create Web Service**
   - Runtime: Docker
   - Dockerfile path: `./frontend/Dockerfile`
   - Build context: `./frontend`

## **Important Considerations**

### **1. Free Tier Limitations**
- **Sleep Mode**: Free services sleep after 15 minutes of inactivity
- **Build Time**: Limited to 500 build minutes/month
- **Bandwidth**: 100GB/month
- **Storage**: Ephemeral (files don't persist between deploys)

### **2. Database Persistence**
SQLite files are ephemeral on Render. For production:

```python
# Use PostgreSQL instead
DATABASE_URL=postgresql://user:password@host:port/database
```

### **3. WebSocket Support**
Render supports WebSockets, but with limitations:
- Free tier has connection limits
- May timeout during inactivity

### **4. Facebook Webhook Requirements**
- Must use HTTPS (Render provides this)
- Webhook URL must be publicly accessible
- Must respond to verification requests

## **Production Optimizations**

### **1. Use PostgreSQL**
```python
# In main.py, update database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./yacht_jobs.db")

# Add PostgreSQL dependency
pip install psycopg2-binary
```

### **2. Environment-Specific Configuration**
```python
# In main.py
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
```

### **3. Persistent Storage**
For file uploads or persistent data:
```python
# Use external storage (AWS S3, Cloudinary, etc.)
import cloudinary
```

## **Monitoring & Debugging**

### **1. View Logs**
```bash
# In Render dashboard
Services > Your Service > Logs
```

### **2. Health Checks**
Both services have health check endpoints:
- Backend: `https://your-backend.onrender.com/health`
- Frontend: `https://your-frontend.onrender.com/`

### **3. Performance Monitoring**
```python
# Add performance monitoring
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

## **Cost Estimation**

### **Free Tier**
- Backend: Free (with sleep mode)
- Frontend: Free (with sleep mode)
- Redis: Free starter plan
- **Total**: $0/month

### **Paid Tier**
- Backend: $7/month (no sleep mode)
- Frontend: $7/month (no sleep mode)
- Redis: $7/month (persistent)
- **Total**: $21/month

## **Deployment Checklist**

- [ ] Repository connected to Render
- [ ] `render.yaml` configured
- [ ] Environment variables set
- [ ] Facebook webhook URL updated
- [ ] Services deployed successfully
- [ ] Health checks passing
- [ ] WebSocket connection working
- [ ] Job detection functioning
- [ ] Notifications working

## **Troubleshooting**

### **Common Issues**

1. **Build Failures**
   ```bash
   # Check Python version
   python --version
   
   # Ensure all dependencies in requirements.txt
   pip freeze > requirements.txt
   ```

2. **spaCy Model Download Fails**
   ```bash
   # Add to build command
   python -m spacy download en_core_web_sm --quiet
   ```

3. **WebSocket Connection Issues**
   ```javascript
   // Use wss:// for HTTPS sites
   const ws = new WebSocket('wss://your-backend.onrender.com/ws/all');
   ```

4. **CORS Errors**
   ```python
   # Update CORS origins
   CORS_ORIGINS=https://your-frontend.onrender.com
   ```

5. **Database Connection Issues**
   ```python
   # For PostgreSQL
   pip install psycopg2-binary
   ```

## **Next Steps**

1. **Custom Domain**: Add custom domain in Render dashboard
2. **SSL Certificate**: Automatic with custom domains
3. **Monitoring**: Set up error tracking and performance monitoring
4. **Scaling**: Upgrade to paid plans for better performance
5. **CI/CD**: Set up automatic deployments on code changes

## **Support**

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [GitHub Issues](https://github.com/your-repo/issues)

Your Yacht Jobs Monitor will be live at:
- **Frontend**: `https://yacht-jobs-frontend.onrender.com`
- **Backend**: `https://yacht-jobs-backend.onrender.com`
- **API Docs**: `https://yacht-jobs-backend.onrender.com/docs` 