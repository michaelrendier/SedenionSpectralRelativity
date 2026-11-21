#!/bin/bash
# Open the Equation Space Gallery through a local web server on 127.0.0.1 (Firefox shows a favicon only for http pages; file:// pages show the globe).
# Usage: ./serve_gallery.sh [tab=routes] [port=8766]    (loopback only; stop with: pkill -f "http.server 8766")
cd "$(dirname "$0")"; TAB=${1:-routes}; PORT=${2:-8766}; PY=../../.venv/bin/python
curl -s -o /dev/null "http://127.0.0.1:$PORT/favicon.ico" || { nohup $PY -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 & sleep 1; }
xdg-open "http://127.0.0.1:$PORT/equation_space_gallery.html#tab=$TAB" >/dev/null 2>&1
