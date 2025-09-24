#!/bin/bash

# Simple P3IF Terminal
# Focuses on the core functionality that works

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    P3IF SIMPLE TERMINAL                      ║"
echo "║            Patterns, Processes, Perspectives Framework       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Function to run tests
run_tests() {
    echo -e "${GREEN}Running tests...${NC}"
    cd "$PROJECT_ROOT"
    python scripts/run_tests.py
    echo -e "${GREEN}Tests completed!${NC}"
}

# Function to run examples
run_examples() {
    echo -e "${GREEN}Running examples...${NC}"
    cd "$PROJECT_ROOT"
    python scripts/run_examples.py
    echo -e "${GREEN}Examples completed!${NC}"
}

# Function to show status
show_status() {
    echo -e "${BLUE}System Status${NC}"
    echo "=============="
    echo "Project: $PROJECT_ROOT"
    echo ""
    if [ -d ".venv" ]; then
        echo -e "${GREEN}Virtual environment: Ready${NC}"
    else
        echo -e "${YELLOW}Virtual environment: Not created${NC}"
    fi
    echo ""
    echo "Output directories:"
    echo "  Tests: output/tests/"
    echo "  Examples: output/examples/"
    echo "  Visualizations: output/visualizations/"
    echo ""
}

# Main menu
case "${1:-}" in
    --help|-h)
        echo "Usage: ./simple_terminal.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  tests        - Run test suite"
        echo "  examples     - Run example orchestrators"
        echo "  status       - Show system status"
        echo "  all          - Run complete workflow"
        echo "  --help       - Show this help"
        echo ""
        ;;
    tests)
        run_tests
        ;;
    examples)
        run_examples
        ;;
    status)
        show_status
        ;;
    all)
        echo -e "${GREEN}Running complete P3IF workflow...${NC}"
        run_tests
        run_examples
        show_status
        echo -e "${GREEN}Complete workflow finished!${NC}"
        ;;
    *)
        echo "P3IF Simple Terminal"
        echo "==================="
        echo ""
        echo "Choose an option:"
        echo "1) Run Tests"
        echo "2) Run Examples"
        echo "3) Show Status"
        echo "4) Run All"
        echo "0) Exit"
        echo ""
        read -p "Enter choice (1-4 or 0): " choice
        echo ""

        case "$choice" in
            1) run_tests ;;
            2) run_examples ;;
            3) show_status ;;
            4)
                echo -e "${GREEN}Running complete P3IF workflow...${NC}"
                run_tests
                run_examples
                show_status
                echo -e "${GREEN}Complete workflow finished!${NC}"
                ;;
            0) echo "Goodbye!" ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
        ;;
esac
