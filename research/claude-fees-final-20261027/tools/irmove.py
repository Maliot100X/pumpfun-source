#!/usr/bin/env python3
"""Move whole basic blocks of the ATA function in an .ll file (after renaming unnamed values so text order is free).
usage: irmove.py IN.ll OUT.ll BLOCK_LABEL BEFORE_LABEL"""
import re, sys
src, out, lab, before = sys.argv[1:5]
s = open(src).read()
m = re.search(r'\ndefine [^\n]*admit_associated_token_account[^\n]*\{\n', s)
start = m.start() + 1; end = s.find('\n}\n', start) + 3; f = s[start:end]
# rename unnamed values %N (not inside quotes/metadata) -> %vN ; skip !N metadata and #N attributes
f = re.sub(r'(?<![\w.$"])%(\d+)\b', r'%v\1', f)
def cut_block(f, label):
    i = f.index('\n' + label + ':') + 1
    j = f.find('\n\n', i)
    if j == -1:
        j = f.rindex('\n}') + 1   # last block: stop before the closing brace
        return f[:i] + f[j:], f[i:j]
    j = j + 2
    return f[:i] + f[j:], f[i:j]
g, blk = cut_block(f, lab)
if not blk.endswith('\n\n'): blk = blk.rstrip('\n') + '\n\n'
p = g.index('\n' + before + ':') + 1
g = g[:p] + blk + g[p:]
open(out, 'w').write(s[:start] + g + s[end:])
print('moved', lab, 'before', before)
