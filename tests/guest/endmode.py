# endmode.py MODE - load what the probe loads, then end in MODE:
#   normal     return from the script
#   sysexit    sys.exit(3)
#   exception  unhandled RuntimeError
#   wait       print WAITING and sleep; stop it with Ctrl-C in this Shell or
#              `Break <n> C` from another Shell
#   spin       busy loop without sleeping; stop it the same ways as wait
#   crash      read address 0 (faulthandler._read_null), a hard fault
# Afterwards, check that the Shell still takes commands.
import sys, os, time, bz2, pwd, socket

mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
print("EM START", mode, flush=True)
try:
    pwd.getpwuid(os.getuid())
except KeyError:
    pass
bz2.decompress(bz2.compress(b"x" * 1000))
s = socket.socket(); s.close()
print("EM LOADED", flush=True)

if mode == "sysexit":
    sys.exit(3)
if mode == "exception":
    raise RuntimeError("endmode: unhandled on purpose")
if mode == "wait":
    print("EM WAITING", flush=True)
    while True:
        time.sleep(1)
if mode == "spin":
    print("EM SPINNING", flush=True)
    n = 0
    while True:
        n += 1
if mode == "crash":
    import faulthandler
    faulthandler._read_null()
print("EM END normal", flush=True)
