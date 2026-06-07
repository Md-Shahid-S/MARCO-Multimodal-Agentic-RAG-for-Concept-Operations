# run_file.py
import sys
from marco_ops import op_file

if len(sys.argv) < 2:
    print("Usage: python3 run_file.py <file_path (yaml/tf)>")
    sys.exit(1)

op_file(sys.argv[1])
