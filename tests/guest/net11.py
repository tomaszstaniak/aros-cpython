# net11.py - one socket operation per line, to find the call that fails with
# errno 86 (ENOTSUP) under urllib/https.
import socket, errno, traceback, time
def step(name, fn):
    try:
        print("N %-16s OK  %s" % (name, fn()), flush=True)
    except BaseException as e:
        print("N %-16s ERR %s errno=%s %s" % (name, type(e).__name__, getattr(e, "errno", None), e), flush=True)
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print("N   at %s:%d %s" % (tb.filename.rsplit("/", 1)[-1], tb.lineno, tb.line), flush=True)
step("gethostbyname", lambda: socket.gethostbyname("pypi.org"))
step("getaddrinfo", lambda: socket.getaddrinfo("pypi.org", 443, socket.AF_INET, socket.SOCK_STREAM)[0][4])
step("getaddrinfo-any", lambda: socket.getaddrinfo("pypi.org", 443)[0][4])
step("getaddrinfo-num", lambda: socket.getaddrinfo("151.101.0.223", 443)[0][4])
def blocking():
    s = socket.socket(); s.connect((socket.gethostbyname("pypi.org"), 80)); s.close(); return "connected"
step("connect-block", blocking)
def settimeout():
    s = socket.socket(); s.settimeout(10); r = s.gettimeout(); s.close(); return r
step("settimeout", settimeout)
def setblocking():
    s = socket.socket(); s.setblocking(False); s.setblocking(True); s.close(); return "ok"
step("setblocking", setblocking)
def timeout_connect():
    s = socket.socket(); s.settimeout(20); s.connect((socket.gethostbyname("pypi.org"), 80)); s.close(); return "connected"
step("connect-timeout", timeout_connect)
step("create_conn", lambda: socket.create_connection(("pypi.org", 80), timeout=20).close() or "ok")
def opts():
    s = socket.socket(); s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1); s.close(); return "TCP_NODELAY"
step("nodelay", opts)
print("N-END", flush=True)
