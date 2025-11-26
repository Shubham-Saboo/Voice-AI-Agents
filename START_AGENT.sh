#!/bin/bash

# Quick start script for the Python agent
# This script starts the Python agent in development mode

cd /Users/shubhamsaboo/Voxology/agent-starter-python

echo "🚀 Starting Python Agent..."
echo "📁 Working directory: $(pwd)"
echo ""

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "❌ Error: .env.local not found!"
    echo "Please create .env.local with your LiveKit credentials"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=.*[^=]$" .env.local 2>/dev/null; then
    echo "⚠️  Warning: OPENAI_API_KEY not set in .env.local"
    echo "The agent will use LiveKit Inference models instead"
    echo ""
fi

# Start the agent
echo "🔊 Starting agent in development mode..."
echo "Press Ctrl+C to stop"
echo ""
uv run python src/agent.py dev


