# conc11.py TAG - run for a while and report start/end times, so two copies
# started together show whether they overlapped. Writes a scratch file of its
# own to check that two interpreters do not disturb each other's files.
import sys, time, os, hashlib, json
tag = sys.argv[1]
t0 = time.time()
print("C %s START %.1f" % (tag, t0), flush=True)
p = "/RAM/conc-%s.json" % tag
h = hashlib.sha256()
for i in range(40):
    data = {"tag": tag, "i": i, "blob": [tag * 50] * 20}
    json.dump(data, open(p, "w"))
    assert json.load(open(p))["tag"] == tag
    h.update(open(p, "rb").read())
    time.sleep(0.25)
os.remove(p)
print("C %s END %.1f dur %.1f digest %s" % (tag, time.time(), time.time() - t0, h.hexdigest()[:12]), flush=True)
