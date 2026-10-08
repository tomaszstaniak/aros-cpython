# CPython port: next development priorities

Assessment: 2026-10-08. Immediate target: x86-64 ABIv11; other ABIs retain
separate builds and verification. The development package now supplies an
embedding interface. The next challenge is making that interface dependable
for real applications while closing failures that make test runs difficult
to recover from.

## Recommended sequence

1. **Release the existing thread-ident correction with matching runtime/dev
   packages (implemented in 0.1.1).** Patch 0023 already corrects conversions in traceback thread
   naming, signal.pthread_kill and time.pthread_getcpuclockid. Its header records
   the ABIv11 faulthandler crash. Focused checks cover eight all-thread dumps
   with 32 workers and the matching static embedding example. pthread_kill
   remains an SDK EINVAL stub and pthread_getcpuclockid is unavailable.
   Version 0.1.0 is preserved; further work starts at item 2.

2. **Make Ctrl-C and Break produce KeyboardInterrupt.** Acceptance L1 records
   that neither interrupts a sleeping script; the previous mainline backlog
   also records a computing loop. For ABIv11, probe both independently and
   bridge the native break signal to CPython's pending-signal handling, including
   timer waits. Finish when wait/spin scripts can catch KeyboardInterrupt, the
   Shell remains usable, and repeated runs do not retain altered state.

3. **Validate embedding against GemRB.** First compile its GUIScript and the
   static link, then run an available demo/game script path. Expand the embedding
   tests around startup paths, C++ ownership, host-to-Python calls, Python-to-host
   calls, and GIL/thread entry only as the application needs them. Ensure DOS
   requester handling belongs to a documented application lifecycle. Upstream
   supports embedding a C/C++ application with registered builtin modules;
   no dynamic extension loader is required for this first integration.
   References: [CPython embedding](https://docs.python.org/3.14/extending/embedding.html),
   [GemRB Python configuration](https://github.com/gemrb/gemrb/blob/master/cmake/Helpers.cmake).

4. **Fix sockets in worker threads before claiming broad asyncio support.**
   Runtime ACCEPTANCE L2 records name lookup/socket failures in workers and
   explains the task-local bsdsocket base. A solution must cover socket, select,
   SSL and OpenSSL, including descriptor transfer/ownership and thread cleanup.
   Finish with a worker-thread HTTPS request, main/worker socket handoff,
   select wakeup, close/error paths and repeat-run checks. Mainline has a
   separate select-wakeup backlog and must not inherit ABIv11 conclusions.

5. **Turn the existing stdlib harness into a repeatable release gate.** The
   collected 2026-09-27 x64 run planned 492 test modules but left 425 unrun;
   it cannot be presented as a complete stdlib pass. Triage returned failures
   by root cause and documented platform limits. Keep one interpreter per
   module with host-side timeouts and recovery, and a small stable suite for
   each runtime/dev release. Start with import/path handling, threads, signals,
   sockets and embedding; broaden after recovering from crashes is reliable.

Evidence: `package/ACCEPTANCE.txt`, `patches/cpython/0023-*`,
`docs/evidence/dev-package-20261008/REPORT.md`, and the local collected run
`AROS-dev/aros-python3-evidence/stdlib-x64-20260927/run1/` (interpreter a072b8ad).
The old run includes 25 passing modules, 6 failed modules, 8 errors, 7 crashes,
19 skips and 1 timeout; it was incomplete and its stored state still labels
one entry running. These are historical results, not a new test run.

## Work to defer

A general dlopen/extension-loader project and compatibility with arbitrary
binary wheels would be a separate platform effort. Native process support
for subprocess/multiprocessing also needs its own design and probes; AROS
process APIs are not automatically a POSIX fork/exec replacement. Do not
add a large collection of optional modules before these core paths are stable.
Add smaller modules when a named application's needs justify them.

The main risk is spending effort on more importable modules while scripts can
still hang or crash the machine. Early indicators are recurring reboots during
the same tests and integrations that cannot progress past lifecycle failures.
The sequence above mitigates that by fixing the known thread defect and
interrupt/recovery path, using GemRB as a concrete consumer, then validating
networking and maintaining a measured release gate.
