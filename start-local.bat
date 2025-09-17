@echo off
REM Legal Assistant GenAI - Local Python Deployment (No Docker Required)

echo 🚀 Starting Legal Assistant GenAI Local Deployment...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 Copying .env.example to .env...
        copy ".env.example" ".env"
        echo ⚠️  Please edit .env file and add your OpenAI API key
        echo Then run this script again
        pause
        exit /b 1
    ) else (
        echo ❌ Error: No .env file found and no .env.example to copy from
        pause
        exit /b 1
    )
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Start backend in background
echo 🚀 Starting FastAPI backend...
start "Legal Assistant Backend" cmd /k "cd /d %CD% && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a bit for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

REM Start frontend
echo 🎨 Starting Streamlit frontend...
start "Legal Assistant Frontend" cmd /k "cd /d %CD% && streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"

echo.
echo ✅ Legal Assistant GenAI is starting!
echo.
echo 🔗 Access your application:
echo    Frontend UI: http://localhost:8501
echo    Backend API: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo.
echo 📝 Note: Two command windows will open for backend and frontend
echo 🛑 To stop: Close both command windows
echo.
echo 🎉 Visit http://localhost:8501 to start using the Legal Assistant!

pause