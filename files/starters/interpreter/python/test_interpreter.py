"""CS374 Interpreter assignment: run every program in programs/ and compare its output.

Run with: python3 test_interpreter.py     Each program has a .expected file beside it.
Programs you have not reached yet fail, so the PASS lines grow as you work.
"""

import glob
import os
import subprocess
import sys

failed = 0
programs = sorted(glob.glob("programs/*.ml"))
for path in programs:
    result = subprocess.run([sys.executable, "mylang.py", path], capture_output=True, text=True)
    expected = open(path[:-3] + ".expected").read()
    if result.stdout == expected:
        print("PASS", os.path.basename(path))
    else:
        failed += 1
        last = (result.stderr.strip().splitlines() or result.stdout.strip().splitlines() or ["no output"])[-1]
        print("FAIL", os.path.basename(path), "--", last)
print(f"{len(programs) - failed} passed, {failed} failed")
