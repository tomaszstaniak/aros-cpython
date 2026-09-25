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
  interpreter (`a072b8ad...`) and byte-identical archives.
- `scripts/compare-binaries.py` compares two executables function by
  function and data object by data object, masking the bytes that
  relocations fill in. Against the previous candidate (`6cdd0f60...`,
  before the L13 fix) it reports differences only in the `posix` module's
  stat code (33 symbols, all in `Modules/posixmodule.c`), the expected
  effect of dropping `st_flags`. That candidate in turn equalled the
  development build used in the earliest test runs in 28269 of 28270
  symbols, all but the version stamp. As controls, two development builds
  with the same code gave 28270 of 28270, and a build from before the
  socket, tm_zone and thread ident patches gave 745 differences.

## L13 before and after

`tests/guest/l13move.py` checks the cause directly (on plain directories
`st_flags` must be absent or 0, in 1000 `stat()` calls) and then moves a
directory from RAM: to SYS: and installs a wheel with pip into a target on
SYS: and imports it from there. With the previous candidate the first check
failed (4 different leftover values); the other two passed in that run, as
the failure depended on the leftover value. With this release all three
pass.
