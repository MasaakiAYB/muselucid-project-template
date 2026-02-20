#!/usr/bin/env bash
set -euo pipefail

SOURCE_URL="https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"

err() {
  printf 'ERROR: %s\n' "$1" >&2
}

fetch_latest_headline_raw() {
  local xml

  if ! xml="$(curl -fsSL --connect-timeout 10 --max-time 20 "$SOURCE_URL")"; then
    err "failed to fetch headline feed from ${SOURCE_URL}"
    return 1
  fi

  if [[ -z "${xml}" ]]; then
    err "empty response from news source"
    return 1
  fi

  local item
  item="$(printf '%s' "$xml" | tr '\n' ' ' | awk 'BEGIN{RS="<item>";FS="</item>"} NR==2 {print $1; exit}')"
  if [[ -z "${item}" ]]; then
    err "could not parse latest item from feed"
    return 1
  fi

  local title link pub_date
  title="$(printf '%s' "$item" | perl -0ne 'if (m{<title>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</title>}s) { print defined($1) && length($1) ? $1 : $2 }')"
  link="$(printf '%s' "$item" | perl -0ne 'if (m{<link>(.*?)</link>}s) { print $1 }')"
  pub_date="$(printf '%s' "$item" | perl -0ne 'if (m{<pubDate>(.*?)</pubDate>}s) { print $1 }')"

  if [[ -z "${title}" ]]; then
    err "latest item has no title"
    return 1
  fi

  printf 'title=%s\n' "$title"
  printf 'link=%s\n' "${link:-N/A}"
  printf 'published_at=%s\n' "${pub_date:-N/A}"
  printf 'source=%s\n' "$SOURCE_URL"
}

format_headline() {
  local raw="$1"
  local title link published_at source

  title="$(printf '%s\n' "$raw" | sed -n 's/^title=//p' | head -n1)"
  link="$(printf '%s\n' "$raw" | sed -n 's/^link=//p' | head -n1)"
  published_at="$(printf '%s\n' "$raw" | sed -n 's/^published_at=//p' | head -n1)"
  source="$(printf '%s\n' "$raw" | sed -n 's/^source=//p' | head -n1)"

  if [[ -z "${title}" ]]; then
    err "failed to format headline: title is missing"
    return 1
  fi

  cat <<OUT
Latest headline:
- Title: ${title}
- Published: ${published_at:-N/A}
- Link: ${link:-N/A}
- Source: ${source:-$SOURCE_URL}
OUT
}

print_headline() {
  local formatted="$1"

  if ! printf '%s\n' "$formatted"; then
    err "failed to write headline to stdout"
    return 1
  fi
}

source_check() {
  if ! curl -fsSIL --connect-timeout 10 --max-time 20 "$SOURCE_URL" >/dev/null; then
    err "news source is not reachable: ${SOURCE_URL}"
    return 1
  fi

  printf 'OK: source reachable (%s)\n' "$SOURCE_URL"
}

main() {
  local mode="show"

  if [[ "${1:-}" == "--raw" ]]; then
    mode="raw"
  elif [[ "${1:-}" == "--source-check" ]]; then
    mode="source-check"
  elif [[ "${1:-}" != "" ]]; then
    err "unknown option: ${1}"
    err "usage: $0 [--raw|--source-check]"
    return 2
  fi

  if [[ "$mode" == "source-check" ]]; then
    source_check
    return 0
  fi

  local raw
  if ! raw="$(fetch_latest_headline_raw)"; then
    return 1
  fi

  if [[ "$mode" == "raw" ]]; then
    printf '%s\n' "$raw"
    return 0
  fi

  local formatted
  if ! formatted="$(format_headline "$raw")"; then
    return 1
  fi

  if ! print_headline "$formatted"; then
    return 1
  fi
}

main "$@"
