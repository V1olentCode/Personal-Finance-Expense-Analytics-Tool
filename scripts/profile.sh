
#!/usr/bin/env bash

# Stop if any command fails
set -e
set -o pipefail

# Find the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Move to the project root
cd "$PROJECT_ROOT"

echo "================================"
echo " Profiling Personal Finance Tool"
echo "================================"

# Create output directory
mkdir -p output

# Locate Python virtual environment
if [ -x ".venv/Scripts/python.exe" ]; then
    PYTHON=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    echo "Error: Python virtual environment not found!"
    exit 1
fi

# Run application with cProfile
echo ""
echo "Starting performance profiling..."

"$PYTHON" -m cProfile -s cumulative main.py | tee output/profile.txt

echo ""
echo "Profiling completed!"
echo "Results saved to output/profile.txt"
