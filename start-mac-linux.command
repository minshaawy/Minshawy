#!/bin/bash
# Auto-launcher for Mac/Linux
# Double-click this file to start the local server

cd "$(dirname "$0")"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   موقع الشيخ المنشاوي — Minshawi Tribute   ║"
echo "║              يبدأ التشغيل...                ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Try Python 3 first, then Python 2
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python غير مثبت / Python is not installed"
    echo ""
    echo "حمّل Python من / Download Python from:"
    echo "https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Find available port (8000, 8080, 8888, 3000)
PORT=8000
for try_port in 8000 8080 8888 3000 5000; do
    if ! lsof -Pi :$try_port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PORT=$try_port
        break
    fi
done

URL="http://localhost:$PORT"

echo "✅ الخادم شغال على / Server running at:"
echo "   $URL"
echo ""
echo "📂 افتح المتصفح على هذا العنوان"
echo "📂 Open browser at this address"
echo ""
echo "⏹  لإيقاف الخادم: اضغط Ctrl+C"
echo "⏹  To stop: press Ctrl+C"
echo ""

# Try to open browser automatically (Mac uses 'open', Linux uses 'xdg-open')
if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 1 && open "$URL" &
elif command -v xdg-open &> /dev/null; then
    sleep 1 && xdg-open "$URL" &
fi

# Start server
$PYTHON_CMD -m http.server $PORT
