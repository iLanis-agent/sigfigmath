#!/usr/bin/env python3
# Sig Fig Math oracle - mirrors engine.js.
import json, re

def _parse(text):
    t = text.strip() if isinstance(text, str) else ""
    if not re.fullmatch(r"[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)", t):
        raise ValueError("enter a plain decimal number such as 0.00450, 1200 or -3.5")
    neg = t[0] == "-"
    body = t[1:] if t[0] in "+-" else t
    hp = "." in body
    ip, fp = (body.split(".", 1) if hp else (body, ""))
    if len(ip) + len(fp) > 30:
        raise ValueError("the number can have at most 30 digits")
    digits = ip + fp
    return {"text": t, "neg": neg, "digits": digits, "frac": len(fp), "hp": hp, "mag": int(digits)}

def _first_nonzero(d):
    for i, c in enumerate(d):
        if c != "0":
            return i
    return -1

def _figs(k): return f"{k} significant figure" if k == 1 else f"{k} significant figures"
def _places(k): return f"{k} decimal place" if k == 1 else f"{k} decimal places"

def count_truth(text):
    p = _parse(text); s = _first_nonzero(p["digits"])
    if s < 0:
        return p["text"] + " is zero, and the usual rules do not give it a count of significant figures."
    all_ = len(p["digits"]) - s
    if p["hp"]:
        return f"{p['text']} has {_figs(all_)}."
    z = 0
    while p["digits"][len(p["digits"]) - 1 - z] == "0":
        z += 1
    if z == 0:
        return f"{p['text']} has {_figs(all_)}."
    return f"{p['text']} has {all_ - z} to {_figs(all_)}, depending on which trailing zeros were measured."

def round_truth(text, n):
    p = _parse(text)
    if isinstance(n, bool) or not isinstance(n, (int, float)) or n != n or n in (float("inf"), float("-inf")) or int(n) != n or n < 1 or n > 30:
        raise ValueError("significant figures must be a whole number from 1 to 30")
    n = int(n)
    if p["mag"] == 0:
        return f"{p['text']} is zero, so rounding it to {_figs(n)} leaves zero."
    ms = str(p["mag"]); e10 = len(ms) - 1 - p["frac"]
    shift = len(ms) - n
    if shift > 0:
        pw = 10 ** shift
        r = (2 * p["mag"] + pw) // (2 * pw)
    else:
        r = p["mag"] * 10 ** (-shift)
    if len(str(r)) > n:
        r //= 10; e10 += 1
    rs = str(r)
    sci = rs[0] + ("." + rs[1:] if n > 1 else "") + f" x 10^{e10}"
    sign = "-" if p["neg"] else ""
    k = e10 - (n - 1)
    if k > 0:
        out = sign + sci
    elif k == 0:
        out = f"{sign}{rs} ({sign}{sci})"
    else:
        f = -k
        rs = rs.rjust(f + 1, "0")
        out = f"{sign}{rs[:len(rs) - f]}.{rs[len(rs) - f:]} ({sign}{sci})"
    return f"{p['text']} to {_figs(n)} is {out}."

def _fmt(s, d):
    neg = s < 0; t = str(-s if neg else s)
    if d == 0:
        return ("-" if neg else "") + t
    t = t.rjust(d + 1, "0")
    return ("-" if neg else "") + t[:len(t) - d] + "." + t[len(t) - d:]

def add_truth(a, b):
    x = _parse(a); y = _parse(b)
    f = max(x["frac"], y["frac"]); dp = min(x["frac"], y["frac"])
    X = (-1 if x["neg"] else 1) * x["mag"] * 10 ** (f - x["frac"])
    Y = (-1 if y["neg"] else 1) * y["mag"] * 10 ** (f - y["frac"])
    s = X + Y
    exact = _fmt(s, f)
    cut = 10 ** (f - dp)
    neg = s < 0; m = -s if neg else s
    r = (2 * m + cut) // (2 * cut)
    if neg and r != 0:
        r = -r
    kept = _fmt(r, dp)
    if x["frac"] == y["frac"]:
        tail = f"Both have {_places(dp)}, so the sum keeps {_places(dp)}: {kept}."
    else:
        tail = f"The less precise number has {_places(dp)}, so the sum is {kept}."
    return f"{x['text']} + {y['text']} = {exact} exactly. {tail}"

FNS = {"countTruth": count_truth, "roundTruth": round_truth, "addTruth": add_truth}
CASES = [
    ("countTruth", ["0.00450"]), ("countTruth", ["1200"]), ("countTruth", ["1200."]), ("countTruth", ["1.200"]), ("countTruth", ["100.0"]),
    ("countTruth", ["5"]), ("countTruth", ["10"]), ("countTruth", ["0.5"]), ("countTruth", ["-3.50"]), ("countTruth", ["007"]), ("countTruth", ["1050"]),
    ("countTruth", ["0"]), ("countTruth", ["0.000"]), ("countTruth", [".0450"]), ("countTruth", ["+12.30"]), ("countTruth", [" 4500 "]),
    ("countTruth", [""]), ("countTruth", ["1e3"]), ("countTruth", ["1,200"]), ("countTruth", ["1" * 31]), ("countTruth", [12]),
    ("roundTruth", ["12345.6", 3]), ("roundTruth", ["0.004567", 2]), ("roundTruth", ["999.5", 3]), ("roundTruth", ["9.995", 3]), ("roundTruth", ["2.5", 1]),
    ("roundTruth", ["-0.0456", 2]), ("roundTruth", ["12", 4]), ("roundTruth", ["123", 3]), ("roundTruth", ["1", 1]), ("roundTruth", ["0.5", 1]),
    ("roundTruth", ["15", 1]), ("roundTruth", ["1200", 5]), ("roundTruth", ["0.00450", 3]), ("roundTruth", ["0", 3]), ("roundTruth", ["99999", 2]),
    ("roundTruth", ["3.14159265358979", 6]), ("roundTruth", ["123456789", 30]),
    ("roundTruth", ["abc", 3]), ("roundTruth", ["12.3", 0]), ("roundTruth", ["12.3", 31]), ("roundTruth", ["12.3", 2.5]),
    ("addTruth", ["12.11", "0.3"]), ("addTruth", ["3.57", "1.2"]), ("addTruth", ["1.25", "2.25"]), ("addTruth", ["100", "0.55"]), ("addTruth", ["5", "-3"]),
    ("addTruth", ["0.5", "-0.55"]), ("addTruth", ["-1.26", "0.1"]), ("addTruth", ["1.5", "1.5"]), ("addTruth", ["0.04", "0.01"]), ("addTruth", ["999.9", "0.15"]),
    ("addTruth", ["1.", "0.25"]), ("addTruth", ["-2.5", "-2.54"]), ("addTruth", ["0", "0.000"]), ("addTruth", ["x", "1"]), ("addTruth", ["1", ""]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
