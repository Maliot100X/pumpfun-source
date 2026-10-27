#!/usr/bin/env python3
"""Data-side checks reused from the frontier verifiers: .rodata equality, .data.rel.ro size, Source-record counters
(fees-sharing-slice-recovery location()), direct-call target agreement for matched pairs.
usage: datacheck.py CANDIDATE_SYMBOLS.so"""
import sys, importlib.util, struct, contextlib, io
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True
WT = Path('/private/tmp/claude-501/-Users-shawwalters-Documents-Codex-2026-10-24-pumpfun-source/bf960843-6806-451b-a211-62c8b228d301/scratchpad/lanes/fees-final/wt')
def module(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
w = module('wm', WT / 'research/fees-composed-frontier188/window_map.py')
loc = module('loc', WT / 'research/fees-sharing-slice-recovery/verify.py')
orig = (WT / 'evidence/original/pump_fees/deployed.so').read_bytes()
cand = Path(sys.argv[1]).read_bytes()
ro_o, ro_c = w.m.section_data(orig, '.rodata'), w.m.section_data(cand, '.rodata')
print('rodata len', len(ro_o), len(ro_c), 'equal', ro_o == ro_c, 'diffbytes', sum(a != b for a, b in zip(ro_o, ro_c)) if len(ro_o) == len(ro_c) else 'n/a')
dr_o, dr_c = w.m.section_data(orig, '.data.rel.ro'), w.m.section_data(cand, '.data.rel.ro')
print('data.rel.ro len', len(dr_o), len(dr_c))
counters = []
for image in [orig, cand]:
    c = Counter()
    for a, k in w.m.relocations(image):
        if k & 0xffffffff != 8: continue
        try: c[loc.location(w, image, a)] += 1
        except (AssertionError, ValueError, StopIteration, struct.error, UnicodeDecodeError): pass
    counters.append(c)
print('source records orig', sum(counters[0].values()), 'cand', sum(counters[1].values()), 'equal', counters[0] == counters[1])
if counters[0] != counters[1]:
    print(' only orig:', list((counters[0] - counters[1]).items())[:10]); print(' only cand:', list((counters[1] - counters[0]).items())[:10])
# direct-call agreement for unique pairs
o = w.windows(orig); c = w.windows(cand); comp = w.compare(o, c)
pair = {p['original']['address']: p['candidate']['address'] for p in comp['unique_pairs']}
ow = {r['address']: r for r in o}; cw = {r['address']: r for r in c}
relo = dict(w.m.relocations(orig)); relc = dict(w.m.relocations(cand))
eq = tot = 0
for oa, ca in pair.items():
    for x, y in zip(w.m.instructions(orig, oa, ow[oa]['bytes']), w.m.instructions(cand, ca, cw[ca]['bytes'])):
        if 'call_target' in x and relo.get(oa + x['offset'], 0) & 0xffffffff != 10:
            tot += 1
            if pair.get(x['call_target']) == y.get('call_target'): eq += 1
print('direct-call observations equal', eq, '/', tot)
