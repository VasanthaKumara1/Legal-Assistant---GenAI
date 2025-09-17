# Legal Assistant GenAI - Deployment Guide

## 🚀 Quick Deploy (3 Steps)

### Step 1: Configure Environment
```bash
# Copy the production environment template
cp .env.production .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_api_key_here
```

### Step 2: Deploy
```bash
# On Linux/Mac
chmod +x deploy.sh
./deploy.sh

# On Windows
deploy.bat
```

### Step 3: Access
- **Web Interface**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

## 🌟 Available Features

### 1. Document Upload & Analysis 📄
- Upload PDF, DOCX, TXT files (max 10MB)
- OCR support for scanned documents
- Automatic text extraction and preprocessing

### 2. Legal Text Simplification 🔄
- Convert legal jargon to plain English
- 4 complexity levels: Elementary, High School, College, Expert
- Key points extraction and red flag identification

### 3. Legal Terms Lookup 📚
- Instant explanation of legal terms
- Context-aware definitions
- Pre-built legal dictionary with 500+ terms

### 4. Risk Assessment ⚠️
- AI-powered contract risk analysis
- Liability assessment
- Compliance checking
- Risk scoring with detailed explanations

## 🔧 Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here  # REQUIRED
MAX_FILE_SIZE=10485760                   # 10MB limit
ALLOWED_FILE_TYPES=[".pdf",".docx",".txt",".png",".jpg"]
```

### Optional Settings
```bash
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/legal_assistant.db
ENVIRONMENT=production
```

## 🐳 Docker Commands

### Start Services
```bash
docker-compose -f docker-compose.production.yml up -d
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs backend
docker-compose -f docker-compose.production.yml logs frontend
```

### Stop Services
```bash
docker-compose -f docker-compose.production.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.production.yml restart
```

## 🌐 Public Deployment Options

### Option 1: Railway
1. Connect your GitHub repository
2. Set environment variable: `OPENAI_API_KEY`
3. Deploy automatically

### Option 2: Heroku
```bash
# Install Heroku CLI and login
heroku create your-legal-assistant
heroku config:set OPENAI_API_KEY=your_key_here
git push heroku main
```

### Option 3: DigitalOcean App Platform
1. Import from GitHub
2. Configure environment variables
3. Select basic plan ($5/month)

### Option 4: AWS/GCP
- Use the provided Docker containers
- Configure load balancing for high availability
- Set up SSL certificates for HTTPS

## 📊 Monitoring

### Health Checks
- Backend: http://localhost:8000/health
- Frontend: http://localhost:8501/_stcore/health

### Performance
- Monitor response times in logs
- Track OpenAI API usage
- Watch Docker container resources

## 🛡️ Security Notes

1. **Never commit API keys** to version control
2. Use strong SECRET_KEY in production
3. Configure proper CORS origins
4. Enable SSL/HTTPS for production
5. Regularly update dependencies

## 🔧 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker is running
docker --version

# Check ports are available
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501
```

**OpenAI API errors:**
- Verify API key is correct
- Check account has sufficient credits
- Ensure internet connectivity

**File upload issues:**
- Check file size < 10MB
- Verify file type is supported
- Ensure upload directory permissions

### Getting Help
- Check logs: `docker-compose logs`
- Verify environment variables
- Test API endpoints individually
- Review OpenAI API documentation

## 📈 Scaling for Production

### Load Balancing
```yaml
# Add to docker-compose.production.yml
backend:
  deploy:
    replicas: 3
```

### Database Upgrade
```bash
# Switch to PostgreSQL for production
DATABASE_URL=postgresql://user:pass@localhost:5432/legal_db
```

### Redis Caching
```bash
# Add Redis for session management
REDIS_URL=redis://localhost:6379
```