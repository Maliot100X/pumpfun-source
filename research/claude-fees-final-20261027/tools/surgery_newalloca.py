#!/usr/bin/env python3
"""Surgery F: new alloca (size N) live from bb8 (create_if_missing check) to the end of the if statement:
lifetime.end in the error-exit join bbX (preds: require-error, invoke-error) and at bb23 entry (normal path).
The alloca gets one real use (volatile-free store of 0 to its first byte before bb8's branch is NOT added; only markers)."""
import re, sys
src, out, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
s = open(src).read()
m = re.search(r'\ndefine [^\n]*admit_associated_token_account[^\n]*\{\n', s)
start = m.start() + 1; end = s.find('\n}\n', start) + 3; f = s[start:end]
e22 = '"_ZN45_$LT$T$u20$as$u20$alloc..string..ToString$GT$9to_string17h3f8720cb5c1d2f09E.exit22"'
e115 = '"_ZN4core3ptr52drop_in_place$LT$solana_instruction..Instruction$GT$17h877e270bb2588328E.exit115"'
LS = f'  call void @llvm.lifetime.start.p0(i64 {N}, ptr nonnull %newx)\n'
LE = f'  call void @llvm.lifetime.end.p0(i64 {N}, ptr nonnull %newx)\n'
# alloca at entry
f = f.replace('\nstart:\n', f'\nstart:\n  %newx = alloca [{N} x i8], align {8 if N >= 8 else 1}\n', 1)
i = f.index('\nbb8:'); j = f.index('\n', i + 1) + 1; f = f[:j] + LS + f[j:]
i = f.index('\nbb23:'); j = f.index('\n', i + 1) + 1; f = f[:j] + LE + f[j:]
def reroute(f, lbl):
    i = f.index(lbl + ':'); j = f.index('br label %bb43', i); return f[:j] + 'br label %bbX' + f[j + len('br label %bb43'):]
f = reroute(f, e22); f = reroute(f, e115)
phis = {}
for l in s[start:end].split('\n'):
    if l.startswith('  %_0.sroa.9.3 = phi') or l.startswith('  %_0.sroa.0.3 = phi'):
        name = l.split('=')[0].strip(); ty = l.split('phi ')[1].split(' ')[0]
        a = re.search(r'\[ ([^,]+), %' + re.escape(e22) + r' \]', l).group(1); b = re.search(r'\[ ([^,]+), %' + re.escape(e115) + r' \]', l).group(1)
        phis[name] = (ty, a, b)
k = f.index('\nbb43:'); head, tail = f[:k], f[k:]
lines = tail.split('\n')
for n, l in enumerate(lines):
    if l.startswith('  %_0.sroa.9.3 = phi') or l.startswith('  %_0.sroa.0.3 = phi'):
        for lbl in (e22, e115):
            l = re.sub(r', \[ [^\]]*%' + re.escape(lbl) + r' \]', '', l); l = re.sub(r'\[ [^\]]*%' + re.escape(lbl) + r' \], ', '', l)
        name = l.split('=')[0].strip(); l = l + f', [ {name}.x, %bbX ]'; lines[n] = l
f = head + '\n'.join(lines)
blk = 'bbX:\n' + ''.join(f'  {n}.x = phi {t} [ {a}, %{e22} ], [ {b}, %{e115} ]\n' for n, (t, a, b) in phis.items()) + LE + '  br label %bb43\n\n'
p = f.index('\nbb50:') + 1; f = f[:p] + blk + f[p:]
open(out, 'w').write(s[:start] + f + s[end:])
