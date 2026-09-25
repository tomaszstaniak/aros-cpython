CPython 3.14.7 for AROS x86_64 ABIv11 - 0.1.0 preview
=====================================================

Python 3.14.7 for 64-bit AROS with the ABIv11 system interface: the ABIv11
releases (deadwood2/AROS) and distributions built on them. It does not run on
mainline AROS nightlies (ABIv1); binaries of the two ABIs are not
interchangeable.

This first published version is for testers and for running scripts. Three
limits matter most, see KNOWN LIMITS:
  L1   a running script cannot be interrupted (Ctrl-C, Break)
  L2   sockets work only in the main thread
  L12  the network is not always ready after a boot; a restart clears it
Install it on a separate (virtual) machine, not on a system you depend on.
Work on the port continues.

WORKS                                    DOES NOT WORK (YET)
  files and JSON                           Ctrl-C and Break (L1)
  182 of 205 stdlib modules checked by     sockets outside the main thread (L2)
    the import probe import (importing     starting processes: subprocess,
    does not show that all of a module       os.popen, multiprocessing
    works)                                 ctypes, mmap, curses, readline, dbm,
  zlib, gzip, bz2, lzma, zip, tar            tkinter, termios, tty, pty
  HTTPS with certificate verification      pip: source distributions
  threads, locks, queues, thread pools     loading additional native C/C++
  pip: installing pure-Python wheels         extension modules (the built-in
  several interpreters at once               ones, such as ssl and the
  many runs in one Shell                     compression modules, work)

Inside: the interpreter (statically linked, one file), the pure-Python
standard library, OpenSSL 4.0.1 with a CA bundle, liblzma, pip 26.2.1, two
demos and two self-tests. Nothing in the archive replaces an AROS system file.


WHAT YOUR AROS NEEDS
--------------------
1. The ABIv11 2026.09 release for x86_64 (deadwood2/AROS, tag ABIv11_2026.09)
   INSTALLED ON A HARD DISK, so that SYS: and C: are writable. That is the
   system this package was tested on (Kickstart 51.51; os.uname() reports
   release 12.1, built Sep 3 2026). Older ABIv11 systems, including earlier
   AROS One releases, were not tested.
2. The system libraries the interpreter opens: z1.library (zlib, gzip),
   bz2.library (bz2) and bsdsocket.library (AROSTCP). The tested system has
   all three.
3. AROSTCP running, with a working network route and DNS, BEFORE python
   starts. The interpreter opens bsdsocket.library at startup even for
   offline scripts; without it, it stops with the requester "Unable to open
   bsdsocket.library version 4 or later". A fresh ABIv11 2026.09
   installation does not start the network. Set it up once in
   SYS:Prefs/Network: Add an interface, choose the device for your network
   card (e1000.device for the QEMU e1000 card; the default is
   pcnet32.device), keep IP Mode Automatic (DHCP), Apply, tick "Start
   networking during system boot", Save, and reboot.


INSTALL
-------
Tested way: a ZIP file with the Python directory, unpacked on AROS with an
UnZip for ABIv11 in C:. The test machine had one; whether a fresh ABIv11
2026.09 installation includes UnZip was not checked. Copying the unpacked
files from a CD image does not work (ISO 9660 changes the file names, and the
standard library can then not be imported). The ZIP itself can come from a CD
image: only the ZIP's own name changes there.

On the host computer:
  1. Unpack the archive:
       tar -xzf aros-cpython-3.14.7-abiv11-0.1.0.tar.gz
     This gives aros-cpython-3.14.7-abiv11-0.1.0/ with the Python/ directory
     inside. The .lha has the same content.
  2. Make a ZIP that contains the Python directory, for example
       cd aros-cpython-3.14.7-abiv11-0.1.0 && zip -r -X ../python-abiv11.zip Python
     and bring it to AROS (CD image, FAT share, network).

In an AROS Shell (SYS:Python must not exist yet):
  3. UnZip >RAM:unzip-log <path to>/python-abiv11.zip -d RAM:pkg
     Keep the redirection: UnZip's interactive screen query does not work in
     the AROS console. Check RAM:unzip-log afterwards.
  4. Copy RAM:pkg/Python SYS:Python ALL CLONE
  5. Protect SYS:Python/python +e
  6. Copy SYS:Python/S/python C:python
     Protect C:python +s
  7. Type >>S:User-Startup SYS:Python/S/python-startup
     This adds "Assign Python: SYS:Python", which is how the interpreter
     finds its standard library.
  8. Reboot.


