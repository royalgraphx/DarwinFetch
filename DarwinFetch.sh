#!/bin/bash

# Detect the operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    python_executable="python3"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    python_executable="python"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    python_executable="python3"
else
    echo "Unsupported operating system"
    exit 1
fi

# Run the Python script using the selected Python executable
$python_executable src/main.py
