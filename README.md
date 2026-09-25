# CPython for AROS x86_64 ABIv11

CPython 3.14.7 cross-compiled for 64-bit AROS with the ABIv11 system
interface (the ABIv11 releases of deadwood2/AROS and systems built on them).
You run `python` and write ordinary Python code. This repository holds
everything needed to rebuild it: the patches, build scripts, package files,
tests and the reproducers for the platform problems found on the way.

**0.1.0 preview** is the first version, for testers and for running
scripts. **The binary release is still being prepared**; until it is
published, build from source (see below). Three limits matter most:

- **L1: a running script cannot be interrupted.** Ctrl-C and `Break` do not
  stop it. A script that does not end by itself needs a reboot.
- **L2: sockets work only in the main thread.** In any other thread, name
  lookup and `socket()` fail.
- **L12: the network is not always ready after a boot.** In 2 of 10 test boots with a correct network
  configuration, network access failed. Once, name lookup failed for every
  host for the whole boot. Once, checked 150 s after the boot, the network
  stack was not available (a C program could not open `bsdsocket.library`
  either); whether it would have started later was not established. A
  restart cleared it both times. The two cases were measured differently
  and are not known to share a cause.

Work on the port continues; see [Further work](#further-work).

## What works and what does not

Measured on the ABIv11 2026.09 release in QEMU; details in
[package/ACCEPTANCE.txt](package/ACCEPTANCE.txt).

| Works | Does not work |
|---|---|
| Files and JSON | Interrupting a script with Ctrl-C or `Break` (L1) |
| 182 of the 205 standard library modules checked by the import probe import (importing a module does not show that all of it works) | Sockets outside the main thread (L2) |
| zlib, gzip, bz2, lzma, zipfile, tarfile | Starting processes: `subprocess`, `os.popen`, `multiprocessing` (this port has no way to create processes) |
| HTTPS with certificate and host name verification | `ctypes`, `mmap`, `curses`, `readline`, `dbm`, `tkinter`, `termios`, `tty`, `pty` |
| Threads, locks, queues, thread pools, timers | pip installing source distributions |
| pip installing pure-Python wheels (into a directory on `RAM:`; see L13) | Loading additional native C/C++ extension modules (the built-in ones, such as `ssl` and the compression modules, work) |
| Several interpreters at the same time | `locale.gettext()` and the other C-level gettext functions |
| Many runs in one Shell | |
| `os.system` | |

Self-tests shipped in the package: `wheel-test.py` passes 6 of 6;
`install-test.py` passes 4 of 6, and the two failing checks are L2.

## Examples

What works, in an AROS Shell (paths are Unix-style: `/RAM/x` is `RAM:x`,
`/Python/...` is `Python:...`):

```
python -c "import sys; print(sys.version)"
python /RAM/script.py
python -c "import json; print(json.dumps({'a': [1, 2]}))"
python -c "import zipfile; z = zipfile.ZipFile('/RAM/a.zip', 'w'); z.writestr('x.txt', 'hi'); z.close()"
python -c "import urllib.request as u; print(u.urlopen('https://www.python.org').status)"
python -c "import threading; t = threading.Thread(target=print, args=('hi',)); t.start(); t.join()"
python -m pip install --no-index --no-build-isolation --target /RAM/pkgs /RAM/some_package-1.0-py3-none-any.whl
Copy RAM:pkgs SYS:Python/lib/python3.14/site-packages ALL CLONE
```

What does not work yet:

```
python /RAM/endless.py              # Ctrl-C does not stop it (L1)
# a socket or an HTTPS request in a worker thread fails (L2)
python -c "import subprocess; subprocess.run(['Echo', 'hi'])"
                                    # OSError: aros does not support processes
python -c "import ctypes"           # ModuleNotFoundError: No module named '_ctypes'
python -m pip install /RAM/some-package-1.0.tar.gz
                                    # source distributions need subprocess
python -m pip install --target /Python/lib/python3.14/site-packages some.whl
                                    # PermissionError: a directory cannot be
                                    # moved between volumes (L13)
```

## Requirements on AROS

- The ABIv11 2026.09 release for x86_64 (tag `ABIv11_2026.09`), installed on
  a hard disk. Other ABIv11 systems, including earlier AROS One releases, are
  not tested.
- `z1.library`, `bz2.library` and AROSTCP (`bsdsocket.library`), all part of
  that release.
- The network running before python starts: the interpreter opens
  `bsdsocket.library` at startup.

It does not run on mainline AROS (ABIv1).

## Install

Download the release archive, then follow `README.txt` inside it
([package/README.txt](package/README.txt)): unpack on the host, zip the
`Python` directory, unpack it on AROS with UnZip, copy it to `SYS:Python`,
install the launcher and reboot.

## Build from source

See [docs/building.md](docs/building.md). In short, with the ABIv11 GCC
10.5.0 cross compiler in `$AROS_TOOLCHAIN` and a host Python 3.14:

```sh
scripts/fetch-sources.sh      # downloads, checked by SHA-256 (sources.txt)
scripts/prepare-source.sh     # CPython 3.14.7 + patches/cpython
scripts/build-deps.sh         # static OpenSSL, jitterentropy, liblzma
scripts/configure.sh
scripts/build.sh
scripts/build-package.sh      # archives in work/dist
```

## Repository

| Path | Contents |
|---|---|
| `patches/cpython/` | 22 patches on CPython 3.14.7, one change each, with the reason in the message |
| `patches/*.diff` | OpenSSL 4.0.1, jitterentropy 3.7.0, and pip 26.2.1 (loading without `mmap`) |
| `config/config.site` | answers for cross-configure, each with its reason |
| `scripts/` | environment, download, build and packaging |
| `package/` | launcher, README, ACCEPTANCE, third-party notices and licenses |
| `tests/guest/` | the test scripts run on AROS |
| `tests/c/` | small C programs that reproduce the platform problems |
| `docs/` | building, testing, platform notes |

## Further work

- **L1, interruption.** The interpreter has to turn the task's break signal
  into `KeyboardInterrupt` where it checks for pending signals, and
  `time.sleep` has to wait for the break signal as well. This belongs in the
  interpreter and does not depend on terminal support.
- **L2, sockets in threads.** `bsdsocket.library` gives each task its own
  library base and refuses calls through another task's base. The socket,
  select and ssl modules, and OpenSSL's socket I/O, need a base per thread.
- **Terminal support with the upcoming AROS terminal (aros-xterm).**
  `termios` is disabled because the ABIv11 C library has `tcgetattr` and
  `tcsetattr` but not `tcsendbreak`, `tcdrain`, `tcflush` and `tcflow`.
  aros-xterm implements equivalents of the last three, besides getting and
  setting attributes, but on AROS DOS handles, while Python uses numeric file
  descriptors; the existing bridge between the two has limits in handle
  lifetime, concurrency and I/O readiness. The plan is a joint review
  starting with `termios` and `tty`; `pty` comes later, as it also depends on
  starting processes. A working `NewShell WINDOW XTERM:` on ABIv11 is not yet
  a tested POSIX PTY.
- **More testing:** other ABIv11 systems (AROS One), real hardware, longer
  runs, and more third-party pure-Python packages.

## Platform notes

Problems in the ABIv11 system that this port works around, each with a
reproducer: [docs/platform-notes.md](docs/platform-notes.md).

## License and credits

The files in this repository are under the BSD 3-Clause License
([LICENSE](LICENSE)). The patches in `patches/cpython/` modify CPython and
are offered under CPython's license (PSF License Agreement), like the code
they change. The package contains third-party components under their own
licenses; see [package/THIRD-PARTY-NOTICES.txt](package/THIRD-PARTY-NOTICES.txt)
and [package/licenses/](package/licenses/).

Built on the work of the Python Software Foundation and the CPython
developers, the OpenSSL project, Stephan Mueller (jitterentropy), the Tukaani
project (xz), the SQLite developers, the Expat developers, Stefan Krah
(mpdecimal), the HACL* authors, the pip maintainers, the curl project (CA
bundle), and the AROS Development Team and deadwood2 (ABIv11 releases, SDK
and toolchain).
