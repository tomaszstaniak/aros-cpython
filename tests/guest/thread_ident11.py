"""Exercise patch 0023 without depending on asyncio or network setup."""
import errno
import faulthandler
import os
import signal
import sys
import threading
import time

print('THREAD-IDENT START', sys.version, flush=True)
filename = '/RAM/thread-ident-dump.txt'
for cycle in range(8):
    barrier = threading.Barrier(5, timeout=30)
    release = threading.Event()
    identities = []
    lock = threading.Lock()

    def waiting_worker():
        with lock:
            identities.append(threading.get_ident())
        barrier.wait()
        release.wait(60)

    workers = [threading.Thread(target=waiting_worker, name='ident-%d-%d' % (cycle, i))
               for i in range(4)]
    for worker in workers:
        worker.start()
    barrier.wait()
    try:
        assert len(set(identities + [threading.get_ident()])) == 5
        assert all(ident > 0 for ident in identities)
        with open(filename, 'wb') as output:
            faulthandler.dump_traceback(file=output, all_threads=True)
        dump = open(filename, 'rb').read()
        assert dump.count(b'waiting_worker') == 4, dump
        assert b'thread_ident11.py' in dump
        print('PASS dump cycle', cycle, 'workers', len(identities), flush=True)
    finally:
        release.set()
        for worker in workers:
            worker.join(30)
        assert not any(worker.is_alive() for worker in workers)

# ABIv11's pthread_kill is an EINVAL stub. This checks the call completes,
# not signal delivery or which pthread identifier reached the stub.
try:
    signal.pthread_kill(threading.get_ident(), 0)
except OSError as error:
    assert error.errno == errno.EINVAL, error
    print('LIMIT pthread_kill: SDK stub returns EINVAL', flush=True)
else:
    raise AssertionError('unexpected pthread_kill behavior; investigate SDK')

if hasattr(time, 'pthread_getcpuclockid'):
    print('SKIP pthread_getcpuclockid: no guest clock regression added', flush=True)
else:
    print('LIMIT pthread_getcpuclockid: API not built on this target', flush=True)
os.remove(filename)
print('THREAD-IDENT PASS: 8 cycles, 32 workers, 8 all-thread dumps', flush=True)
