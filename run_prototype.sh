#!/bin/bash

# Legal Assistant GenAI - Simplified Startup Script

echo "🚀 Starting Legal Assistant GenAI Prototype..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install required packages if not already installed
echo "📦 Installing required packages..."
pip3 install fastapi uvicorn streamlit python-multipart pydantic requests 2>/dev/null || {
    echo "⚠️  Some packages may already be installed"
}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs

# Start backend API
echo "🔧 Starting backend API..."
cd "$(dirname "$0")"
python3 -m uvicorn app.main_clean:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Test backend connection
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend might still be starting..."
fi

# Start frontend
echo "🎨 Starting Streamlit frontend..."
python3 -m streamlit run frontend/app_clean.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "🎉 Legal Assistant GenAI is running!"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 Frontend UI: http://localhost:8501"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait