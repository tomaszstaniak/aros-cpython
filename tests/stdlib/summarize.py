#!/usr/bin/env python3
"""Summarize a Lib/test run collected by the host (state.json + logs/).

    summarize.py RUNDIR [--md OUT.md] [--json OUT.json]

Per test module, the verdict is regrtest's own line ("test_x passed",
"failed", "skipped -- reason", "crashed", "resource denied", "failed (env
changed)"), or, when the module never returned, the host's classification:
timeout (no result in the time limit), crash (a system failure on screen),
requester (a system requester on screen), or not run.

Per test case, the counts and every skip reason come from regrtest's JUnit
XML. A skip is only reported with the reason the test gave; whether that
reason is acceptable is decided in the report, not here.
"""
import argparse, collections, json, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

VERDICT = re.compile(r"^\d+:\d\d:\d\d(?: load avg: [\d.]+)? \[\s*\d+/\d+(?:/\d+)?\] (\S+) (.*)$", re.M)


def module_verdict(log, test):
    if log is None:
        return None, None
    last = None
    for m in VERDICT.finditer(log):
        if m.group(1) == test:
            last = m.group(2).strip()
    if last is None:
        return None, None
    if last.startswith("passed"):
        return "PASS", last
    if last.startswith("skipped"):
        return "SKIP", last
    if last.startswith("failed (env changed)"):
        return "ENV_CHANGED", last
    if "resource denied" in last:
        return "RESOURCE_DENIED", last
    if last.startswith("failed (uncaught exception)") or last.startswith("crashed"):
        return "ERROR", last
    if last.startswith("failed"):
        return "FAIL", last
    if "run no tests" in last or "no tests ran" in last:
        return "NO_TESTS", last
    return "OTHER", last


def cases(xml):
    out = collections.Counter()
    skips, failures = [], []
    if not xml:
        return out, skips, failures
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        out["xml_unreadable"] += 1
        return out, skips, failures
    for tc in root.iter("testcase"):
        name = tc.get("name", "")
        # regrtest writes the reason or traceback as element text.
        def text(e):
            return ((e.get("message") or "") + " " + (e.text or "")).strip()
        if tc.find("skipped") is not None:
            out["skipped"] += 1
            skips.append((name, text(tc.find("skipped"))))
        elif tc.find("failure") is not None:
            out["failed"] += 1
            failures.append((name, "failure", text(tc.find("failure"))[-600:]))
        elif tc.find("error") is not None:
            out["error"] += 1
            failures.append((name, "error", text(tc.find("error"))[-600:]))
        else:
            out["passed"] += 1
    return out, skips, failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    run = Path(a.rundir)
    state = json.loads((run / "state.json").read_text())
    rows = []
    for t in state["tests"]:
        att = t["attempts"][-1] if t["attempts"] else None
        row = {"seq": t["seq"], "test": t["test"], "attempts": len(t["attempts"]),
               "host_status": t["status"]}
        if att is None:
            row["verdict"] = "NOT_RUN"
        elif t["status"] == "returned":
            logp = run / "logs" / (att["name"] + ".log")
            xmlp = run / "logs" / (att["name"] + ".xml")
            log = logp.read_text(errors="replace") if logp.exists() else None
            xml = xmlp.read_text(errors="replace") if xmlp.exists() else None
            v, line = module_verdict(log, t["test"])
            row["verdict"] = v or ("NO_VERDICT" if log else "NO_LOG")
            row["line"] = line
            row["rt_exit"] = att.get("rt_exit")
            row["seconds"] = att.get("seconds")
            c, skips, fails = cases(xml)
            row["cases"] = dict(c)
            row["skips"] = skips
            row["failures"] = fails
            row["log"] = str(logp.name)
        elif t["status"] in ("timeout", "crash", "requester"):
            row["verdict"] = t["status"].upper()
            row["why"] = att.get("why")
            row["shot"] = att.get("shot")
            p = run / "logs" / (att["name"] + ".partial.log")
            row["partial_log"] = p.name if p.exists() else None
        else:
            row["verdict"] = "NOT_RUN" if t["status"] == "pending" else t["status"].upper()
        rows.append(row)

    total = collections.Counter(r["verdict"] for r in rows)
    case_total = collections.Counter()
    for r in rows:
        case_total.update(r.get("cases", {}))
    if a.json:
        Path(a.json).write_text(json.dumps({"modules": rows, "totals": total,
                                            "cases": case_total}, indent=1))
    lines = ["# Lib/test run %s" % run.name, "",
             "Interpreter reported by the guest: %s" % ", ".join(sorted({h.get("sha256", "?") for h in state.get("hello", [])})),
             "Options: `%s`" % " ".join(state.get("opts", [])), "",
             "## Test modules (%d)" % len(rows), ""]
    for k, v in sorted(total.items()):
        lines.append("- %s: %d" % (k, v))
    lines += ["", "## Test cases (from JUnit XML of modules that returned)", ""]
    for k, v in sorted(case_total.items()):
        lines.append("- %s: %d" % (k, v))
    lines += ["", "## Modules", "", "| # | test | verdict | cases | detail |", "|---|---|---|---|---|"]
    for r in rows:
        c = r.get("cases", {})
        cs = "%d/%d/%d/%d" % (c.get("passed", 0), c.get("failed", 0), c.get("error", 0), c.get("skipped", 0)) if c else ""
        detail = (r.get("line") or r.get("why") or "").replace("|", "\\|")[:160]
        lines.append("| %d | %s | %s | %s | %s |" % (r["seq"], r["test"], r["verdict"], cs, detail))
    lines += ["", "Cases column: passed/failed/error/skipped.", "", "## Skip reasons", ""]
    reasons = collections.Counter()
    for r in rows:
        for _, why in r.get("skips", []):
            reasons[why[:200]] += 1
        if r["verdict"] == "SKIP":
            reasons["(whole module) " + (r.get("line") or "")[:200]] += 1
    for why, n in reasons.most_common():
        lines.append("- %d x %s" % (n, why.replace("\n", " ")))
    out = "\n".join(lines) + "\n"
    if a.md:
        Path(a.md).write_text(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
