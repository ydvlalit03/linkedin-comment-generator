#!/bin/bash

# Start FastAPI backend on port 8000 (background)
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Next.js frontend on PORT (Railway sets this)
cd /app/frontend
PORT=${PORT:-3000}
HOSTNAME=0.0.0.0
BACKEND_URL=http://localhost:8000

export PORT HOSTNAME BACKEND_URL

node server.js &
FRONTEND_PID=$!

echo "Backend running on :8000 (PID $BACKEND_PID)"
echo "Frontend running on :$PORT (PID $FRONTEND_PID)"

# Wait for either to exit
wait -n $BACKEND_PID $FRONTEND_PID
