"""Files and JSON round-trip."""
import json
doc = {"os": "aros", "python": "3.14", "items": [1, 2, 3]}
with open("/RAM/demo.json", "w") as f:
    json.dump(doc, f, indent=2)
with open("/RAM/demo.json") as f:
    print("read back:", json.load(f))
