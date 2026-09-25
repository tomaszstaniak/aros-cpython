# threads11.py - threads, locks, queues and a thread pool on one interpreter.
import threading, queue, time, concurrent.futures as cf
res = []
lock = threading.Lock()
def work(i):
    s = sum(range(20000 * (i + 1)))
    with lock:
        res.append(i)
    return s
ts = [threading.Thread(target=work, args=(i,)) for i in range(8)]
t0 = time.time()
[t.start() for t in ts]; [t.join(60) for t in ts]
print("T threads   %s joined=%d results=%d (%.1fs)" % ("PASS" if not any(t.is_alive() for t in ts) and sorted(res) == list(range(8)) else "FAIL", sum(not t.is_alive() for t in ts), len(res), time.time() - t0))
q = queue.Queue()
def prod():
    for i in range(1000): q.put(i)
    q.put(None)
got = []
def cons():
    while (v := q.get()) is not None: got.append(v)
a, b = threading.Thread(target=prod), threading.Thread(target=cons)
a.start(); b.start(); a.join(30); b.join(30)
print("T queue     %s %d items" % ("PASS" if got == list(range(1000)) else "FAIL", len(got)))
with cf.ThreadPoolExecutor(4) as ex:
    r = list(ex.map(work, range(6)))
print("T pool      %s %d results" % ("PASS" if len(r) == 6 else "FAIL", len(r)))
ev = threading.Event()
threading.Timer(0.5, ev.set).start()
print("T timer     %s" % ("PASS" if ev.wait(10) else "FAIL"))
print("T-END", flush=True)
