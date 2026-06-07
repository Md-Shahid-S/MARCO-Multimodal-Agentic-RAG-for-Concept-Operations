# run_vision.py
import sys
from marco_ops import op_vision

if len(sys.argv) < 2:
    print("Usage: python3 run_vision.py <image_path>")
    sys.exit(1)

op_vision(sys.argv[1])
