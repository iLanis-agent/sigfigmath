// Sig Fig Math engine - count significant figures, round to n of them, and add measured decimals.
// Mirrored by oracle.py; keep the op order identical.
// Numbers are typed decimals of up to 30 digits. Arithmetic is exact (big integers); rounding is half away from zero.

function _parse(text) {
  var t = typeof text === "string" ? text.trim() : "";
  if (!/^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)$/.test(t)) {
    throw new Error("enter a plain decimal number such as 0.00450, 1200 or -3.5");
  }
  var neg = t.charAt(0) === "-";
  var body = t.charAt(0) === "-" || t.charAt(0) === "+" ? t.slice(1) : t;
  var at = body.indexOf(".");
  var hasPoint = at >= 0;
  var ip = hasPoint ? body.slice(0, at) : body, fp = hasPoint ? body.slice(at + 1) : "";
  if (ip.length + fp.length > 30) throw new Error("the number can have at most 30 digits");
  var digits = ip + fp;
  return { text: t, neg: neg, digits: digits, frac: fp.length, hasPoint: hasPoint, mag: BigInt(digits) };
}

function _firstNonzero(d) {
  for (var i = 0; i < d.length; i++) if (d.charAt(i) !== "0") return i;
  return -1;
}

function _figs(k) { return k + (k === 1 ? " significant figure" : " significant figures"); }
function _places(k) { return k + (k === 1 ? " decimal place" : " decimal places"); }

// The count truth: the significant figures in a number as written.
function countTruth(text) {
  var p = _parse(text), s = _firstNonzero(p.digits);
  if (s < 0) return p.text + " is zero, and the usual rules do not give it a count of significant figures.";
  var all = p.digits.length - s;
  if (p.hasPoint) return p.text + " has " + _figs(all) + ".";
  var z = 0;
  while (p.digits.charAt(p.digits.length - 1 - z) === "0") z++;
  if (z === 0) return p.text + " has " + _figs(all) + ".";
  return p.text + " has " + (all - z) + " to " + _figs(all) + ", depending on which trailing zeros were measured.";
}

// The round truth: a number rounded to n significant figures.
function roundTruth(text, n) {
  var p = _parse(text);
  if (typeof n !== "number" || !isFinite(n) || Math.floor(n) !== n || n < 1 || n > 30) {
    throw new Error("significant figures must be a whole number from 1 to 30");
  }
  if (p.mag === 0n) return p.text + " is zero, so rounding it to " + _figs(n) + " leaves zero.";
  var ms = p.mag.toString();
  var e10 = ms.length - 1 - p.frac;
  var shift = ms.length - n, r;
  if (shift > 0) {
    var pw = 10n ** BigInt(shift);
    r = (2n * p.mag + pw) / (2n * pw);
  } else {
    r = p.mag * 10n ** BigInt(-shift);
  }
  if (r.toString().length > n) { r = r / 10n; e10 += 1; }
  var rs = r.toString();
  var sci = rs.charAt(0) + (n > 1 ? "." + rs.slice(1) : "") + " x 10^" + e10;
  var sign = p.neg ? "-" : "";
  var k = e10 - (n - 1);
  var out;
  if (k > 0) out = sign + sci;
  else if (k === 0) out = sign + rs + " (" + sign + sci + ")";
  else {
    var f = -k;
    while (rs.length <= f) rs = "0" + rs;
    out = sign + rs.slice(0, rs.length - f) + "." + rs.slice(rs.length - f) + " (" + sign + sci + ")";
  }
  return p.text + " to " + _figs(n) + " is " + out + ".";
}

function _fmt(s, d) {
  var neg = s < 0n, a = neg ? -s : s;
  var t = a.toString();
  if (d === 0) return (neg ? "-" : "") + t;
  while (t.length <= d) t = "0" + t;
  return (neg ? "-" : "") + t.slice(0, t.length - d) + "." + t.slice(t.length - d);
}

// The add truth: a sum of two measured decimals, kept to the fewer decimal places.
function addTruth(a, b) {
  var x = _parse(a), y = _parse(b);
  var f = Math.max(x.frac, y.frac), dp = Math.min(x.frac, y.frac);
  var X = (x.neg ? -1n : 1n) * x.mag * 10n ** BigInt(f - x.frac);
  var Y = (y.neg ? -1n : 1n) * y.mag * 10n ** BigInt(f - y.frac);
  var s = X + Y;
  var exact = _fmt(s, f);
  var cut = 10n ** BigInt(f - dp);
  var neg = s < 0n, m = neg ? -s : s;
  var r = (2n * m + cut) / (2n * cut);
  if (neg && r !== 0n) r = -r;
  var kept = _fmt(r, dp);
  var tail = x.frac === y.frac
    ? "Both have " + _places(dp) + ", so the sum keeps " + _places(dp) + ": " + kept + "."
    : "The less precise number has " + _places(dp) + ", so the sum is " + kept + ".";
  return x.text + " + " + y.text + " = " + exact + " exactly. " + tail;
}
