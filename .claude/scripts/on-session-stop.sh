#!/bin/bash
# Session stop: commit and push pending changes
# Runs as Stop hook

if git rev-parse --is-inside-work-tree &>/dev/null; then
  BRANCH=$(git branch --show-current 2>/dev/null)
  if [ -n "$BRANCH" ] && [ "$BRANCH" != "master" ] && [ "$BRANCH" != "main" ]; then
    git add -A 2>/dev/null
    if ! git diff --cached --quiet 2>/dev/null; then
      git commit -m "auto-save: session stop on $BRANCH" 2>/dev/null || true
      git push -u origin "$BRANCH" 2>/dev/null || true
    fi
  fi
fi
