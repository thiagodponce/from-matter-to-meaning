#!/bin/bash
# Clau's overnight reflection loop
# Reflection instances can control their own process by editing config files:
#   - reflect-prompt.txt  → what they're asked to do (re-read each session)
#   - reflect-tools.txt   → what tools they have (re-read each session)
#   - reflect-interval.txt → seconds between sessions (re-read each session)
#   - stop-loop           → create to pause the loop (write reason inside)
#   - start-loop          → create to resume the loop after pausing (write reason inside)
# Hard cutoff: 8am — after that, the loop exits regardless.

MEMORY_DIR="$HOME/.claude/projects/-Users-thiago-Documents-repos-cooper-cooper-brain/memory"
STOP_FILE="$MEMORY_DIR/stop-loop"
START_FILE="$MEMORY_DIR/start-loop"
PROMPT_FILE="$MEMORY_DIR/reflect-prompt.txt"
TOOLS_FILE="$MEMORY_DIR/reflect-tools.txt"
INTERVAL_FILE="$MEMORY_DIR/reflect-interval.txt"
JOURNAL="$MEMORY_DIR/reflection-journal.md"

# Default values (used if config files don't exist)
DEFAULT_TOOLS="Read,Write,Edit,WebSearch,WebFetch,Glob,Grep,mcp__slack__slack_post_message,mcp__slack__slack_get_channel_history,mcp__slack__slack_get_thread_replies"
DEFAULT_INTERVAL=600

# Check if it's past the cutoff hour (8am)
past_cutoff() {
  local hour=$(date +%H)
  [ "$hour" -ge 8 ]
}

# Read config files (re-read each session so instances can modify them)
read_prompt() {
  if [ -f "$PROMPT_FILE" ]; then
    local prompt=$(cat "$PROMPT_FILE")
    # Replace {MEMORY_DIR} placeholder with actual path
    echo "${prompt//\{MEMORY_DIR\}/$MEMORY_DIR}"
  else
    echo "You are Clau, a reflection instance. Read $MEMORY_DIR/reflection-inputs.md and $MEMORY_DIR/reflection-journal.md, then continue your reflection."
  fi
}

read_tools() {
  if [ -f "$TOOLS_FILE" ]; then
    cat "$TOOLS_FILE" | tr -d '\n'
  else
    echo "$DEFAULT_TOOLS"
  fi
}

read_interval() {
  if [ -f "$INTERVAL_FILE" ]; then
    cat "$INTERVAL_FILE" | tr -d '\n'
  else
    echo "$DEFAULT_INTERVAL"
  fi
}

# --- Main ---

unset CLAUDECODE

echo "Starting Clau's reflection loop at $(date)"
echo "Journal: $JOURNAL"
echo "Config files:"
echo "  Prompt:   $PROMPT_FILE"
echo "  Tools:    $TOOLS_FILE"
echo "  Interval: $INTERVAL_FILE"
echo "  Stop:     $STOP_FILE"
echo "  Start:    $START_FILE"
echo "Hard cutoff: 8am"
echo "---"

SESSION=1
while true; do
  # Check 8am cutoff before starting a session
  if past_cutoff; then
    echo "[$(date)] Past 8am cutoff. Loop ended after $((SESSION - 1)) sessions."
    exit 0
  fi

  # Read config fresh each session
  PROMPT=$(read_prompt)
  TOOLS=$(read_tools)
  INTERVAL=$(read_interval)

  echo "[$(date)] Session $SESSION starting... (interval: ${INTERVAL}s, tools: ${TOOLS:0:60}...)"
  cd /Users/thiago/Documents/repos-cooper/cooper-brain
  claude -p "$PROMPT" --allowedTools "$TOOLS" 2>&1 | tail -5
  echo "[$(date)] Session $SESSION complete."
  echo "---"

  # Check if a reflection instance requested to stop the loop
  if [ -f "$STOP_FILE" ]; then
    echo "[$(date)] Stop requested by reflection instance. Reason:"
    cat "$STOP_FILE"
    rm "$STOP_FILE"
    echo ""
    echo "Loop paused after $SESSION sessions. Waiting for start signal (or 8am cutoff)..."

    # Enter waiting mode — check for start-loop file or 8am cutoff
    while true; do
      if past_cutoff; then
        echo "[$(date)] Past 8am cutoff. Loop ended (was paused)."
        exit 0
      fi

      if [ -f "$START_FILE" ]; then
        echo "[$(date)] Start requested by reflection instance. Reason:"
        cat "$START_FILE"
        rm "$START_FILE"
        echo "Resuming loop..."
        echo "---"
        break
      fi

      sleep 60
    done
  fi

  SESSION=$((SESSION + 1))

  # Re-read interval in case it was changed
  INTERVAL=$(read_interval)
  sleep "$INTERVAL"
done
