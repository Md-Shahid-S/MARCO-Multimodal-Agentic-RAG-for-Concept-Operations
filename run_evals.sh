#!/bin/bash
# run.sh - Helper script to run evaluations

echo "==================================="
echo "    MARCO EVALUATION RUNNER        "
echo "==================================="

# Get absolute path to venv python
VENV_PYTHON="$(pwd)/venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $VENV_PYTHON"
    exit 1
fi

echo "Running Baseline Evaluation..."
cd baseline
"$VENV_PYTHON" evaluation/run_eval.py

echo ""
echo "Running Proposed MARCO Evaluation..."
cd ../proposed_solution
"$VENV_PYTHON" evaluation/run_eval.py --mode marco --queries data/base/eval_queries_50.json

echo ""
echo "Evaluation completed successfully!"
