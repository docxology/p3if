#!/bin/bash

# P3IF Interactive Terminal Wrapper
# This wrapper script provides backward compatibility for scripts/interactive_terminal.sh
# The main interactive terminal is now located at the repository root.

echo "P3IF Interactive Terminal Wrapper"
echo "=================================="
echo "The interactive terminal has been moved to the repository root."
echo "Please use: ./interactive_terminal.sh"
echo ""
echo "Redirecting to the main interactive terminal..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Execute the main interactive terminal
exec "$PROJECT_ROOT/interactive_terminal.sh" "$@"
