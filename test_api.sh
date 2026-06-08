#!/bin/bash
# Start the server in the background
uvicorn backend.main:app --port 8000 &
SERVER_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 5

# Send the test request
echo "Sending test request for TCS.NS..."
curl -s -X POST "http://127.0.0.1:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"ticker": "TCS.NS"}' | python -m json.tool

# Kill the server
echo "Killing the server..."
kill $SERVER_PID
