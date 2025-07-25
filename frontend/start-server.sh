#!/bin/bash

# GramSetu Frontend Development Server Startup Script
# This script starts the Vite development server for the GramSetu application

echo "🚀 Starting GramSetu Frontend Development Server..."
echo "📍 Current directory: $(pwd)"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules directory not found. Installing dependencies..."
    npm install
    echo "✅ Dependencies installed successfully!"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from template!"
        echo "🔧 Please update your Gemini API key in the .env file"
    else
        echo "❌ .env.example file not found. Please create a .env file manually."
    fi
    echo ""
fi

# Start the development server
echo "🌟 Starting Vite development server..."
echo "🌐 The application will be available at: http://localhost:5173"
echo "🛠️  Press Ctrl+C to stop the server"
echo ""

# Start the server
npm run dev

# If the server stops, show a message
echo ""
echo "🛑 Development server stopped."
echo "💡 To restart, run: ./start-server.sh"
