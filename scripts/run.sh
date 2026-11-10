
#!/usr/bin/env bash

# Stop if any command fails
set -e

# Find the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Move to the project root
cd "$PROJECT_ROOT"

echo "================================"
echo " Personal Finance Analytics Tool"
echo "================================"

# Create output directory if it doesn't exist
mkdir -p output

# Find the project's Python virtual environment
if [ -x ".venv/bin/python3" ]; then
    PYTHON=".venv/bin/python3"
elif [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif [ -x ".venv/Scripts/python.exe" ]; then
    PYTHON=".venv/Scripts/python.exe"
else
    echo "Error: Python virtual environment not found!"
    echo "Please create the .venv environment first."
    exit 1
fi

# Run the application
echo ""
echo "Running application..."
"$PYTHON" main.py

echo ""
echo "Application completed successfully!"
