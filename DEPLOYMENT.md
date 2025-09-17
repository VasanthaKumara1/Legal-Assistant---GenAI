# Legal Assistant GenAI - Heroku Deployment Guide

## Quick Deploy to Heroku

### Method 1: One-Click Deploy (Backend Only)
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Method 2: Manual Heroku CLI Deploy

```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create legal-assistant-genai

# Set environment variables
heroku config:set DEBUG=false
heroku config:set LOG_LEVEL=INFO

# Deploy
git push heroku main

# Open app
heroku open
```

### Method 3: Streamlit Cloud (Frontend Only)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set main file to: `frontend/app_clean.py`
6. Update API_BASE_URL in the code to your Heroku backend URL

## Environment Variables for Production

```bash
# Heroku Config
heroku config:set APP_NAME="Legal Assistant GenAI"
heroku config:set DEBUG=false
heroku config:set LOG_LEVEL=INFO
heroku config:set CORS_ORIGINS="https://your-frontend-url.streamlitapp.com"
```

## Architecture for Production

```
Frontend (Streamlit Cloud) <--> Backend (Heroku)
```

- **Frontend**: Streamlit app hosted on Streamlit Cloud
- **Backend**: FastAPI app hosted on Heroku
- **CORS**: Configured to allow frontend domain

## URLs After Deployment

- **Backend API**: `https://your-app-name.herokuapp.com`
- **Frontend UI**: `https://your-username-legal-assistant.streamlitapp.com`
- **API Docs**: `https://your-app-name.herokuapp.com/docs`

## Files for Deployment

- `Procfile` - Heroku process configuration
- `runtime.txt` - Python version specification  
- `requirements.prototype.txt` - Simplified dependencies
- `app/main_clean.py` - Main backend application
- `frontend/app_clean.py` - Frontend application