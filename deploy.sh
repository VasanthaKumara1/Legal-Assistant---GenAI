#!/bin/bash

# Legal Assistant GenAI - Production Deployment Script
# This script deploys the application with Docker Compose

set -e  # Exit on any error

echo "🚀 Starting Legal Assistant GenAI Production Deployment..."

# Check if required files exist
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please copy .env.production.example to .env.production and configure your API keys"
    exit 1
fi

if [ ! -f "docker-compose.production.yml" ]; then
    echo "❌ Error: docker-compose.production.yml not found!"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs data ssl

# Check if OpenAI API key is configured
if ! grep -q "your_openai_api_key_here" .env.production; then
    echo "✅ OpenAI API key appears to be configured"
else
    echo "⚠️  Warning: Please update your OpenAI API key in .env.production"
    echo "The application will not work without a valid API key"
fi

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose -f docker-compose.production.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.production.yml ps

# Display access information
echo ""
echo "✅ Deployment completed!"
echo ""
echo "🔗 Access your Legal Assistant:"
echo "   Frontend UI: http://localhost:8501"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 To check logs:"
echo "   Backend: docker-compose -f docker-compose.production.yml logs backend"
echo "   Frontend: docker-compose -f docker-compose.production.yml logs frontend"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.production.yml down"
echo ""

# Test if services are responding
echo "🧪 Testing service health..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    else
        echo "⏳ Waiting for backend to be ready... (attempt $i/5)"
        sleep 5
    fi
done

for i in {1..5}; do
    if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
        echo "✅ Frontend is healthy"
        break
    else
        echo "⏳ Waiting for frontend to be ready... (attempt $i/5)"
        sleep 5
    fi
done

echo ""
echo "🎉 Legal Assistant GenAI is now running!"
echo "Open http://localhost:8501 in your browser to get started."