#!/bin/bash

# Team requirements installer for Soton LM Data Engineering
# Usage: ./install_team.sh [1|2|3]

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CENTRAL_REQS="$PROJECT_ROOT/requirements.txt"

# Team configuration
declare -A TEAMS=(
    [1]="division_1_academic"
    [2]="division_2_web" 
    [3]="division_3_social"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    echo "Usage: $0 [TEAM_NUMBER]"
    echo ""
    echo "Available teams:"
    echo "  1 - Academic (Research papers, educational material)"
    echo "  2 - Web (Wikipedia, news articles, general knowledge)"
    echo "  3 - Social (Social media platforms)"
    echo ""
    echo "Examples:"
    echo "  $0 1  # Install dependencies for Academic team"
    echo "  $0 2  # Install dependencies for Web team"
    echo "  $0 3  # Install dependencies for Social team"
}

# Validate input
if [ $# -ne 1 ]; then
    print_error "Team number argument required"
    show_usage
    exit 1
fi

TEAM_NUMBER="$1"
TEAM_NAME="${TEAMS[$TEAM_NUMBER]}"
TEAM_REQS="$PROJECT_ROOT/src/$TEAM_NAME/requirements.txt"

if [ -z "$TEAM_NAME" ]; then
    print_error "Invalid team number: $TEAM_NUMBER"
    show_usage
    exit 1
fi

print_info "Installing dependencies for Team $TEAM_NUMBER ($TEAM_NAME)"

# Check if requirements files exist
if [ ! -f "$CENTRAL_REQS" ]; then
    print_error "Central requirements not found: $CENTRAL_REQS"
    exit 1
fi

if [ ! -f "$TEAM_REQS" ]; then
    print_error "Team requirements not found: $TEAM_REQS"
    print_warning "Creating template team requirements file..."
    mkdir -p "$(dirname "$TEAM_REQS")"
    cat > "$TEAM_REQS" << EOF
# Team $TEAM_NUMBER ($TEAM_NAME) specific requirements
# Add your team's specialized dependencies here

EOF
    print_info "Created template: $TEAM_REQS"
    print_warning "Please add your team-specific dependencies to this file"
fi

# Install central requirements
print_info "Installing central requirements..."
if pip install -r "$CENTRAL_REQS"; then
    print_info "✓ Central requirements installed successfully"
else
    print_error "Failed to install central requirements"
    exit 1
fi

# Install team-specific requirements
print_info "Installing team-specific requirements..."
if pip install -r "$TEAM_REQS"; then
    print_info "✓ Team-specific requirements installed successfully"
else
    print_error "Failed to install team-specific requirements"
    exit 1
fi

# Verify installation
print_info "Verifying installation..."
if python -c "import prefect, pandas, duckdb"; then
    print_info "✓ Core packages verified"
else
    print_error "Core package verification failed"
    exit 1
fi

print_info "🎉 Installation completed for Team $TEAM_NUMBER ($TEAM_NAME)"
print_info "📁 Team directory: src/$TEAM_NAME"
print_info "📋 Team requirements: $TEAM_REQS"