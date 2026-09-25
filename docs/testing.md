# Testing

## On AROS

The results of release 0.1.0 are in
[package/ACCEPTANCE.txt](../package/ACCEPTANCE.txt): an install from the
package as its README describes, on a fresh ABIv11 2026.09 system in QEMU,
then the full test run twice, the second time after a restart.

### Package self-tests

Shipped in the package, run after installing:

| Command | Expected on ABIv11 |
|---|---|
| `python /Python/tests/wheel-test.py` | `SUMMARY 6 checks passed, 0 failed` |
| `python /Python/tests/install-test.py` | `SUMMARY 4/6 PASS`; the two failures are L2 |

### Full test run

`tests/guest` holds the scripts. Copy the directory to `SYS:pytest`, then in
a Shell:

```
Assign PYTEST: SYS:pytest
Execute PYTEST:suite-A
```

where `suite-A` was made on the host with `tests/guest/mksuite.sh A`. Each
test writes `RAM:A-<name>.txt`, ending with `RUN11-EXIT` and the exit code.

| Script | What it checks | Result file |
|---|---|---|
| `idprobe.py` | `sys.platform`, sysconfig identifiers, pip tags, `ENV:ABI`, SHA-256 of the interpreter | `A-id` |
| `imports11.py` | imports every standard library module; lists those that fail | `A-imp` |
| `probe11.py` | files and JSON, stat, pwd, urandom, zlib, bz2, lzma, HTTPS, pip, a socket in a worker thread | `A-p11` |
| `compress11.py` | zlib, gzip, bz2, lzma, zipfile and tarfile round trips | `A-z` |
| `https11.py` | two HTTPS sites, and three that must be refused (expired, wrong host, self-signed) | `A-h` |
| `threads11.py` | threads with a lock, a queue, a thread pool, a timer | `A-t` |
| `limits.py` | how unsupported features fail (subprocess, popen, multiprocessing, ctypes, pip on an sdist) | `A-lim` |
| `conc11.py` | two interpreters at once, one started with `Run` | `A-c1`, `A-c2` |
| eight `python -c` runs | repeated runs in one Shell | `A-r1` to `A-r8` |

Not in the suite, run by hand:

| Script | Purpose |
|---|---|
| `endmode.py wait` | L1: press Ctrl-C, or `Break <n> C` from another Shell; the script keeps running |
| `ident11.py` | thread identifiers, lock ownership, and L2 (line `WS`: a socket in a worker thread) |
| `net11.py` | socket calls one by one, for diagnosing network failures |

### C reproducers

`tests/c`: see [platform-notes.md](platform-notes.md).

## Rebuild checks

- Two builds from fresh clones in different directories gave the same
  interpreter (`6cdd0f60...`) and byte-identical archives.
- The release binary was compared with the build used in the earlier test
  runs (made from the same patches in a development tree, with different
  build paths and time stamp) using `scripts/compare-binaries.py`, which
  compares every function and data object by name and masks the bytes that
  relocations fill in: 28269 of 28270 symbols are equal; the one that
  differs is `Py_GetBuildInfo`, which returns the version stamp. As
  controls, two development builds with the same code gave 28270 of 28270,
  and a build from before the socket, tm_zone and thread ident patches gave
  745 differences.
