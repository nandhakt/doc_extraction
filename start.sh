#!/bin/bash

# DocExtract AI - Startup Script
# Starts both the FastAPI backend and Streamlit frontend

echo "🚀 DocExtract AI - Starting Services"
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please create a .env file with your OPENAI_API_KEY"
    echo "   Example: echo 'OPENAI_API_KEY=your-key-here' > .env"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY" .env 2>/dev/null || grep -q "OPENAI_API_KEY=$" .env 2>/dev/null; then
    echo "❌ Error: OPENAI_API_KEY not set in .env file"
    exit 1
fi

echo ""
echo "📦 Starting FastAPI backend..."
python run_api.py &
API_PID=$!

# Wait for API to start
sleep 3

echo ""
echo "🎨 Starting Streamlit frontend..."
streamlit run streamlit_app.py --server.port 8501 &
STREAMLIT_PID=$!

echo ""
echo "======================================"
echo "✅ Services started successfully!"
echo ""
echo "   📊 API:       http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo "   🎨 Frontend:  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================"

# Handle shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $API_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait


