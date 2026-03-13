#!/bin/bash
# Security check: prevent committing secrets
# Runs as PreToolUse hook

# Check for common secret patterns in staged files
if git diff --cached --name-only 2>/dev/null | head -1 >/dev/null; then
  SECRETS=$(git diff --cached -G '(PRIVATE_KEY|sk-|password\s*=\s*"[^"]+")' --name-only 2>/dev/null)
  if [ -n "$SECRETS" ]; then
    echo "WARNING: Possible secrets detected in: $SECRETS"
  fi
fi
