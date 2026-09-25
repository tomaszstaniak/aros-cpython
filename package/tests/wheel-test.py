"""Offline wheel acceptance - install, import from the target, run, clean up.

Run:  python /Python/tests/wheel-test.py
Writes /RAM/aros-py-wheel.log AND stdout; ends with a SUMMARY line and a
non-zero exit code on any failure.

Everything runs IN THIS ONE PROCESS (AROS has no fork/subprocess): pip is driven
through its in-process entry point, so we see its real return code. The import
check requires pyfiglet.__file__ to live INSIDE the fresh target dir, so a
failed install can NOT pass by finding a pyfiglet installed somewhere else.
"""
import sys, os, shutil, importlib

WHEEL = "/Python/wheels/pyfiglet-1.0.4-py3-none-any.whl"
EXPECT_VER = "1.0.4"
TGT = "/RAM/aros-py-wheeltest-%d" % os.getpid()   # fresh, test-owned dir
LOG = "/RAM/aros-py-wheel.log"
_lf = open(LOG, "w", buffering=1)
def emit(s):
    print(s); _lf.write(s + "\n"); _lf.flush()

fails = []
def require(cond, ok_msg, bad_msg):
    if cond: emit("  ok   " + ok_msg)
    else:    emit("  FAIL " + bad_msg); fails.append(bad_msg)
    return cond

emit("wheel-test: start (target=%s)" % TGT)

# 0. the wheel must exist (negative-path guard: no wheel -> FAIL, never skip)
if not require(os.path.exists(WHEEL), "wheel present", "wheel missing: %s" % WHEEL):
    emit("\nSUMMARY 0 checks passed, 1 failed"); _lf.close(); sys.exit(1)

# 1. fresh empty target dir owned by this test
if os.path.exists(TGT): shutil.rmtree(TGT, ignore_errors=True)
os.makedirs(TGT)

# 2. install via pip's in-process entry point; capture the real return code
def pip_install():
    from pip._internal.cli.main import main as pipmain
    argv = ["install", "--no-index", "--no-build-isolation", "--target", TGT, WHEEL]
    try:
        return pipmain(argv)
    except SystemExit as e:      # pip may raise SystemExit instead of returning
        return int(e.code) if e.code is not None else 0
emit("wheel-test: pip install -> %s" % TGT)
rc = pip_install()
require(rc == 0, "pip returned 0", "pip returned %r" % (rc,))

# 3. import MUST come from the target dir (proves the install, not a stray copy)
sys.path.insert(0, TGT)
for m in list(sys.modules):
    if m == "pyfiglet" or m.startswith("pyfiglet."):
        del sys.modules[m]
mod_file = None
try:
    import pyfiglet
    importlib.reload(pyfiglet)
    mod_file = os.path.abspath(getattr(pyfiglet, "__file__", "") or "")
except Exception as e:
    emit("  FAIL import raised %r" % (e,)); fails.append("import")
    pyfiglet = None

tgt_abs = os.path.abspath(TGT) + os.sep
require(mod_file is not None and mod_file.startswith(tgt_abs),
        "imported from target (%s)" % mod_file,
        "imported from OUTSIDE target: %s" % mod_file)

# 4. version check
if pyfiglet is not None:
    ver = getattr(pyfiglet, "__version__", None)
    require(ver == EXPECT_VER, "version %s" % ver,
            "version %r != %s" % (ver, EXPECT_VER))
    # 5. actually RUN a function from the package
    try:
        art = pyfiglet.figlet_format("AROS")
        require(isinstance(art, str) and len(art.strip()) > 0,
                "figlet_format produced %d chars" % len(art),
                "figlet_format produced no output")
    except Exception as e:
        require(False, "", "figlet_format raised %r" % (e,))

# 6. clean up and confirm removal
sys.path.remove(TGT)
shutil.rmtree(TGT, ignore_errors=True)
require(not os.path.exists(TGT), "cleanup removed target",
        "cleanup FAILED, target remains: %s" % TGT)

npass = 6 - len(fails)  # 6 substantive checks when the wheel is present
emit("\nSUMMARY %d checks passed, %d failed" % (npass, len(fails)))
_lf.close()
sys.exit(0 if not fails else 1)
