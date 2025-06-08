#!/bin/bash

echo "🚀 Starting DriverScore Backend Stack..."

# Start only database and backend API
docker-compose up --build db api

echo "✅ Backend stack started!"
echo "📊 API available at: http://localhost:8000"
echo "📖 API docs at: http://localhost:8000/docs"
echo "🗄️ Database at: localhost:5432"