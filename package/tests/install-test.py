"""CPython for AROS - install acceptance test.

Run:  python /Python/tests/install-test.py
Writes results line by line to /RAM/aros-py-test.log AND stdout, so a host-side
timeout that kills this process leaves a partial log (missing lines) rather than
a false PASS. A check counts as PASS only if its line says PASS.

Everything here runs on an unmodified AROS system. The wheel install/import/run
check is a SEPARATE step (it needs its own process); see wheel-test.
"""
import sys, os, json, threading, socket, errno

LOG = "/RAM/aros-py-test.log"
_lf = open(LOG, "w", buffering=1)
def emit(s):
    print(s); _lf.write(s + "\n"); _lf.flush()

results = []
def check(name, fn):
    try:
        ok, detail = fn()
    except BaseException as e:
        ok, detail = False, "EXC %r" % (e,)
    results.append((name, ok))
    emit("%-30s %s  %s" % (name, "PASS" if ok else "FAIL", detail))

# 1. interpreter identity
def t_interp():
    return sys.platform == "aros", sys.version.split("[")[0].strip()
check("interpreter", t_interp)

# 2. files + JSON round-trip
def t_json():
    path = "/RAM/aros_py_json.tmp"
    data = {"name": "aros", "n": 314, "list": [1, 2, 3], "ok": True}
    with open(path, "w") as f:
        json.dump(data, f)
    with open(path) as f:
        back = json.load(f)
    os.remove(path)
    return back == data, "round-trip ok"
check("files + JSON", t_json)

# 2b. zlib via the system z1.library (RUNTIME dependency, not bundled here).
#     Presence in a dev build does not guarantee it on a recipient's system.
def t_zlib():
    import zlib
    data = b"AROS-preview " * 64
    ok = zlib.decompress(zlib.compress(data, 6)) == data
    return ok, "z1.library present, ZLIB_VERSION=%s" % zlib.ZLIB_VERSION
check("zlib (system z1.library)", t_zlib)

# 3. HTTPS with certificate AND hostname verification; response closed
def t_https():
    import ssl, urllib.request
    ctx = ssl.create_default_context()
    assert ctx.verify_mode == ssl.CERT_REQUIRED, "cert verification off"
    assert ctx.check_hostname is True, "hostname check off"
    r = urllib.request.urlopen("https://example.com", timeout=40, context=ctx)
    try:
        body = r.read()
        status = r.status
    finally:
        r.close()
    return status == 200 and len(body) > 0, "status=%d len=%d verify+hostname=on" % (status, len(body))
check("HTTPS (cert+hostname)", t_https)

# 4. single-threaded HTTP server: created AND served on ONE thread, three
#    sequential requests from a raw-socket loopback client (no urllib, no DNS,
#    so this does NOT depend on the worker resolver path), response body
#    checked, server bounded by a timeout so it can never hang, closed cleanly.
def t_http_single():
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"      # server closes after each response
        def log_message(self, *a): pass
        def do_GET(self):
            b = b"ok"; self.send_response(200)
            self.send_header("Content-Length", "2"); self.end_headers()
            self.wfile.write(b)
            self.server._served += 1
    srv = HTTPServer(("127.0.0.1", 8097), H)
    srv.timeout = 8                        # handle_request can NEVER block forever
    srv._served = 0
    res = {"n": 0, "bodies": []}
    def client():
        import socket as _s
        for i in range(3):
            try:
                c = _s.create_connection(("127.0.0.1", 8097), timeout=8)
                c.sendall(b"GET /x%d HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n" % i)
                buf = b""
                while True:
                    chunk = c.recv(4096)
                    if not chunk: break
                    buf += chunk
                c.close()
                body = buf.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in buf else b""
                res["bodies"].append(body)
                if b"200" in buf.split(b"\r\n", 1)[0] and body == b"ok":
                    res["n"] += 1
            except Exception as e:
                res["err"] = repr(e); break
    emit("single-thread HTTP: starting (bounded, raw loopback client)")  # before blocking
    tc = threading.Thread(target=client); tc.start()
    for _ in range(3):
        srv.handle_request()               # each call bounded by srv.timeout
    srv.server_close()
    tc.join(15)
    ok = (res["n"] == 3 and srv._served == 3 and not tc.is_alive()
          and res["bodies"] == [b"ok", b"ok", b"ok"])
    return ok, "served=%d client_ok=%d bodies=%r%s" % (
        srv._served, res["n"], res["bodies"],
        "" if "err" not in res else " err=" + res["err"])
check("single-thread HTTP x3", t_http_single)

# 5. an erroring socket op in a WORKER thread must raise a SPECIFIC, clean
#    exception (errno ENOTCONN, real message), close its socket, and finish.
def t_worker_error():
    out = {}
    def w():
        s = socket.socket()
        try:
            s.getpeername()          # unconnected -> must raise ENOTCONN
            out["r"] = ("returned",)
        except OSError as e:
            out["r"] = ("OSError", e.errno, e.strerror)
        except BaseException as e:
            out["r"] = ("OTHER", repr(e))
        finally:
            s.close()
            out["closed"] = (s.fileno() == -1)
    t = threading.Thread(target=w)
    t.start(); t.join(15)
    r = out.get("r")
    good_err = (isinstance(r, tuple) and r[0] == "OSError"
                and r[1] == errno.ENOTCONN
                and isinstance(r[2], str) and len(r[2]) > 0)
    ok = good_err and out.get("closed") is True and not t.is_alive()
    return ok, "worker=%r closed=%s alive=%s" % (r, out.get("closed"), t.is_alive())
check("worker socket error -> ENOTCONN", t_worker_error)

npass = sum(1 for _, ok in results if ok)
emit("\nSUMMARY %d/%d PASS" % (npass, len(results)))
_lf.close()
sys.exit(0 if npass == len(results) else 1)
