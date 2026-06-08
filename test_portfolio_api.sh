#!/bin/bash
# Start the server in the background
uvicorn backend.main:app --port 8000 &
SERVER_PID=$!

# Wait for the server to start
sleep 5

# Send the test request
curl -s -X POST "http://127.0.0.1:8000/analyze-portfolio" \
     -H "Content-Type: application/json" \
     -d '{
"portfolio": [
{"ticker":"TCS.NS","weight":25},
{"ticker":"INFY.NS","weight":25},
{"ticker":"RELIANCE.NS","weight":25},
{"ticker":"HDFCBANK.NS","weight":25}
]
}' | python -m json.tool

# Kill the server
kill $SERVER_PID
