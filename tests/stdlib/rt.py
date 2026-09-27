# rt.py LOGDIR NAME TEST [REGRTEST OPTIONS...] - run one test of the standard
# test suite (Lib/test) with regrtest, in this interpreter, and write its full
# output to LOGDIR/NAME.log and its JUnit XML to LOGDIR/NAME.xml.
#
# Why a wrapper: a redirection given to the python launcher (a Shell script)
# does not reach the interpreter, and the AROS Shell cannot redirect stderr.
# The log is opened here, line buffered, so that as much as possible of it is
# on disk if the test brings the machine down.
#
# regrtest runs in this process (no -j): this port cannot start processes.
# Its --timeout option is kept: faulthandler's watchdog thread ends the
# interpreter with _exit() when a test runs too long, which works even though
# Ctrl-C and Break do not (L1). The host adds its own, longer limit.
import sys, os, time, runpy, faulthandler, traceback

logdir, name, testname = sys.argv[1], sys.argv[2], sys.argv[3]
opts = sys.argv[4:]
log = open(os.path.join(logdir, name + ".log"), "w", buffering=1,
           encoding="utf-8", errors="backslashreplace")
# regrtest reads the __stdout__/__stderr__ originals as well, and passes the
# stderr file descriptor to faulthandler: all of it must be the log.
sys.stdout = sys.stderr = sys.__stdout__ = sys.__stderr__ = log
print("RT-START", testname, time.time(), flush=True)


class SetupFaulthandler:
    """faulthandler as regrtest's setup_process() sees it.

    Test infrastructure only: on ABIv11 the C library cannot install a SIGSEGV
    handler (sigaction returns ENOSYS), so faulthandler.enable() and
    register() raise, and setup_process() would stop every test before it
    starts. Here the failure is written to the log and setup continues.
    The faulthandler module itself is not changed: test_faulthandler and every
    other test see the real one."""

    def __getattr__(self, name):
        return getattr(faulthandler, name)

    def enable(self, *args, **kw):
        try:
            faulthandler.enable(*args, **kw)
        except (RuntimeError, OSError) as e:
            print("RT-NOTE regrtest setup: faulthandler.enable() failed:", e, flush=True)

    def register(self, *args, **kw):
        try:
            faulthandler.register(*args, **kw)
        except (RuntimeError, OSError) as e:
            print("RT-NOTE regrtest setup: faulthandler.register() failed:", e, flush=True)


import test.libregrtest.setup
test.libregrtest.setup.faulthandler = SetupFaulthandler()

# Test infrastructure only: regrtest records every locale category before and
# after each test to detect tests that change it. It expects the query
# setlocale(category, None) to succeed for every LC_* constant; on ABIv11 the
# LC_MESSAGES query fails with locale.Error, which regrtest does not catch,
# and every test would end as "uncaught exception" before it runs. Categories
# that cannot be queried are left out of that bookkeeping and logged here;
# the locale module is not changed, so test_locale still sees the failure.
import locale
import test.libregrtest.save_env as save_env
queryable = []
for lc in save_env.saved_test_environment._lc:
    try:
        locale.setlocale(lc, None)
        queryable.append(lc)
    except locale.Error as e:
        print("RT-NOTE regrtest save_env: locale category %d not recorded: %s" % (lc, e), flush=True)
save_env.saved_test_environment._lc = queryable
sys.argv = ["python -m test"] + opts + [
    "--junit-xml", os.path.join(logdir, name + ".xml"), testname]
rc = None
t0 = time.time()
try:
    runpy.run_module("test", run_name="__main__", alter_sys=True)
    rc = 0
except SystemExit as e:
    rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
except BaseException:
    traceback.print_exc(file=log)
    rc = 99
print("RT-EXIT", rc, "%.1f" % (time.time() - t0), flush=True)
log.close()
