#!/usr/bin/env bash
# Clean up empty/minimal session memory files across Claude Code workspace agents
set -euo pipefail

MEMORY_BASE="${HOME}/.claude/projects"
SUBCOMMAND="${1:-scan}"

# Colors (disabled when not a terminal)
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  CYAN='\033[0;36m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' CYAN='' BOLD='' NC=''
fi

# Classify a single .md file
# Returns: SKIP, EMPTY, MINIMAL, or OK
classify_file() {
  local file="$1"
  local size
  size=$(wc -c < "$file" | tr -d ' ')

  # Only evaluate .md files
  [[ "$file" != *.md ]] && echo "SKIP" && return

  # Read first line
  local first_line
  first_line=$(head -1 "$file")

  # Only evaluate files starting with "# Session:"
  if [[ "$first_line" != "# Session:"* ]]; then
    echo "SKIP"
    return
  fi

  # Files > 1500 bytes are directly OK
  if [ "$size" -gt 1500 ]; then
    echo "OK"
    return
  fi

  # Check for Conversation Summary section
  if ! grep -q '^## Conversation Summary' "$file" 2>/dev/null; then
    echo "EMPTY"
    return
  fi

  # Has Conversation Summary — check if minimal
  # Extract content after "## Conversation Summary" header
  local summary_content
  summary_content=$(sed -n '/^## Conversation Summary$/,/^## /{ /^## /d; p; }' "$file")

  # If summary section content is empty or whitespace only
  if [ -z "$(echo "$summary_content" | tr -d '[:space:]')" ]; then
    echo "EMPTY"
    return
  fi

  # Check for real user messages (not just system/startup boilerplate)
  # Boilerplate patterns: session info, startup greeting, system prompt references
  local stripped
  stripped=$(echo "$summary_content" | \
    grep -v -i -E '(session (key|id|source|started)|conversation info|startup|system prompt|initialized|began|greeted|no (substantial|meaningful) conversation|no real conversation|brief|trivial)' | \
    tr -d '[:space:]')

  # If < 500 bytes total and no real content after filtering boilerplate
  if [ "$size" -lt 500 ] && [ ${#stripped} -lt 50 ]; then
    echo "MINIMAL"
    return
  fi

  echo "OK"
}

# Extract agent name from project path
agent_name() {
  local dir="$1"
  local user
  user=$(whoami)
  basename "$dir" | sed "s/^-Users-${user}--//" | sed "s/^-Users-${user}-/~\//"
}

# --- Subcommands ---

cmd_scan() {
  echo -e "${BOLD}Memory Cleanup — Scan (dry-run)${NC}"
  echo "────────────────────────────────────────"
  echo ""

  local empty_count=0
  local minimal_count=0
  local ok_count=0
  local skip_count=0
  local total_bytes=0

  for mem_dir in "${MEMORY_BASE}"/*/memory; do
    [ -d "$mem_dir" ] || continue

    local agent
    agent=$(agent_name "$(dirname "$mem_dir")")

    for file in "$mem_dir"/*.md; do
      [ -f "$file" ] || continue

      local status
      status=$(classify_file "$file")
      local fsize
      fsize=$(wc -c < "$file" | tr -d ' ')

      case "$status" in
        EMPTY)
          echo -e "  ${RED}[EMPTY]${NC}   ${agent}/$(basename "$file") (${fsize} bytes)"
          empty_count=$((empty_count + 1))
          total_bytes=$((total_bytes + fsize))
          ;;
        MINIMAL)
          echo -e "  ${YELLOW}[MINIMAL]${NC} ${agent}/$(basename "$file") (${fsize} bytes)"
          minimal_count=$((minimal_count + 1))
          total_bytes=$((total_bytes + fsize))
          ;;
        OK)
          ok_count=$((ok_count + 1))
          ;;
        SKIP)
          skip_count=$((skip_count + 1))
          ;;
      esac
    done
  done

  echo ""
  echo "────────────────────────────────────────"
  echo -e "  ${RED}EMPTY:${NC}   ${empty_count} file(s)"
  echo -e "  ${YELLOW}MINIMAL:${NC} ${minimal_count} file(s)"
  echo -e "  ${GREEN}OK:${NC}      ${ok_count} file(s)"
  echo -e "  SKIP:    ${skip_count} file(s)"
  echo ""

  local to_delete=$((empty_count + minimal_count))
  if [ "$to_delete" -gt 0 ]; then
    echo -e "Would free ~${total_bytes} bytes (${to_delete} file(s))"
    echo -e "Run ${CYAN}clean${NC} to delete these files."
  else
    echo "Nothing to clean up."
  fi
}

cmd_clean() {
  echo -e "${BOLD}Memory Cleanup — Clean${NC}"
  echo "────────────────────────────────────────"
  echo ""

  local deleted=0
  local total_bytes=0

  for mem_dir in "${MEMORY_BASE}"/*/memory; do
    [ -d "$mem_dir" ] || continue

    local agent
    agent=$(agent_name "$(dirname "$mem_dir")")

    for file in "$mem_dir"/*.md; do
      [ -f "$file" ] || continue

      local status
      status=$(classify_file "$file")
      local fsize
      fsize=$(wc -c < "$file" | tr -d ' ')

      if [ "$status" = "EMPTY" ] || [ "$status" = "MINIMAL" ]; then
        echo -e "  ${RED}Deleted${NC} [${status}] ${agent}/$(basename "$file") (${fsize} bytes)"
        rm "$file"
        deleted=$((deleted + 1))
        total_bytes=$((total_bytes + fsize))
      fi
    done
  done

  echo ""
  echo "────────────────────────────────────────"
  if [ "$deleted" -gt 0 ]; then
    echo "Deleted ${deleted} file(s), freed ~${total_bytes} bytes."
  else
    echo "Nothing to clean up."
  fi
}

cmd_report() {
  echo -e "${BOLD}Memory Usage Report${NC}"
  echo "════════════════════════════════════════"
  echo ""

  local grand_files=0
  local grand_bytes=0
  local grand_empty=0
  local grand_minimal=0
  local grand_ok=0
  local grand_skip=0

  for mem_dir in "${MEMORY_BASE}"/*/memory; do
    [ -d "$mem_dir" ] || continue

    local agent
    agent=$(agent_name "$(dirname "$mem_dir")")

    local dir_files=0
    local dir_bytes=0
    local dir_empty=0
    local dir_minimal=0
    local dir_ok=0
    local dir_skip=0

    for file in "$mem_dir"/*.md; do
      [ -f "$file" ] || continue

      local fsize
      fsize=$(wc -c < "$file" | tr -d ' ')
      local status
      status=$(classify_file "$file")

      dir_files=$((dir_files + 1))
      dir_bytes=$((dir_bytes + fsize))

      case "$status" in
        EMPTY)   dir_empty=$((dir_empty + 1)) ;;
        MINIMAL) dir_minimal=$((dir_minimal + 1)) ;;
        OK)      dir_ok=$((dir_ok + 1)) ;;
        SKIP)    dir_skip=$((dir_skip + 1)) ;;
      esac
    done

    # Also count non-.md files
    local other_files=0
    for file in "$mem_dir"/*; do
      [ -f "$file" ] || continue
      [[ "$file" == *.md ]] && continue
      other_files=$((other_files + 1))
      local fsize
      fsize=$(wc -c < "$file" | tr -d ' ')
      dir_files=$((dir_files + 1))
      dir_bytes=$((dir_bytes + fsize))
    done

    # Skip agents with no files
    [ "$dir_files" -eq 0 ] && continue

    # Human-readable size
    local hr_size
    if [ "$dir_bytes" -ge 1048576 ]; then
      hr_size="$(echo "scale=1; $dir_bytes / 1048576" | bc)M"
    elif [ "$dir_bytes" -ge 1024 ]; then
      hr_size="$(echo "scale=1; $dir_bytes / 1024" | bc)K"
    else
      hr_size="${dir_bytes}B"
    fi

    echo -e "${CYAN}${agent}${NC}"
    echo -e "  Files: ${dir_files} (${hr_size})"
    printf "  Status: "
    local parts=()
    [ "$dir_empty" -gt 0 ]   && parts+=("${dir_empty} empty")
    [ "$dir_minimal" -gt 0 ] && parts+=("${dir_minimal} minimal")
    [ "$dir_ok" -gt 0 ]      && parts+=("${dir_ok} ok")
    [ "$dir_skip" -gt 0 ]    && parts+=("${dir_skip} skip")
    [ "$other_files" -gt 0 ] && parts+=("${other_files} other")
    local IFS=', '
    echo "${parts[*]}"
    echo ""

    grand_files=$((grand_files + dir_files))
    grand_bytes=$((grand_bytes + dir_bytes))
    grand_empty=$((grand_empty + dir_empty))
    grand_minimal=$((grand_minimal + dir_minimal))
    grand_ok=$((grand_ok + dir_ok))
    grand_skip=$((grand_skip + dir_skip))
  done

  local hr_grand
  if [ "$grand_bytes" -ge 1048576 ]; then
    hr_grand="$(echo "scale=1; $grand_bytes / 1048576" | bc)M"
  elif [ "$grand_bytes" -ge 1024 ]; then
    hr_grand="$(echo "scale=1; $grand_bytes / 1024" | bc)K"
  else
    hr_grand="${grand_bytes}B"
  fi

  echo "════════════════════════════════════════"
  echo -e "${BOLD}Total:${NC} ${grand_files} files (${hr_grand})"
  echo -e "  ${RED}Empty:${NC}   ${grand_empty}"
  echo -e "  ${YELLOW}Minimal:${NC} ${grand_minimal}"
  echo -e "  ${GREEN}OK:${NC}      ${grand_ok}"
  echo -e "  Skip:    ${grand_skip}"
}

# --- Main ---

case "$SUBCOMMAND" in
  scan)   cmd_scan   ;;
  clean)  cmd_clean  ;;
  report) cmd_report ;;
  *)
    echo "Usage: clean_memory.sh [scan|clean|report]"
    echo ""
    echo "  scan    Dry-run preview of files to delete (default)"
    echo "  clean   Delete EMPTY and MINIMAL session files"
    echo "  report  Show per-agent memory usage statistics"
    exit 1
    ;;
esac
