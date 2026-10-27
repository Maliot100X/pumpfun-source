#!/usr/bin/env python3
"""List the basic blocks of one function in an LLVM .ll file: label, non-intrinsic calls, terminator.
usage: irblocks.py FILE.ll NAME_SUBSTRING [--out FUNC.ll]"""
import re, sys
s = open(sys.argv[1]).read(); key = sys.argv[2]
m = re.search(r'\ndefine [^\n]*' + re.escape(key) + r'[^\n]*\{\n', s)
start = m.start() + 1; end = s.find('\n}\n', start) + 3; f = s[start:end]
if '--out' in sys.argv: open(sys.argv[sys.argv.index('--out') + 1], 'w').write(f)
blocks = re.split(r'\n(?=[A-Za-z0-9_.$"]+:)', f)
for b in blocks[1:] if blocks[0].startswith('define') and '\nstart:' not in blocks[0] else blocks:
    lines = b.strip().splitlines(); head = lines[0].split(';')[0].strip()
    calls = []
    for l in lines:
        c = re.search(r'call [^@]*@("?[^\(]+)', l)
        if c and not re.search(r'llvm\.(lifetime|dbg|assume|experimental|memcpy|memset)', l):
            nm = c.group(1).strip('"'); nm = re.sub(r'17h[0-9a-f]{16}E$', '', nm)
            calls.append(nm[-50:])
    print(f'{head[:40]:40s} {lines[-1].strip()[:90]:90s} {calls}')
