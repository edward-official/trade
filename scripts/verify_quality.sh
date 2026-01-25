#!/bin/bash
echo "🔍 Running Quality Checks..."
echo "--------------------------------"

echo "1. Ruff Check (Linting)"
ruff check .
if [ $? -ne 0 ]; then
    echo "❌ Linting failed!"
    exit 1
fi

echo "2. Ruff Format (Formatting)"
ruff format .
if [ $? -ne 0 ]; then
    echo "❌ Formatting failed!"
    exit 1
fi

echo "--------------------------------"
echo "✅ All checks passed!"
