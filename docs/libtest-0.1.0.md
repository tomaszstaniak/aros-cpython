# Lib/test results for 0.1.0 (x86_64 ABIv11)

CPython's own test suite, run against the 0.1.0 interpreter
(`a072b8ad8c79dfa4106fbbfee7016e037e17d096e1bd27868ebb5124731e1203`).
One pass, measured on 2026-09-28. These are measurements, not a claim that
the test suite passes: it does not.

## How it was run

- System: ABIv11 2026.09 (deadwood2 tag `ABIv11_2026.09`) installed on a
  QEMU disk, with the 0.1.0 package, `Lib/test` of CPython 3.14.7
  (identical to the upstream tarball) and a small harness. The same disk
  image was used earlier for runs under software emulation; this pass ran
  under QEMU 10.2.2 with KVM on an x86-64 Fedora 44 host (pc machine, host
  CPU, 2 vCPUs, 2 GB, e1000 with user networking).
- Each of the 492 test modules ran in a fresh interpreter:
  `regrtest -v --timeout 900 -u all,-largefile,-extralargefile`. The host
  stopped a module after 1500 s (power off and restart of the guest).
- Verdicts: PASS, FAIL (some test cases failed), ERROR (the module did not
  run, usually an import failure), SKIP (the whole module skipped),
  ENV_CHANGED, TIMEOUT (no result within 1500 s).
- Modules that timed out were not retried with longer limits; they are
  kept for separate diagnosis.

## Result

| Verdict | Modules |
|---|---|
| PASS | 218 |
| FAIL | 135 |
| ERROR | 30 |
| SKIP | 84 |
| TIMEOUT | 24 |
| ENV_CHANGED | 1 |
| total | 492 |

Test cases in the modules that returned (from regrtest's JUnit XML):
27629 passed, 240 failed, 2222 errors, 2625 skipped.

A timeout records only that no result came back. After a regrtest timeout
the guest was found unresponsive without a message on screen; whether that
was the test hanging or a failure while faulthandler reported the timeout
was not established for each case (the i386 build carries a fix, patch
0023, for one such failure found on ABIv11 earlier).

## Why modules did not run (ERROR, 30)

Two kinds are kept apart: a function of the port that fails, and a test
module that cannot be checked at all.

Verification blocked (the module's own subject was not tested):

| Cause | Modules |
|---|---|
| `test.support` imports `resource`, which is not built | 15, e.g. test_ast, test_call, test_class, test_copy, test_descr, test_exceptions, test_functools, test_json |
| imports of other modules not built (`termios`, `_remote_debugging`, `_testinternalcapi`) | 3 |

An import failure of this kind says nothing about the tested feature: for
example, test_json not running does not mean JSON does not work (JSON is
checked in ACCEPTANCE.txt).

Functions that fail:

| Cause | Modules |
|---|---|
| `socket(AF_UNIX)` fails with errno 43 although `AF_UNIX` is defined | 6 |
| no processes (`OSError` "aros does not support processes") | 2 |
| deleting or renaming an open file fails with `EBUSY` | 2 |
| `MemoryError` in regrtest's clean-up | 1 (test.test_asyncio.test_runners) |
| `KeyError` | 1 (test_tarfile) |

## Skips

The most frequent skip reasons, verbatim:

- 240 × ProcessPoolExecutor unavailable on this system
- 223 × test requires a Windows-compatible system
- 222 × _testinternalcapi required
- 131 × requires _testinternalcapi
- 130 × Test needs selectors.PollSelector
- 129 × requires Windows-flavoured path class
- 83 × (whole module) skipped
- 76 × ndarray object required for this test

The build has no CPython test modules (`--disable-test-modules`), so tests
that need `_testcapi` or `_testinternalcapi` skip. That is a build choice,
not a limit of AROS. Whether a skip belongs to another platform or is a gap
of this port is not decided here.

## Timeouts (24)

test_asyncio (buffered_proto, free_threading, ssl, sslproto, tasks),
test_concurrent_futures (as_completed, init, interpreter_pool), test_pydoc,
test__interpreters, test_codeop, test_httpservers, test_importlib,
test_interpreters, test_io, test_logging, test_shutil, test_signal,
test_socket, test_ssl, test_struct, test_threading, test_urllib2_localnet,
test_xmlrpc.

Many of these start servers or clients in worker threads, which L2 rules
out; that is a likely cause for those, not yet shown test by test.
