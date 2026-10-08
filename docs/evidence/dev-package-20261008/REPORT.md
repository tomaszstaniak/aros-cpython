# Development package verification, 2026-10-08

Target: CPython 3.14.7, x86-64 AROS ABIv11, companion to runtime 0.1.0.
Compiler: GCC 10.5.0 from `AROS/toolchain`, SDK: ABIv11 2026.09
`SDK-202609/Development`. Package built in `AROS/local/cpython-dev-package`.

## Artifact and build identity

The source is the current repository's release patch series 0001-0022. Patch
0023, added after release, was reversed in the disposable build source only.
The versioned patch remains unchanged. All custom dependencies were rebuilt.
The stripped interpreter reproduced the release SHA-256 exactly:
`a072b8ad8c79dfa4106fbbfee7016e037e17d096e1bd27868ebb5124731e1203`.

Archives (both contain the same files):

| Archive | SHA-256 |
| --- | --- |
| `aros-cpython-3.14.7-abiv11-0.1.0-dev.tar.gz` | `46abfa4b48d711727fcd01c5851e725bbc6164f017c5b66bf72dc4d137171c0b` |
| `aros-cpython-3.14.7-abiv11-0.1.0-dev.zip` | `c49c625eb7850cee3b902c89e9235987e6474fbf8eb07959ffbbcc634237f48f` |

Repeated packaging produced byte-identical archives. Stripping archives uses
`-D --strip-debug`: without `-D`, binutils stamps the archive symbol index with
the current time even if the outer tar/ZIP metadata is fixed.

## Host checks

`python3 -m unittest discover -s tests -p 'test_*.py'` with `DEV_ARCHIVE`,
`AROS_TOOLCHAIN` and `AROS_SDK` set: four tests passed, no skips. See
`host-checks.log`. The checks cover missing-build errors, WORK configuration,
rejection of a stale interpreter after a library rebuild, unpacked SHA-256
manifest, identical ZIP/tar contents and absence of host paths in link config.
Both the CMake imported target and pkg-config flags compiled/linked the example
from a temporary relocated extraction; `x86_64-aros-nm -u` returned no symbols.

## Guest execution

Pool machine `v11-1`, AROS One 1.3, x86-64 ABIv11, QEMU TCG, 2 GiB. This is
the pool's older One installation, not the ABIv11 2026.09 base used for the
original runtime acceptance. The executable was built with the SDK above.
The guest used the unmodified 0.1.0 runtime stdlib from the release archive,
unpacked under `RAM:CPDEV1008B/Python`, assigned as `Python:`. Shell stack:
1 MiB. Example executable SHA-256:
`1df5e242d74489c397fa47758bd1fa597b990eed1088aa0543ed272805682a40`.

Two successive executions in the same Shell printed `EMBED PASS` and
`FINALIZE PASS`; the final run's recorded return code was 0. Evidence:
`cpdev-1008-run3.log` and `cpdev-1008-rc3.log`. Results were collected while
the machine was stopped, with the pool collector's source/destination hashes.
The machine was then released. Test input lived in RAM; no system files or
startup settings were changed.

The example tested isolated PyConfig initialization, a builtin C module
registered by the host, Python execution, JSON, Decimal, SHA-256, lzma/bz2/zlib
round trips, an in-memory SQLite query, SSL import/version, and Py_FinalizeEx.

The first example blocked on a missing-volume requester for `pyvenv.cfg`.
Root cause: embedding bypasses `Programs/python.c`, where our AROS executable
suppresses requesters. The example now saves `pr_WindowPtr`, sets it to -1
while Python runs, and restores it via atexit. This requirement is documented
for embedders; the release library itself remains unchanged.

## What this did not show

No GemRB compilation or execution, C++ host, foreign-thread/GIL calls,
subinterpreter lifecycle, TLS networking, signal interruption, memory-leak
measurement, native guest compiler, other architectures, or real hardware were
tested. Dynamic extension loading and all runtime 0.1.0 limitations remain.
Patch 0023's thread-ident correction is deliberately absent from this matching
companion and should be released with a matching future runtime package.

Published as additional assets of the existing v0.1.0 release on 2026-10-08:
https://github.com/tomaszstaniak/aros-cpython/releases/tag/v0.1.0
The runtime assets were preserved.
