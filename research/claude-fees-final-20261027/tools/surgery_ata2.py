#!/usr/bin/env python3
"""IR surgery diagnostics for the ATA invoke-branch layout. Writes OUT.ll from base-opt.ll.
mode B: route both if-internal error exits (require + invoke error) through a new block bbX placed
right after the invoke block; bbX holds PHIs for the error pair and a lifetime.end; bb43 phis updated."""
import re, sys
src, out, mode = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src).read()
m = re.search(r'\ndefine [^\n]*admit_associated_token_account[^\n]*\{\n', s)
start = m.start() + 1; end = s.find('\n}\n', start) + 3; f = s[start:end]
e22 = '"_ZN45_$LT$T$u20$as$u20$alloc..string..ToString$GT$9to_string17h3f8720cb5c1d2f09E.exit22"'
e115 = '"_ZN4core3ptr52drop_in_place$LT$solana_instruction..Instruction$GT$17h877e270bb2588328E.exit115"'
def reroute(f, lbl):
    i = f.index(lbl + ':'); j = f.index('br label %bb43', i)
    return f[:j] + 'br label %bbX' + f[j + len('br label %bb43'):]
lt = {'B': '  call void @llvm.lifetime.end.p0(i64 160, ptr nonnull %_29)\n', 'C': '', 'G': '  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %expected)\n'}[mode]
f = reroute(f, e22); f = reroute(f, e115)
k = f.index('\nbb43:'); head, tail = f[:k], f[k:]
# bb43 phis: drop the two incoming and add bbX
lines = tail.split('\n')
for n, l in enumerate(lines):
    if ' = phi ' in l:
        l = re.sub(r', \[ [^\]]*%' + re.escape(e22) + r' \]', '', l)
        l = re.sub(r'\[ [^\]]*%' + re.escape(e22) + r' \], ', '', l)
        l = re.sub(r', \[ [^\]]*%' + re.escape(e115) + r' \]', '', l)
        l = re.sub(r'\[ [^\]]*%' + re.escape(e115) + r' \], ', '', l)
        name = l.split('=')[0].strip()
        l = l + f', [ {name}.x, %bbX ]'
        lines[n] = l
tail = '\n'.join(lines)
f = head + tail
# values: pick from original phis
phis = {}
for l in s[start:end].split('\n'):
    if l.startswith('  %_0.sroa.9.3 = phi') or l.startswith('  %_0.sroa.0.3 = phi'):
        name = l.split('=')[0].strip(); ty = l.split('phi ')[1].split(' ')[0]
        v22 = re.search(r'\[ ([^,]+), %' + re.escape(e22) + r' \]', l).group(1)
        v115 = re.search(r'\[ ([^,]+), %' + re.escape(e115) + r' \]', l).group(1)
        phis[name] = (ty, v22, v115)
blk = 'bbX:\n' + ''.join(f'  {n}.x = phi {t} [ {a}, %{e22} ], [ {b}, %{e115} ]\n' for n, (t, a, b) in phis.items()) + lt + '  br label %bb43\n\n'
p = f.index('\nbb50:') + 1
f = f[:p] + blk + f[p:]
open(out, 'w').write(s[:start] + f + s[end:])
print('written', out)
