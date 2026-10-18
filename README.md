# Sig Fig Math

Significant figures arithmetic. 1200 might have two significant figures or four, and the number alone cannot say.

## What it computes

- **The count truth** - significant figures in a number as written. Leading zeros do not count; zeros after a decimal point do; trailing zeros in a whole number with no point are reported as a range instead of guessed. Zero gets no count.
- **The round truth** - a number rounded to 1 to 30 significant figures, shown plainly and in scientific notation.
- **The add truth** - two measured decimals added exactly, then kept to the fewer decimal places.

Numbers are typed decimals of up to 30 digits. Arithmetic is exact with big integers. Rounding is half away from zero.

## Boundary

Arithmetic only. Sig Fig Math does not know the rounding or notation rules your course, lab or journal requires. Check those where they apply.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic.
- `oracle.py` - the Python mirror that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (57 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/sigfigmath/
Repo: https://github.com/iLanis-agent/sigfigmath
