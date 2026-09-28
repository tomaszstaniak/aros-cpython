# threadident.py - thread identity and thread bookkeeping on AROS.
# Checks, each printed as PASS/FAIL:
#   stable    a thread's ident is the same at start, middle and end, and
#             equals Thread.ident and the creator's handle ident
#   unique    threads alive at the same time (held at a barrier) have
#             different idents
#   churn     many short threads started and ended quickly: stable idents
#   reuse     threads started one after another with a pause, so that each
#             has ended (but is not joined yet) when the next one starts;
#             joined in batches. This is the case that exposed the ABIv0
#             pthread_self() bug; every thread's ident must stay its own
#   join      every join() returns and the thread is no longer alive
#   registry  afterwards threading knows only the main thread
#   rlock     an RLock held by one thread: another thread cannot acquire it
#             without blocking, and its release() raises RuntimeError;
#             re-entry by the owner works; no lost updates under contention
#   quiet     no exception reached threading.excepthook, sys.unraisablehook
#             or stderr ("Exception ignored", "Traceback") during the run
# Usage: python threadident.py [ROUNDS]
import io, sys, threading, _thread, time

ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 25
N = 16
CHURN = 1000

background = []
threading.excepthook = lambda a: background.append("excepthook: %r" % (a.exc_value,))
sys.unraisablehook = lambda u: background.append("unraisable: %r" % (u.exc_value,))
real_stderr = sys.stderr
sys.stderr = captured = io.StringIO()
results = {}

def report(name, ok, detail):
    results[name] = ok
    print("TI %-9s %s %s" % (name, "PASS" if ok else "FAIL", detail), flush=True)

def handle_ident(t):
    h = getattr(t, "_os_thread_handle", None)
    return getattr(h, "ident", None)

# stable + unique
bad_stable, bad_unique, checked = [], [], 0
main_ident = _thread.get_ident()
for r in range(ROUNDS):
    barrier = threading.Barrier(N + 1)
    rec = {}
    def work(i):
        a = _thread.get_ident()
        barrier.wait(30)
        b = _thread.get_ident()
        barrier.wait(30)
        sum(range(2000 * (i + 1)))
        c = _thread.get_ident()
        rec[i] = (a, b, c, threading.current_thread().ident)
    ts = [threading.Thread(target=work, args=(i,)) for i in range(N)]
    for t in ts: t.start()
    barrier.wait(30)                    # all N alive and past their first read
    alive = [t.ident for t in ts]
    barrier.wait(30)
    for t in ts: t.join(30)
    if len(set(alive)) != N or main_ident in alive:
        bad_unique.append((r, alive))
    for i, t in enumerate(ts):
        checked += 1
        a, b, c, cur = rec.get(i, (None,) * 4)
        if not (a == b == c == cur == t.ident == handle_ident(t)):
            bad_stable.append((r, i, a, b, c, cur, t.ident, handle_ident(t)))
report("stable", not bad_stable, "%d threads, %d mismatched %s" % (checked, len(bad_stable), bad_stable[:3]))
report("unique", not bad_unique, "%d rounds of %d live threads, %d with duplicates %s" % (ROUNDS, N, len(bad_unique), bad_unique[:1]))

# churn
bad_churn, not_joined = [], 0
def short(out):
    a = _thread.get_ident()
    out.append((a, _thread.get_ident(), threading.current_thread().ident))
t0 = time.time()
batch = []
for i in range(CHURN):
    out = []
    t = threading.Thread(target=short, args=(out,))
    t.start()
    batch.append((t, out))
    if len(batch) == 8:
        for t, out in batch:
            t.join(30)
            not_joined += t.is_alive()
            if not out or not (out[0][0] == out[0][1] == out[0][2] == t.ident):
                bad_churn.append((out, t.ident))
        batch = []
for t, out in batch:
    t.join(30); not_joined += t.is_alive()
report("churn", not bad_churn, "%d threads in %.3fs, %d mismatched %s" % (CHURN, time.time() - t0, len(bad_churn), bad_churn[:3]))
# reuse
bad_reuse, reuse_n = [], 0
def mark(out):
    a = _thread.get_ident()
    sum(range(20000))
    out.append((a, _thread.get_ident(), threading.current_thread().ident))
for r in range(ROUNDS * 2):
    batch = []
    for i in range(8):
        out = []
        t = threading.Thread(target=mark, args=(out,))
        t.start()
        batch.append((t, out))
        time.sleep(0.05)            # let this thread end before the next starts
    for t, out in batch:
        t.join(30); reuse_n += 1
        not_joined += t.is_alive()
        if not out or not (out[0][0] == out[0][1] == out[0][2] == t.ident == handle_ident(t)):
            bad_reuse.append((out, t.ident, handle_ident(t)))
report("reuse", not bad_reuse, "%d threads, %d mismatched %s" % (reuse_n, len(bad_reuse), bad_reuse[:3]))
report("join", not_joined == 0, "%d threads still alive after join" % not_joined)

# registry
others = [t for t in threading.enumerate() if t is not threading.main_thread()]
extra = [k for k in threading._active if k != main_ident]
report("registry", not others and not extra and threading.main_thread().ident == main_ident == _thread.get_ident(),
       "enumerate others %d, _active extra keys %s, main %s/%s" % (len(others), extra[:5], threading.main_thread().ident, main_ident))

# rlock
problems = []
rl = threading.RLock()
held, go = threading.Event(), threading.Event()
def owner():
    rl.acquire(); rl.acquire()          # re-entry
    held.set(); go.wait(30)
    rl.release(); rl.release()
def intruder():
    if rl.acquire(blocking=False):
        problems.append("second thread acquired a held RLock"); rl.release()
    try:
        rl.release()
        problems.append("release() by a non-owner did not raise")
    except RuntimeError:
        pass
to = threading.Thread(target=owner); to.start(); held.wait(30)
ti = threading.Thread(target=intruder); ti.start(); ti.join(30)
go.set(); to.join(30)
if not rl.acquire(blocking=False):
    problems.append("RLock not free after the owner released it")
else:
    rl.release()
counter = [0]
def bump():
    for _ in range(3000):
        with rl:
            with rl:
                v = counter[0]; counter[0] = v + 1
ts = [threading.Thread(target=bump) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join(60)
if counter[0] != 8 * 3000:
    problems.append("lost updates: %d of %d" % (counter[0], 8 * 3000))
report("rlock", not problems, "; ".join(problems) or "exclusion, re-entry and non-owner release as expected")

sys.stderr = real_stderr
text = captured.getvalue()
noisy = [l for l in text.splitlines() if "Exception ignored" in l or "Traceback" in l]
report("quiet", not background and not noisy, "%d hook events %s, %d stderr lines %s" % (len(background), background[:3], len(noisy), noisy[:3]))
print("TI-END %d/%d" % (sum(results.values()), len(results)), flush=True)
