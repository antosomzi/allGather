#!/bin/bash

echo "🎨 Starting DriverScore Frontend..."

# Start only frontend (assumes API is running elsewhere)
docker-compose up --build web

echo "✅ Frontend started!"
echo "🌐 App available at: http://localhost:3000"