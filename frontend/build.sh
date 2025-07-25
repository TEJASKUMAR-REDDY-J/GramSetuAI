#!/bin/bash

# GramSetu Frontend Build Script
# This script builds the GramSetu application for production

echo "🏗️  Building GramSetu Frontend for Production..."
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
        echo "⚠️  Please update your Gemini API key in the .env file before production build!"
    else
        echo "❌ .env.example file not found. Please create a .env file manually."
    fi
    echo ""
fi

# Run the build
echo "📦 Building application..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build completed successfully!"
    echo "📁 Build files are available in the 'dist' directory"
    echo "🚀 Ready for deployment!"
else
    echo ""
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi
