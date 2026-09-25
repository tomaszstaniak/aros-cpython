# l13move.py - L13. Before the fix, os.stat() reported an st_flags that the
# ABIv11 C library leaves unset: a different leftover value on every call.
# shutil.move() refuses to move a directory whose st_flags equals
# UF_IMMUTABLE or SF_IMMUTABLE, so moving a directory between volumes (and
# with it pip install --target on another volume than pip's temporary
# directory) failed only when the leftover happened to match. The first
# check tests that cause directly and so fails every time on an affected
# build; the other two are the operations themselves.
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

def flags():
    paths = ["/RAM", "/Python", "/Python/lib", "/tmp", "/Python/lib/python3.14"]
    if not hasattr(os.stat("/RAM"), "st_flags"):
        return "st_flags not reported"
    seen, hits, calls = set(), 0, 0
    for _ in range(200):
        for p in paths:
            seen.add(os.stat(p).st_flags)
            hits += shutil._is_immutable(p)
            calls += 1
    assert seen == {0}, "%d distinct st_flags values on plain directories, %d of %d calls looked immutable" % (len(seen), hits, calls)
    return "all 0"
check("flags", flags)

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
