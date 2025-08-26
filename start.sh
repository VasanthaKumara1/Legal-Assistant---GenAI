#!/bin/bash

# AI Legal Assistant Startup Script

echo "🏗️  Starting AI Legal Assistant..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please update .env file with your OpenAI API key and other settings"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs data

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start backend API
echo "🚀 Starting backend API..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend
echo "🎨 Starting Streamlit frontend..."
cd ../frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo "✅ AI Legal Assistant is running!"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 Frontend UI: http://localhost:8501"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait