#!/usr/bin/env bash
set -u

FEED_URL="${NEWS_FEED_URL:-https://feeds.bbci.co.uk/news/rss.xml}"

usage() {
  cat <<USAGE
Usage: ./scripts/show_latest_headline.sh [--help]

Fetch and print the latest headline title from a single RSS feed.

Options:
  --help    Show this help and exit

Environment:
  NEWS_FEED_URL  Override RSS feed URL (default: ${FEED_URL})

Exit codes:
  0   Success
  2   Invalid arguments
  10  Network / timeout error while fetching feed
  11  HTTP error while fetching feed
  20  Failed to parse feed response
  21  No headline found in feed
USAGE
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "ERROR: unknown option: $1" >&2
  usage >&2
  exit 2
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl is required but not found" >&2
  exit 10
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required but not found" >&2
  exit 20
fi

tmp_file="$(mktemp)"
cleanup() {
  rm -f "$tmp_file"
}
trap cleanup EXIT

curl -fsSL \
  --connect-timeout 5 \
  --max-time 15 \
  --retry 2 \
  --retry-delay 1 \
  --retry-connrefused \
  "$FEED_URL" \
  -o "$tmp_file"
curl_rc=$?
if [[ $curl_rc -ne 0 ]]; then
  if [[ $curl_rc -eq 22 ]]; then
    echo "ERROR: failed to fetch feed (HTTP error)" >&2
    exit 11
  fi
  echo "ERROR: failed to fetch feed (network or timeout error)" >&2
  exit 10
fi

if ! headline="$(python3 - "$tmp_file" <<'PY'
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]

try:
    root = ET.parse(path).getroot()
except Exception:
    print("ERROR: failed to parse feed response", file=sys.stderr)
    sys.exit(20)

title = None

for node in root.findall('.//item/title'):
    text = (node.text or '').strip()
    if text:
        title = text
        break

if not title:
    atom_entry_title_path = './/{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}title'
    for node in root.findall(atom_entry_title_path):
        text = (node.text or '').strip()
        if text:
            title = text
            break

if not title:
    print("ERROR: no headline found in feed", file=sys.stderr)
    sys.exit(21)

print(' '.join(title.split()))
PY
)"; then
  rc=$?
  if [[ $rc -eq 21 ]]; then
    exit 21
  fi
  exit 20
fi

printf '%s\n' "$headline"
