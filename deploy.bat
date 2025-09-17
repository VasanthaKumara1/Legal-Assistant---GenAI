@echo off
REM Legal Assistant GenAI - Windows Production Deployment Script

echo 🚀 Starting Legal Assistant GenAI Production Deployment...

REM Check if required files exist
if not exist ".env.production" (
    echo ❌ Error: .env.production file not found!
    echo Please copy .env.production.example to .env.production and configure your API keys
    pause
    exit /b 1
)

if not exist "docker-compose.production.yml" (
    echo ❌ Error: docker-compose.production.yml not found!
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "ssl" mkdir ssl

REM Build and start services
echo 🏗️ Building Docker images...
docker-compose -f docker-compose.production.yml build

echo 🚀 Starting services...
docker-compose -f docker-compose.production.yml up -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak > nul

REM Check service status
echo 🔍 Checking service status...
docker-compose -f docker-compose.production.yml ps

REM Display access information
echo.
echo ✅ Deployment completed!
echo.
echo 🔗 Access your Legal Assistant:
echo    Frontend UI: http://localhost:8501
echo    Backend API: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo.
echo 📊 To check logs:
echo    Backend: docker-compose -f docker-compose.production.yml logs backend
echo    Frontend: docker-compose -f docker-compose.production.yml logs frontend
echo.
echo 🛑 To stop services:
echo    docker-compose -f docker-compose.production.yml down
echo.
echo 🎉 Legal Assistant GenAI is now running!
echo Open http://localhost:8501 in your browser to get started.

pause