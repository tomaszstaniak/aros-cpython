# imports11.py - try every top-level stdlib module this interpreter lists.
# "I OK n", then one "I FAIL name: error" line per module that did not import,
# then "I-END ok/total". Windows/macOS-only modules are expected failures.
import sys, importlib
names = sorted(n for n in sys.stdlib_module_names if not n.startswith("_") or n in (
    "_ssl", "_hashlib", "_sqlite3", "_ctypes", "_decimal", "_socket", "_lzma",
    "_bz2", "_zstd", "_uuid", "_curses", "_dbm", "_gdbm", "_tkinter", "_multiprocessing",
    "_posixsubprocess", "_posixshmem"))
skip = {"antigravity", "this", "idlelib", "turtledemo", "__phello__", "tkinter", "turtle"}
ok = 0
fails = []
for n in names:
    if n in skip:
        continue
    try:
        importlib.import_module(n)
        ok += 1
    except BaseException as e:
        fails.append((n, "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:70] if str(e) else "")))
for n, e in fails:
    print("I FAIL %-18s %s" % (n, e))
print("I-END %d/%d" % (ok, ok + len(fails)), flush=True)
