# ABIv11 platform notes

Behaviour of the ABIv11 2026.09 system that this port had to work around.
Each was measured on that system; the reproducers are in `tests/c` and
`tests/guest`. Build a C reproducer with
`aros-v11-gcc -std=gnu11 -nix x.c -o x` (add `-lpthread`, `-lnet` or
`-llzma` where noted).

| Problem | Reproducer | Effect on CPython | Handled in |
|---|---|---|---|
| `SSIZE_MAX` is `_POSIX_SSIZE_MAX` (32767) while `ssize_t` is a 64-bit `long` | `ssizemax.c` | every allocation over 32 KiB failed; startup ended in MemoryError | patch 0016 |
| `wcstombs()` does not write the terminating NUL when there is room | `wcsnul.c` | `fopen()` got a garbage mode string | patch 0014 |
| `localtime()` and `gmtime()` leave `tm_zone` NULL | `tmprobe.c` | `time.localtime()` crashed in `strlen()` | patch 0018 |
| socket numbers start at 0 and share the numbers of C library files; `close()`, `ioctl()`, `fcntl()` on a socket act on the file | `sockprobe.c` (`-lnet`) | the first socket was fd 0; closing it would close stdin | patch 0020, OpenSSL patch |
| `socket()` rejects `SOCK_CLOEXEC` with errno 43, not EINVAL | `sockprobe.c` | no socket could be created | patch 0020 |
| the socket calls are inline functions in `<proto/socket.h>` | configure log | configure found no `socket()` and the module used stubs | `config/config.site` |
| the main thread's pthread number is 0 | `ident11.py` | recursive locks held by the main thread looked free; pip and thread pools failed | patch 0021 |
| each task needs its own `bsdsocket.library` base | `ident11.py` (line `WS`) | sockets fail in worker threads | open, L2 |
| the break signal is not delivered as a POSIX signal | `endmode.py wait` | Ctrl-C does not interrupt a script | open, L1 |
| the system xz library decodes only: no encoder, no check other than NONE | `lzmaprobe.c` (`-llzma`) | `lzma.compress()` failed | static liblzma |
| `setvbuf(stdout, NULL, _IONBF, 0)` leaves the calling Shell's own output handle unbuffered after the program exits; escape sequences then arrive in pieces and print as text | `constate.c V` (`-lpthread`), then `Echo "*E[1mX"` | `python -u` broke the Shell prompt | launcher without `-u` |
| no `getentropy()`, `getrandom()` or random device | none needed | no OS entropy for `os.urandom` | jitterentropy seeds OpenSSL (OpenSSL patch); os.urandom uses OpenSSL (patch 0012) |
| `ioctl(FIOCLEX)` on a file fails with ENOSYS and returns 14, not -1 | `fdprobe.c` | `set_inheritable()` failed | patch 0015 |
| `sysconf(_SC_CLK_TCK)` fails | `fdprobe.c` | `os.times()` failed | patch 0015 |
| no `fork()` or `execve()` | none | no subprocess | patch 0019 (import works, `Popen` raises OSError) |
| sendmsg exists but `SC_IOV_MAX` is not a sysconf name | none | `import asyncio` raised ValueError | patch 0022 |
| `stat()` leaves `st_flags` unset (garbage, for example `0x4bcaa880`) | `python -c "import os; print(hex(os.stat('/RAM').st_flags))"` | `shutil.move()` of a directory between volumes could fail with PermissionError whenever the leftover value equalled an immutable flag, and with it `pip install --target` outside RAM: (intermittent) | `config/config.site` (L13, fixed in 0.1.0: `st_flags` not reported) |

Checked and found correct, so ruled out as causes: POSIX semaphores
(`semprobe.c`, `-lpthread`) and `_Thread_local` variables (`tlsprobe.c`,
`-lpthread`).
