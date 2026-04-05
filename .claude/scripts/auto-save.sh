#!/bin/bash
# Auto-save: stage changes after tool use
# Runs as PostToolUse hook

if git rev-parse --is-inside-work-tree &>/dev/null; then
  git add -A 2>/dev/null || true
fi
