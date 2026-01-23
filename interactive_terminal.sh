#!/bin/bash

# P3IF Interactive Terminal
# Simple interactive menu system for running tests, examples, and visualizations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="P3IF"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_NAME=".venv"
REQUIREMENTS_FILE="requirements.txt"

# Session management for unified output
SESSION_TIMESTAMP=""
SESSION_DIR=""

# Create unified session directory for Run All
create_session_dir() {
    SESSION_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    SESSION_DIR="$PROJECT_ROOT/outputs/run_${SESSION_TIMESTAMP}"
    mkdir -p "$SESSION_DIR/tests"
    mkdir -p "$SESSION_DIR/examples"
    mkdir -p "$SESSION_DIR/visualizations"
    mkdir -p "$SESSION_DIR/logs"
    
    # Create session metadata
    cat > "$SESSION_DIR/session_metadata.json" << EOF
{
    "session_id": "run_${SESSION_TIMESTAMP}",
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "project": "$PROJECT_NAME",
    "components": ["tests", "examples", "visualizations"]
}
EOF
    echo -e "${GREEN}Created session: $SESSION_DIR${NC}"
}

# Show header
show_header() {
    clear
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    P3IF INTERACTIVE TERMINAL                ║"
    echo "║            Patterns, Processes, Perspectives Framework       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Show main menu
show_main_menu() {
    clear
    show_header
    echo -e "${BLUE}P3IF Interactive Terminal${NC}"
    echo "========================="
    echo ""
    echo "Available Options:"
    echo ""
    echo "1)  Setup Environment (UV, venv, dependencies)"
    echo "2)  Run All Tests"
    echo "3)  Run All Examples"
    echo "4)  Generate Visualizations"
    echo "5)  Show System Status"
    echo "6)  Help & Information"
    echo "7)  Run All (1-4)"
    echo ""
    echo "0)  Exit"
    echo ""
    echo -n "Choose an option (0-7): "
}

# Setup UV if not present
setup_uv() {
    if ! command -v uv >/dev/null 2>&1; then
        echo "Installing UV package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    echo "UV package manager is ready"
}

# Create virtual environment
setup_venv() {
    if [ ! -d "$PROJECT_ROOT/$VENV_NAME" ]; then
        echo "Creating virtual environment..."
        uv venv "$PROJECT_ROOT/$VENV_NAME" --python 3.11
    fi
    source "$PROJECT_ROOT/$VENV_NAME/bin/activate"
    echo "Virtual environment activated"
}

# Install dependencies
install_deps() {
    setup_venv
    echo "Installing dependencies..."
    uv pip install --upgrade pip
    uv pip install -r "$PROJECT_ROOT/$REQUIREMENTS_FILE"
    uv pip install -e "$PROJECT_ROOT"
    echo "Dependencies installed"
}

# Run tests
run_tests() {
    echo "Running test suite..."
    local output_dir="${SESSION_DIR:-$PROJECT_ROOT/outputs}/tests"
    mkdir -p "$output_dir"
    cd "$PROJECT_ROOT"
    python tests/run_all_tests.py -v --output "$output_dir/test_report.json" 2>&1 | tee "$output_dir/test_output.log"
}

# Run examples
run_examples() {
    echo "Running examples..."
    local output_dir="${SESSION_DIR:-$PROJECT_ROOT/outputs/examples}"
    mkdir -p "$output_dir"
    cd "$PROJECT_ROOT"
    python scripts/run_examples.py --output-dir "$output_dir" 2>&1 | tee "${SESSION_DIR:-$PROJECT_ROOT/outputs}/logs/examples.log"
}

# Generate visualizations
gen_viz() {
    echo "Generating visualizations..."
    local output_dir="${SESSION_DIR:-$PROJECT_ROOT/outputs}/visualizations"
    mkdir -p "$output_dir"
    cd "$PROJECT_ROOT"
    python scripts/generate_final_visualizations.py --output-dir "$output_dir" 2>&1 | tee "${SESSION_DIR:-$PROJECT_ROOT/outputs}/logs/visualizations.log"
}

# Show status
show_status() {
    echo ""
    echo -e "${BLUE}System Status${NC}"
    echo "=============="
    echo ""

    echo "Project: $PROJECT_NAME"
    echo "Location: $PROJECT_ROOT"
    echo ""

    if [ -d "$PROJECT_ROOT/$VENV_NAME" ]; then
        echo -e "${GREEN}Virtual environment: Ready${NC}"
    else
        echo -e "${YELLOW}Virtual environment: Not created${NC}"
    fi

    if command -v uv >/dev/null 2>&1; then
        echo -e "${GREEN}UV package manager: Installed${NC}"
    else
        echo -e "${YELLOW}UV package manager: Not installed${NC}"
    fi

    echo ""
    echo "Output directories:"
    echo "  Tests: $PROJECT_ROOT/outputs/tests/"
    echo "  Examples: $PROJECT_ROOT/outputs/examples/"
    echo "  Visualizations: $PROJECT_ROOT/outputs/visualizations/"
    echo ""
}

# Show help
show_help() {
    echo ""
    echo -e "${BLUE}P3IF Interactive Terminal${NC}"
    echo "=========================="
    echo ""
    echo "Usage:"
    echo "  ./interactive_terminal.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h      Show this help message"
    echo "  --status        Show system status"
    echo "  --auto          Run complete automated workflow"
    echo "  --commands CMD  Run comma-separated commands"
    echo ""
    echo "Interactive Mode:"
    echo "  When run without options, displays a numbered menu with these options:"
    echo ""
    echo "  1) Setup Environment"
    echo "     - Install UV package manager"
    echo "     - Create virtual environment"
    echo "     - Install dependencies"
    echo ""
    echo "  2) Run All Tests"
    echo "     - Execute comprehensive test suite"
    echo "     - Generate test reports and coverage"
    echo ""
    echo "  3) Run All Examples"
    echo "     - Execute example orchestrators"
    echo "     - Generate example results and logs"
    echo ""
    echo "  4) Generate Visualizations"
    echo "     - Create PNG visualizations and animations"
    echo "     - Generate interactive web portal"
    echo ""
    echo "  5) Show System Status"
    echo "     - Display environment and system information"
    echo ""
    echo "  6) Help & Information"
    echo "     - Show this help message"
    echo ""
    echo "  7) Run All (1-4)"
    echo "     - Setup, run tests, run examples, and generate visualizations"
    echo ""
    echo "  0) Exit"
    echo "     - Exit the terminal"
    echo ""
    echo "Command Line Examples:"
    echo "  ./interactive_terminal.sh --auto"
    echo "  ./interactive_terminal.sh --commands setup_uv,run_tests,run_examples"
    echo ""
}

# Interactive loop with numbered menu
interactive_loop() {
    while true; do
        show_main_menu
        read -r choice

        echo ""  # Add spacing

        case "$choice" in
            1)
                echo -e "${GREEN}Setting up environment...${NC}"
                setup_uv
                setup_venv
                install_deps
                echo -e "${GREEN}Environment setup completed!${NC}"
                ;;
            2)
                echo -e "${GREEN}Running all tests...${NC}"
                run_tests
                ;;
            3)
                echo -e "${GREEN}Running all examples...${NC}"
                run_examples
                ;;
            4)
                echo -e "${GREEN}Generating visualizations...${NC}"
                gen_viz
                ;;
            5)
                show_status
                ;;
            6)
                show_help
                ;;
            7)
                echo -e "${GREEN}Running all operations (1-4)...${NC}"
                echo ""
                # Create unified session directory for all outputs
                create_session_dir
                echo ""
                echo -e "${BLUE}Step 1/4: Setting up environment...${NC}"
                setup_uv
                setup_venv
                install_deps
                echo -e "${GREEN}Environment setup completed!${NC}"
                echo ""
                echo -e "${BLUE}Step 2/4: Running all tests...${NC}"
                run_tests
                echo -e "${GREEN}Tests completed!${NC}"
                echo ""
                echo -e "${BLUE}Step 3/4: Running all examples...${NC}"
                run_examples
                echo -e "${GREEN}Examples completed!${NC}"
                echo ""
                echo -e "${BLUE}Step 4/4: Generating visualizations...${NC}"
                gen_viz
                echo -e "${GREEN}Visualizations completed!${NC}"
                echo ""
                echo -e "${GREEN}All operations completed successfully!${NC}"
                echo -e "${BLUE}📁 All outputs saved to: ${SESSION_DIR}${NC}"
                ;;
            0)
                echo -e "${GREEN}Goodbye!${NC}"
                break
                ;;
            *)
                echo -e "${RED}Invalid choice. Please select 0-7.${NC}"
                ;;
        esac

        if [ "$choice" != "0" ]; then
            echo ""
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read -r
        fi
        echo ""
    done
}

