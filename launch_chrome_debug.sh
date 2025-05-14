#!/bin/bash

# Kill any existing Chrome processes
pkill -f "Google Chrome"
sleep 2

# Create a user data directory if it doesn't exist
USER_DATA_DIR="$HOME/chrome-debug-profile"
mkdir -p "$USER_DATA_DIR"

# Launch Chrome in debug mode with specific options
echo "Launching Chrome in debug mode..."
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$USER_DATA_DIR" \
  --no-first-run \
  --no-default-browser-check \
  --disable-extensions \
  --disable-component-extensions-with-background-pages \
  --disable-background-networking \
  --disable-client-side-phishing-detection \
  --disable-sync \
  --metrics-recording-only \
  --disable-default-apps \
  --no-default-browser-check \
  --no-first-run \
  --disable-backgrounding-occluded-windows \
  --disable-renderer-backgrounding \
  --disable-background-timer-throttling \
  "about:blank" &

# Store the Chrome process ID
CHROME_PID=$!

# Wait a moment for Chrome to start
echo "Waiting for Chrome to start..."
sleep 5

# Check if Chrome is running and the debug port is accessible
if ! curl -s http://localhost:9222/json/version > /dev/null; then
  echo "Error: Chrome debug port is not accessible. Chrome may not have started properly."
  exit 1
fi

echo "Chrome is now running in debug mode with PID: $CHROME_PID"
echo "Debug URL: http://localhost:9222"
echo "Keep this terminal window open and run your script in a different terminal."
echo "Press Ctrl+C to stop Chrome when you're done."

# Wait for user to press Ctrl+C
wait $CHROME_PID
