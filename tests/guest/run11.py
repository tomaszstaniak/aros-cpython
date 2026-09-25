# run11.py OUTFILE SCRIPT ARGS... - run a test script with its stdout and
# stderr in OUTFILE, and end with the exit status on a line of its own.
# The file is opened here because a redirection given to the python launcher
# (a Shell script) does not reach the interpreter, and the Shell has no
# stderr redirection at all.
import sys, runpy, traceback
out = open(sys.argv[1], "w", buffering=1, encoding="utf-8", errors="backslashreplace")
sys.stdout = sys.stderr = out
sys.argv = sys.argv[2:]
rc = 0
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
except SystemExit as e:
    rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
except BaseException:
    traceback.print_exc(file=out)
    rc = 99
print("RUN11-EXIT", rc, flush=True)
out.close()
