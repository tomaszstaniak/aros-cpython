# driver.py URL LOGDIR - ask the host which test to run next, run it in a new
# interpreter (os.system, through the python launcher), and send the log and
# the JUnit XML back. Loops until the host answers "done".
#
# Each test gets a fresh interpreter so that one test cannot leave state that
# changes the result of the next, as a single regrtest process would. The host
# watches the time each test takes; if a test hangs or the machine crashes, the
# host restarts the machine and this driver is started again. The host then
# hands out the next test, so a test that brings the machine down is run once.
#
# Sockets work only in the main thread in this port (L2); all network calls
# here are made from it.
import sys, os, json, time, hashlib, platform, urllib.request

url, logdir = sys.argv[1].rstrip("/"), sys.argv[2]
os.makedirs(logdir, exist_ok=True)


def call(path, data=None, tries=30):
    for i in range(tries):
        try:
            req = urllib.request.Request(url + path, data=data, method="POST" if data is not None else "GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except OSError as e:
            print("driver: %s failed (%s), retrying" % (path, e), flush=True)
            time.sleep(10)
    raise SystemExit("driver: host not reachable")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read(path):
    try:
        with open(path, "rb") as f:
            return f.read().decode("utf-8", "backslashreplace")
    except OSError as e:
        return None


hello = {"version": sys.version, "executable": sys.executable,
         "sha256": sha256(sys.executable), "platform": sys.platform,
         "uname": list(os.uname()), "machine": platform.machine(),
         "maxsize": sys.maxsize, "logdir": logdir}
reply = call("/hello", json.dumps(hello).encode())
# Tests that did not return before the machine was restarted: whatever part
# of their log reached the disk is sent back as a partial result.
for name in reply.get("recover", []):
    partial = {"name": name,
               "log": read(os.path.join(logdir, name + ".log")),
               "xml": read(os.path.join(logdir, name + ".xml"))}
    call("/partial", json.dumps(partial).encode())
while True:
    job = call("/next")
    if job.get("done"):
        print("driver: all tests handed out", flush=True)
        break
    name, test, opts = job["name"], job["test"], job["opts"]
    print("driver: %s %s" % (name, test), flush=True)
    t0 = time.time()
    rc = os.system("python /Python/tests/stdlib/rt.py %s %s %s %s"
                   % (logdir, name, test, " ".join(opts)))
    result = {"name": name, "test": test, "system_rc": rc,
              "seconds": round(time.time() - t0, 1),
              "log": read(os.path.join(logdir, name + ".log")),
              "xml": read(os.path.join(logdir, name + ".xml"))}
    call("/result", json.dumps(result).encode())
