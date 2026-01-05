#!/bin/bash

PORT=9422
PROFILE_DIR="/Users/admins/Downloads/chrome-user-tmp"
# CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_PATH="/Applications/Google Chrome Dev.app/Contents/MacOS/Google Chrome Dev"

# 检查 Chrome Dev 是否已经运行
## if pgrep -x "Google Chrome" > /dev/null || pgrep -x "chrome" > /dev/null; then

# 检查 Chrome Dev 是否已经运行
if pgrep -x "Google Chrome Dev" > /dev/null || pgrep -x "chrome-dev" > /dev/null; then
    echo "⚠️  WARNING: Chrome Dev is already running!"
    echo "Please close all Chrome Dev windows first."
    exit 1
fi


echo "✅ Chrome Dev started with debugging on port $PORT"
echo "Debug URL: http://localhost:$PORT"
echo "Press Ctrl+C to stop"

# 启动 Chrome Dev
"$CHROME_PATH" \
    --remote-debugging-port=$PORT \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    # --disable-web-security \
    --no-default-browser-check &

# 等待 Chrome 进程
wait