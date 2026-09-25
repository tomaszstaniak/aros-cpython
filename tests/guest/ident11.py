# ident11.py - thread identifiers, lock ownership, and a socket in a worker.
import threading, os, socket, _thread, sys, traceback
print("ID main get_ident", threading.get_ident(), "main_thread", threading.main_thread().ident, flush=True)
w = []
th = threading.Thread(target=lambda: w.append(threading.get_ident())); th.start(); th.join()
print("ID worker", w, flush=True)
r = threading.RLock()
with r:
    print("ID rlock repr in main:", repr(r), flush=True)
print("SC SC_IOV_MAX known", "SC_IOV_MAX" in os.sysconf_names, "sendmsg", hasattr(socket.socket, "sendmsg"), flush=True)
import warnings
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    print("WL catch_warnings ok", flush=True)
except BaseException as e:
    print("WL", type(e).__name__, e, flush=True)
res = []
def work():
    try:
        s = socket.create_connection(("pypi.org", 80), timeout=20)
        s.sendall(b"HEAD / HTTP/1.0\r\nHost: pypi.org\r\n\r\n")
        res.append(s.recv(40)); s.close()
    except BaseException as e:
        res.append("%s: %s" % (type(e).__name__, e))
th = threading.Thread(target=work); th.start(); th.join(60)
print("WS worker socket", res, flush=True)
print("ID-END", flush=True)
