#!/bin/bash

PORT=9422
PROFILE_DIR="/Users/admins/Documents/chrome-user-tmp"

echo "Starting Chrome with Remote Debugging..."
echo ""
echo "Debug URL: http://localhost:$PORT"
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CHROME_PATH="google-chrome"
    PROFILE_DIR="/tmp/chrome-debug-profile"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# 检查 Chrome 是否已经运行
if pgrep -x "Google Chrome" > /dev/null || pgrep -x "chrome" > /dev/null; then
    echo "⚠️  WARNING: Chrome is already running!"
    echo "Please close all Chrome windows first."
    exit 1
fi

# 启动 Chrome
"$CHROME_PATH" \
    --remote-debugging-port=$PORT \
    --user-data-dir="$PROFILE_DIR" \
    # --no-first-run \
    # --disable-web-security \
    --no-default-browser-check &

echo "✅ Chrome started with debugging on port $PORT"
echo "💡 You can now run your agent script"
echo ""
echo "Press Ctrl+C to stop"

# 等待 Chrome 进程
wait