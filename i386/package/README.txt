CPython 3.14.7 for AROS i386 ABIv0 - 0.1.0 preview
===================================================

Python 3.14.7 for 32-bit AROS with the ABIv0 system interface: the deadwood2
ABIv0 releases for i386 and distributions built on them. It does not run on
ABIv11 (64-bit) or on mainline AROS nightlies; binaries of different ABIs
are not interchangeable. The x86_64 ABIv11 build is a separate package.

This is a preview for testers and for running scripts. Install it on a
separate (virtual) machine, not on a system you depend on. Work on the port
continues.

Measured on a clean ABIv0 20250313-1 installation in QEMU (ACCEPTANCE.txt):

WORKS                                    DOES NOT WORK (YET)
  files and JSON                           sockets outside the main thread (L2)
  180 of 205 stdlib modules checked by     starting processes: subprocess,
    the import probe import (importing       os.popen, multiprocessing (L3)
    does not show that all of a module     ctypes, mmap, curses, readline, dbm,
    works)                                   tkinter, termios, tty, pty,
  zlib, gzip, bz2, lzma, zip, tar            sqlite3 (L4)
  HTTPS with certificate verification      pip: source distributions (L5)
  threads, locks, queues, thread pools
  pip: installing pure-Python wheels     Ctrl-C and Break (L1)
  several interpreters at once
  many runs in one Shell

Inside: the interpreter (statically linked, one file), the pure-Python
standard library, OpenSSL 4.0.1 with a CA bundle, liblzma, pip 26.2.1, two
demos and two self-tests. Nothing in the archive replaces an AROS system file.


WHAT YOUR AROS NEEDS
--------------------
1. The ABIv0 20250313-1 release for i386 (deadwood2/AROS, tag
   ABIv0_20250313-1) INSTALLED ON A HARD DISK, so that SYS: and C: are
   writable. That is the system this package was tested on. Other ABIv0
   systems were not tested.
2. A program that unpacks LhA archives, for example lha from the release's
   contrib archive (AROS-20250313-1-any-i386-contrib, Extras/Misc/aminet/C)
   or from your distribution. A bare installation from the release ISO has
   no unpacker.
3. bsdsocket.library (AROSTCP), which the interpreter opens. zlib and bzip2
   are linked into the interpreter on this platform; z1.library and
   bz2.library are not needed.
4. AROSTCP running, with a working network route and DNS, BEFORE python
   starts. The interpreter opens bsdsocket.library at startup even for
   offline scripts. A fresh installation does not start the network. Set
   it up once in SYS:Prefs/Network: Add an interface, choose the device for
   your network card (e1000.device for the QEMU e1000 card; the default is
   pcnet32.device), keep IP Mode Automatic (DHCP), Apply, tick "Start
   networking during system boot", Save, and reboot.


INSTALL
-------
On the host computer:
  1. Bring aros-cpython-3.14.7-abiv0-0.1.0.lha to AROS (CD image, FAT
     share, network). Only the archive's own name may change on the way;
     do not copy the unpacked files from a CD image (ISO 9660 changes the
     file names, and the standard library can then not be imported).

In an AROS Shell (SYS:Python must not exist yet):
  2. MakeDir RAM:pkg
     lha >RAM:lha-log xw=RAM:pkg <path to>/aros-cpython-3.14.7-abiv0-0.1.0.lha
     (the syntax of the lha in the release's contrib archive, LHa for UNIX
     1.00; other LhA programs take "x archive RAM:pkg/"). Keep the
     redirection: printing about 1000 file names slows the console down.
  3. Copy RAM:pkg/aros-cpython-3.14.7-abiv0-0.1.0/Python SYS:Python ALL CLONE
  4. Protect SYS:Python/python +e
  5. Copy SYS:Python/S/python C:python
     Protect C:python +s
  6. Type >>S:User-Startup SYS:Python/S/python-startup
     This adds "Assign Python: SYS:Python", which is how the interpreter
     finds its standard library.
  7. Reboot.


CHECK THE INSTALL
-----------------
After the reboot, in a new Shell, once the network is up:

  python -c "import sys; print(sys.version)"
      expect: 3.14.7 (main, Sep 25 2026, 00:00:00) [GCC 6.5.0]
  python /Python/tests/wheel-test.py
      expect: SUMMARY 6 checks passed, 0 failed
      pip also prints a warning that /home/.cache/pip is not writable and
      two DEPRECATION notes about the test importing pyfiglet; none of them
      affects the result.
  python /Python/tests/install-test.py
      expect: SUMMARY 4/6 PASS. The two checks that fail use a socket in a
      thread other than the main one (L2). Its "zlib (system z1.library)"
      label is written for x86_64; on i386 zlib is linked in.

At startup python prints
  Could not find platform dependent libraries <exec_prefix>
That is expected: all extension modules are built in.


KNOWN LIMITS
------------
Measured on the test system; details in ACCEPTANCE.txt.
  L1  A running script cannot be interrupted: Ctrl-C and `Break <n> C` do
      not stop it. A script that does not end by itself needs a reboot.
  L2  Sockets work only in the main thread. In any other thread, name
      lookup fails (gaierror "getaddrinfo failed") and socket() fails with
      OSError errno 0.
  L3  No subprocess and no os.popen: they raise OSError "aros does not
      support processes". os.system works. multiprocessing does not.
  L4  Missing modules (not built, not replaced by stand-ins): ctypes, mmap,
      curses, readline, dbm, tkinter, termios/tty/pty, resource, syslog,
      _uuid (uuid itself works), _zstd, sqlite3, and the Windows-only ones.
  L5  pip installs pure-Python wheels; source distributions need
      subprocess. The bundled pip carries a small change so that it loads
      without mmap (pip-26.2.1-without-mmap.diff in this folder).
  L11 python needs AROSTCP running when it starts.
  L14 ABIv0's pthread_self() can name another thread (a system bug, fixed
      in ABIv11). This interpreter does not rely on it for Python threads.
  L15 ABIv0's unsetenv() returns garbage. This interpreter ignores it, so
      del os.environ[...] works, but os.unsetenv() cannot report errors.
  L16 Some ABIv0 C library calls fail without an error code; Python then
      reports OSError errno 0 ("Error").
  Lib/test (CPython's own test suite) does not pass as a whole; one pass
  is summarised in ACCEPTANCE.txt, section D.
  Not checked on i386: python -u and network readiness over many boots. On
  x86_64, -u disturbs the Shell's output afterwards; the launcher does not
  use it.
  Random numbers (os.urandom, secrets, ssl) come from OpenSSL, seeded from
  CPU timing jitter (jitterentropy): ABIv0 has no operating system entropy
  source.
  Tested environment: QEMU with KVM, 2 GB, one installation of the ABIv0
  20250313-1 release. Not tested on real hardware.


REPORTING A PROBLEM
-------------------
Include: the AROS system and version (the Version command), emulator or
hardware, the output of  python -c "import sys; print(sys.version)" , the
exact command, and the full text of any error or crash requester.