CHECK THE INSTALL
-----------------
After the reboot, in a new Shell, once the network is up. AROSTCP and its
DHCP client start a little after the desktop appears; a python started
before that stops with the requester "Unable to open bsdsocket.library
version 4 or later". Click "Exit python", wait a moment and start it again.

  python -c "import sys; print(sys.version)"
      expect: 3.14.7 (main, Sep 25 2026, 00:00:00) [GCC 10.5.0]
  python /Python/tests/wheel-test.py
      expect: SUMMARY 6 checks passed, 0 failed
      pip also prints a warning that /home/.cache/pip is not writable and
      that its cache is disabled, and two DEPRECATION notes from pip about
      the test importing pyfiglet; none of them affects the result.
  python /Python/tests/install-test.py
      expect: SUMMARY 4/6 PASS. The two checks that fail,
      "single-thread HTTP x3" and "worker socket error -> ENOTCONN", both
      use a socket in a thread other than the main one, which this build
      does not support yet (see KNOWN LIMITS).

install-test checks the interpreter, files and JSON, zlib through
z1.library, HTTPS with certificate and host name verification against the
shipped CA bundle, a local HTTP server and a socket in a worker thread.
wheel-test installs the bundled pure-Python wheel (pyfiglet) with pip into a
fresh directory, imports it from there, runs it and cleans up.

At startup python may print
  Could not find platform dependent libraries <exec_prefix>
That is expected: all extension modules are built in, so there is no
lib-dynload directory.


USING IT
--------
  python                           interactive prompt
  python /RAM/script.py            paths are Unix-style: /RAM/... is RAM:...,
                                   /Python/... is Python:...
  python /Python/demo/https_verify.py
  python /Python/demo/json_files.py
  python -m pip install --no-index --no-build-isolation \
      --target /RAM/pkgs <wheel file>
  Copy RAM:pkgs SYS:Python/lib/python3.14/site-packages ALL CLONE
      (pip cannot install straight into SYS:Python, see KNOWN LIMITS)
  python -c "import json; print(json.dumps({'a': [1, 2]}))"
  python -c "import urllib.request as u; print(u.urlopen('https://www.python.org').status)"

Not possible yet:
  stopping a running script with Ctrl-C (L1); reboot instead
  a socket or HTTPS request in a worker thread (L2)
  python -c "import subprocess; subprocess.run(['Echo', 'hi'])"
      OSError: aros does not support processes
  python -c "import ctypes"
      ModuleNotFoundError: No module named '_ctypes'

The launcher C:python sets a 16 MB stack and SSL_CERT_FILE, then runs
Python:python. Run the interpreter through it.


KNOWN LIMITS
------------
Measured on the test system; details and how each was measured are in
ACCEPTANCE.txt.
  - A running script cannot be interrupted: Ctrl-C and `Break <n> C` do not
    stop it. A script that does not end by itself leaves you with a reboot.
  - Sockets work only in the main thread. In any other thread, name lookup
    fails (gaierror "getaddrinfo failed") and socket() fails with OSError
    errno 0: bsdsocket.library hands out one library base per task, and this
    build uses the main task's for every thread.
  - No subprocess and no os.popen: they raise OSError "aros does not support
    processes". os.system works. multiprocessing does not.
  - Missing modules (not built, and not replaced by stand-ins): ctypes, mmap,
    curses, readline, dbm, tkinter, termios/tty/pty, resource, syslog, _uuid
    (the uuid module itself works), _zstd (compression.zstd), and the
    Windows-only ones. pip cannot build or install source distributions
    (they need subprocess); pure-Python wheels install.
  - The bundled pip carries a small change so that it loads without the mmap
    module: pip-26.2.1-without-mmap.diff in this folder shows it.
  - locale.gettext() and the other C-level gettext functions are not
    available; the gettext module works.
  - time.localtime() has an empty tm_zone: the C library leaves it unset.
  - Do not run python with -u. On ABIv11 it leaves the Shell's own output
    unbuffered after python exits, and the Shell prompt's colour codes then
    appear as text until you open a new Shell. The launcher does not use -u.
  - Random numbers (os.urandom, secrets, ssl) come from OpenSSL, seeded from
    CPU timing jitter (jitterentropy), because ABIv11 has no operating
    system entropy source.
  - time_t is 32 bits in this C library: times after 2038-01-19 03:14:07
    UTC cannot be represented.
  - L12: in 2 of 10 test boots with a correct network configuration, the
    network failed for the whole boot: once name lookup failed for every
    host, once the network stack did not start at all (a C program could
    not open bsdsocket.library either). A restart cleared it both times.
    Check with a simple lookup before longer work, for example
      python -c "import socket; print(socket.gethostbyname('example.com'))"
  - L13: os.stat().st_flags holds no meaningful value (the C library leaves
    it unset), and shutil.move() of a directory from one volume to another
    can then fail with PermissionError. This is why pip --target must point
    to a directory on RAM: (where pip keeps its temporary files); copy the
    result with the AmigaDOS Copy command.
  - Tested environment: QEMU (software emulation, x86_64), 2 GB, on one
    installation of the ABIv11 2026.09 release. Not tested on real hardware.


REPORTING A PROBLEM
-------------------
Include: the AROS system and version (the Version command), emulator or
hardware, the output of  python -c "import sys; print(sys.version)" , the
exact command, and the full text of any error or crash requester.
