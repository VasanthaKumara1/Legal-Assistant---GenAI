#!/bin/bash

# Legal Assistant GenAI - Simple Deployment Script
echo "🚀 Starting Legal Assistant GenAI..."

# Create necessary directories
mkdir -p uploads logs

# Install dependencies
echo "📦 Installing dependencies..."
pip install fastapi uvicorn python-multipart openai python-dotenv aiofiles streamlit requests

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# AI Legal Assistant Environment Configuration
APP_NAME=Legal Document Demystification AI
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000
MAX_FILE_SIZE=10485760
UPLOAD_DIRECTORY=uploads
CORS_ORIGINS=["*"]
LOG_LEVEL=INFO

# Optional: Add your OpenAI API key for enhanced features
# OPENAI_API_KEY=your_openai_api_key_here
EOF
fi

# Start backend in background
echo "🔧 Starting backend API..."
cd "$(dirname "$0")"
uvicorn app.main_clean:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Test backend
echo "🧪 Testing backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
streamlit run frontend_clean.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "🎉 Legal Assistant GenAI is now running!"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 Frontend UI: http://localhost:8501"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "✨ Features available:"
echo "  • Document upload and processing"
echo "  • Text simplification"
echo "  • Health monitoring"
echo "  • Interactive web interface"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait