#!/bin/bash
# Double-click in Finder to build (if needed), start the local server, and
# open pokeemerald-wasm in a dedicated Chrome app window.
set -e
cd "$(dirname "$0")"

PORT="${PORT:-8000}"
URL="http://localhost:$PORT"

if [ ! -f build/wasm/pokeemerald.wasm ]; then
  echo "pokeemerald.wasm not built yet — building now (this can take a while)…"
  make wasm
fi

if ! curl -s -o /dev/null "$URL"; then
  echo "Starting local server on port $PORT…"
  nohup node web/server.mjs > /tmp/pokeemerald-wasm-server.log 2>&1 &
  disown
  for _ in $(seq 1 60); do
    curl -s -o /dev/null "$URL" && break
    sleep 0.5
  done
fi

echo "Opening $URL in Chrome…"
open -na "Google Chrome" --args --app="$URL"
