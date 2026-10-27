#!/usr/bin/env python3
"""Extract a function's .text section bytes from an ELF relocatable object (function-sections), and
compare to a window in a linked image under call/lddw masking.
usage: objfn.py OBJ NAME_SUBSTR [--cmp IMAGE ADDRESS] [--dis]"""
import struct, sys, re, hashlib
from pathlib import Path
def sections(b):
    shoff = struct.unpack_from('<Q', b, 0x28)[0]; shentsize, shnum, shstrndx = struct.unpack_from('<HHH', b, 0x3a)
    sh = [struct.unpack_from('<IIQQQQIIQQ', b, shoff + i * shentsize) for i in range(shnum)]
    strtab = sh[shstrndx]; names = b[strtab[4]:strtab[4] + strtab[5]]
    out = []
    for i, s in enumerate(sh):
        out.append(dict(idx=i, name=names[s[0]:].split(b'\0')[0].decode(), type=s[1], off=s[4], size=s[5], link=s[6], info=s[7], entsize=s[9]))
    return out
def find(b, key):
    secs = sections(b)
    hits = [s for s in secs if s['name'].startswith('.text') and key in s['name']]
    return hits, secs
def norm(code):
    out = bytearray(); p = 0
    while p < len(code):
        op = code[p]; w = 16 if op == 0x18 else 8; ins = bytearray(code[p:p + w])
        if op == 0x85 or op == 0x18: ins[4:8] = bytes(4)
        if op == 0x18: ins[12:16] = bytes(4)
        out += ins; p += w
    return bytes(out)
if __name__ == '__main__':
    b = Path(sys.argv[1]).read_bytes(); key = sys.argv[2]
    hits, secs = find(b, key)
    for h in hits: print(h['name'][:150], h['size'])
    if '--cmp' in sys.argv:
        i = sys.argv.index('--cmp'); img = Path(sys.argv[i + 1]).read_bytes(); addr = int(sys.argv[i + 2])
        sys.path.insert(0, str(Path(__file__).parent))
        import importlib.util
        WT = Path('/private/tmp/claude-501/-Users-shawwalters-Documents-Codex-2026-10-24-pumpfun-source/bf960843-6806-451b-a211-62c8b228d301/scratchpad/lanes/fees-final/wt')
        s = importlib.util.spec_from_file_location('wm', WT / 'research/fees-composed-frontier188/window_map.py'); w = importlib.util.module_from_spec(s); s.loader.exec_module(w)
        win = {r['address']: r for r in w.windows(img)}[addr]
        ref = w.m.at_address(img, addr, win['bytes'])
        h = hits[0]; code = b[h['off']:h['off'] + h['size']]
        print('obj size', len(code), 'image size', len(ref), 'normalized equal:', norm(code) == norm(ref))
        if norm(code) != norm(ref):
            a, c = norm(code), norm(ref)
            for k in range(0, min(len(a), len(c)), 8):
                if a[k:k+8] != c[k:k+8]: print('first diff at', k, a[k:k+8].hex(), c[k:k+8].hex()); break
