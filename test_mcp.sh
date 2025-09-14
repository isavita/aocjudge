#!/usr/bin/env bash
set -euo pipefail

# ---------- Config ----------
MCP_URL="${MCP_URL:-https://aocjudge.fly.dev/mcp}"
CASE_NAME="${CASE_NAME:-day1_part1_2015}"
LANGUAGE="${LANGUAGE:-python}"
CODE_PY='s=open("./input.txt").read().strip();print(s.count("(")-s.count(")"))'
RETRY_MAX=30                 # total attempts if daemon is cold
RETRY_BASE_SLEEP=1           # seconds; backoff is min(10, RETRY_BASE_SLEEP*2^(n-1))

# ---------- Checks ----------
if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required. Install jq and re-run." >&2
  exit 1
fi

# ---------- Helpers ----------
rand_hex() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 16
  else
    # poor-man's fallback
    printf '%s' "$(date +%s%N)$$RANDOM" | md5sum | awk '{print $1}'
  fi
}

# Extract JSON lines from SSE stream (lines prefixed by "data: ")
sse_to_json() {
  awk '/^data: /{ sub(/^data: /,""); print }'
}

# POST JSON-RPC over SSE, return the LAST JSON object from the stream
mcp_post() {
  local json="$1"
  curl -sS -N \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -H "Mcp-Session-Id: $SESSION" \
    -d "$json" \
    "$MCP_URL" | sse_to_json | tail -n 1
}

# ---------- 1) Open a session ----------
SESSION="${SESSION:-$(rand_hex)}"
echo "SESSION=$SESSION"

INIT_PAYLOAD=$(jq -nc '{
  jsonrpc:"2.0",
  id:"1",
  method:"initialize",
  params:{ protocolVersion:"2024-11-05", capabilities:{} }
}')

INIT_RESP="$(mcp_post "$INIT_PAYLOAD")"
echo "initialize => $(jq -c . <<<"$INIT_RESP")"

# Optional: notify initialized (not strictly required by this server)
NOTIF_PAYLOAD=$(jq -nc '{jsonrpc:"2.0", method:"notifications/initialized"}')
NOTIF_RESP="$(mcp_post "$NOTIF_PAYLOAD" || true)"
[ -n "$NOTIF_RESP" ] && echo "notifications/initialized => $(jq -c . <<<"$NOTIF_RESP")"

# ---------- 2) List tools ----------
LIST_PAYLOAD=$(jq -nc '{jsonrpc:"2.0", id:"2", method:"tools/list"}')
LIST_RESP="$(mcp_post "$LIST_PAYLOAD")"
echo "tools/list => $(jq -c . <<<"$LIST_RESP")"

# ---------- 3) Call aoc_eval (with retries for cold dockerd) ----------
echo "Calling aoc_eval for $CASE_NAME in $LANGUAGE ..."
ATTEMPT=0
while :; do
  ATTEMPT=$((ATTEMPT+1))

  # Choose code per language if you want to test others
  case "$LANGUAGE" in
    python)   CODE="$CODE_PY" ;;
    javascript) CODE='const fs=require("fs");const s=fs.readFileSync("./input.txt","utf8").trim();let f=0;for (const c of s){if(c==="(")f++;else if(c===")")f--;}console.log(f);' ;;
    ruby)     CODE='s=File.read("./input.txt").strip;puts s.count("(")-s.count(")")' ;;
    rust)     CODE='use std::fs;fn main(){let s=fs::read_to_string("./input.txt").unwrap();let mut f=0;for c in s.chars(){if c=="(" {f+=1;} else if c==")" {f-=1;}}println!("{}",f);}' ;;
    d)        CODE='import std.stdio, std.file;void main(){auto s=readText("./input.txt");int f=0;foreach(c; s){if(c=="(")f++;else if(c==")")f--; }writeln(f);}' ;;
    racket)   CODE='#lang racket
(let ([s (string-trim (file->string "./input.txt"))])
  (displayln (for/fold ([f 0]) ([c (in-string s)])
    (cond [(char=? c #\() (add1 f)]
          [(char=? c #\)) (sub1 f)]
          [else f]))))' ;;
    *) echo "Unsupported LANGUAGE=$LANGUAGE"; exit 2;;
  esac

  EVAL_PAYLOAD=$(jq -nc --arg name "$CASE_NAME" --arg lang "$LANGUAGE" --arg code "$CODE" '{
    jsonrpc:"2.0",
    id:"3",
    method:"tools/call",
    params:{ name:"aoc_eval", arguments:{ name:$name, language:$lang, code:$code } }
  }')

  RESP="$(mcp_post "$EVAL_PAYLOAD")"
  echo "Attempt #$ATTEMPT => $(jq -c . <<<"$RESP")"

  # Pull structuredContent if present; fall back to content[0].text
  STRUCT="$(jq -er '.result.structuredContent // ( .result.content[0].text | try fromjson )' <<<"$RESP" 2>/dev/null || true)"
  if [ -z "$STRUCT" ]; then
    echo "No structuredContent; raw response above."
    exit 3
  fi

  EXIT_CODE="$(jq -r '.exit_code // empty' <<<"$STRUCT" || true)"
  PASS="$(jq -r '.pass // false' <<<"$STRUCT" || echo false)"
  GOT="$(jq -r '.got // empty' <<<"$STRUCT" || true)"
  STDERR="$(jq -r '.stderr // empty' <<<"$STRUCT" || true)"

  if [ "$PASS" = "true" ]; then
    echo "✅ PASS. got=$GOT"
    break
  fi

  if [ "$EXIT_CODE" = "125" ] || grep -qi 'docker daemon not ready' <<<"$STDERR"; then
    if [ "$ATTEMPT" -ge "$RETRY_MAX" ]; then
      echo "❌ Docker still not ready after $RETRY_MAX attempts."
      exit 4
    fi
    # exponential backoff with cap
    SLEEP=$(( RETRY_BASE_SLEEP * (2**(ATTEMPT-1)) ))
    [ "$SLEEP" -gt 10 ] && SLEEP=10
    echo "Daemon not ready yet (exit_code=$EXIT_CODE). Retrying in ${SLEEP}s..."
    sleep "$SLEEP"
    continue
  fi

  # Non-retryable failure
  echo "❌ FAIL. exit_code=$EXIT_CODE, got='$GOT'"
  [ -n "$STDERR" ] && echo "stderr: $STDERR"
  exit 5
done
