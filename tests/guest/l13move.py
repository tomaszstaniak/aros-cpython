# l13move.py - L13: moving a directory between volumes, and pip installing a
# wheel into a target on another volume than its temporary directory, then
# importing the installed package from there. Before the fix, os.stat() had
# an st_flags with an unset value, and shutil.move() could refuse the move
# with PermissionError "Cannot move the non-empty directory".
import os, sys, shutil, tempfile, importlib
WHEEL = "/Python/wheels/pyfiglet-1.0.4-py3-none-any.whl"
tag = "%d" % os.getpid()
results = []
def check(name, fn):
    try:
        r = fn(); results.append(True); print("M %-10s PASS %s" % (name, r), flush=True)
    except BaseException as e:
        results.append(False); print("M %-10s FAIL %s: %s" % (name, type(e).__name__, e), flush=True)

print("M st_flags  %s" % (hex(os.stat("/RAM").st_flags) if hasattr(os.stat("/RAM"), "st_flags") else "not reported"), flush=True)
print("M tempdir   %s" % tempfile.gettempdir(), flush=True)

def move_dir():
    src = "/RAM/l13-src-" + tag
    os.makedirs(src + "/sub")
    open(src + "/sub/f.txt", "w").write("x")
    dst = "/Python/l13-dst-" + tag
    shutil.move(src, dst)
    ok = open(dst + "/sub/f.txt").read() == "x" and not os.path.exists(src)
    shutil.rmtree(dst)
    assert ok
    return "RAM: -> SYS:Python"
check("move", move_dir)

def pip_target():
    target = "/Python/l13-target-" + tag
    from pip._internal.cli.main import main as pipmain
    rc = pipmain(["install", "--no-index", "--no-build-isolation", "--quiet",
                  "--target", target, WHEEL])
    assert rc == 0, "pip returned %s" % rc
    sys.path.insert(0, target)
    mod = importlib.import_module("pyfiglet")
    where = mod.__file__
    assert where.startswith(target), where
    shutil.rmtree(target)
    return "imported from " + where
check("pip", pip_target)
print("M-END %d/%d" % (sum(results), len(results)), flush=True)
