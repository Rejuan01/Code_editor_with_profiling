import glob
import os
import subprocess
import sys

file1 = "./annotate/annotation.txt"
file2 = "./annotate/summary.txt"

if len(sys.argv) != 2:
    print(f"Usage: python3 {sys.argv[0]} <source.cpp>")
    sys.exit(1)

src = sys.argv[1]
exe = os.path.splitext(os.path.basename(src))[0]

# Compile (no optimization)
subprocess.run(
    ["g++", "-g", src, "-o", exe],
    check=True
)

# ---------------- Callgrind ----------------

subprocess.run(
    ["valgrind", "--tool=callgrind", f"./{exe}"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=True
)

call_file = max(glob.glob("callgrind.out.*"), key=os.path.getmtime)

with open(file1, "w") as f:
    subprocess.run(
        ["callgrind_annotate", call_file],
        stdout=f,
        check=True
    )

os.remove(call_file)

# ---------------- Cachegrind ----------------

with open(file2, "w") as f:
    subprocess.run(
        [
            "valgrind",
            "--tool=cachegrind",
            "--cache-sim=yes",
            "--branch-sim=yes",
            f"./{exe}",
        ],
        stdout=subprocess.DEVNULL,   # discard program output
        stderr=f,                    # Valgrind summary goes here
        check=True,
    )

cache_file = max(glob.glob("cachegrind.out.*"), key=os.path.getmtime)
os.remove(cache_file)