# Execute commands automatically
execute_commands() {
    local commands=("$@")

    # Ensure UV is set up first
    setup_uv

    for cmd in "${commands[@]}"; do
        case "$cmd" in
            setup_uv)
                setup_uv
                ;;
            setup_venv)
                setup_venv
                ;;
            install_deps)
                install_deps
                ;;
            run_tests)
                run_tests
                ;;
            run_examples)
                run_examples
                ;;
            gen_viz)
                gen_viz
                ;;
            status)
                show_status
                ;;
            run_all)
                setup_venv
                install_deps
                run_tests
                run_examples
                gen_viz
                show_status
                ;;
            *)
                echo -e "${RED}Unknown command: $cmd${NC}"
                ;;
        esac
        echo ""
    done
}

# Main execution
main() {
    # Parse command line arguments
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        --auto)
            # Automated mode - run predefined workflow
            show_header
            echo -e "${GREEN}Running automated P3IF workflow...${NC}"
            execute_commands "run_all"
            echo -e "${GREEN}Automated workflow completed!${NC}"
            exit 0
            ;;
        --commands)
            # Custom commands mode - expects comma-separated commands as second argument
            if [ -n "${2:-}" ]; then
                show_header
                echo -e "${GREEN}Running custom commands: $2${NC}"
                IFS=',' read -ra COMMANDS <<< "$2"
                execute_commands "${COMMANDS[@]}"
                echo -e "${GREEN}Custom commands completed!${NC}"
                exit 0
            else
                echo -e "${RED}Error: --commands requires a comma-separated list of commands${NC}"
                echo "Example: --commands setup_uv,run_tests,run_examples"
                exit 1
            fi
            ;;
        *)
            # Interactive mode with numbered menu
            interactive_loop
            ;;
    esac
}

# Run main function with all arguments
main "$@"