#!/usr/bin/env python3
"""Native IR screen for ATA source variants (diagnostic only; never an acceptance build).
usage: ata_try.py VARIANT_NAME   (variants defined in ata_variants.py as {name: function_text or callable(src)->src})
Copies out/native/w579, rewrites instructions/fee_sharing/mod.rs, emits LLVM IR natively, compiles it with llc,
and compares the ATA body against original 243184 under call/lddw masking. Appends a JSON line to out/ata/results.jsonl."""
import sys, os, re, json, shutil, subprocess, hashlib, time
from pathlib import Path
L = Path('/private/tmp/claude-501/-Users-shawwalters-Documents-Codex-2026-10-24-pumpfun-source/bf960843-6806-451b-a211-62c8b228d301/scratchpad/lanes/fees-final')
OUT = L / 'out'; sys.path.insert(0, str(OUT / 'tools'))
import ata_variants, objfn
name = sys.argv[1]; var = ata_variants.VARIANTS[name]
src = OUT / 'native' / 'x' / name
if src.exists(): shutil.rmtree(src)
shutil.copytree(OUT / 'native' / 'w580', src, symlinks=True)
files = var(src) if callable(var) else None
mod = src / 'programs/pump-fees/src/instructions/fee_sharing/mod.rs'
if not callable(var):
    s = mod.read_text(); i = s.index('pub fn admit_associated_token_account'); j = s.index('\n}\n', i) + 3
    # the replacement must preserve the line count of the function region
    new = var
    assert new.count('\n') == s[i:j].count('\n'), (new.count('\n'), s[i:j].count('\n'))
    mod.write_text(s[:i] + new + s[j:])
for line in (273, 278, 299, 306):
    t = mod.read_text().split('\n')[line - 1]
    assert 'require' in t or 'error!' in t or 'err!' in t, (line, t)
ll = L / 'target-mac/sbpf-solana-solana/release/deps/pump_fees_candidate.ll'
if ll.exists(): ll.unlink()
t0 = time.time()
r = subprocess.run([str(OUT / 'tools/nbuild.sh'), str(src), '--emit=llvm-ir'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
log = r.stdout.decode(errors='replace'); (OUT / 'ata' / (name + '-build.log')).write_text(log)
res = dict(name=name, exit=r.returncode, build_s=round(time.time() - t0, 1))
if r.returncode == 0 and ll.exists():
    shutil.copy(ll, OUT / 'ata' / (name + '.ll'))
    o = OUT / 'ata' / (name + '.o')
    rr = subprocess.run(['python3', '/private/tmp/claude-501/-Users-shawwalters-Documents-Codex-2026-10-24-pumpfun-source/bf960843-6806-451b-a211-62c8b228d301/scratchpad/sbf_lock.py', '--slots', '6', '--name', 'sbf', '--',
        os.path.expanduser('~/.cache/solana/v1.44/platform-tools/llvm/bin/llc'), '-O3', '-march=sbf', '-mattr=+store-imm,+jmp-ext', '-relocation-model=pic',
        '-function-sections', '-data-sections', '-filetype=obj', str(OUT / 'ata' / (name + '.ll')), '-o', str(o)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res['llc_exit'] = rr.returncode
    if rr.returncode == 0:
        b = o.read_bytes(); hits, _ = objfn.find(b, 'admit_associated_token_account')
        orig = (L / 'wt/evidence/original/pump_fees/deployed.so').read_bytes()
        import importlib.util
        spec = importlib.util.spec_from_file_location('wm', L / 'wt/research/fees-composed-frontier188/window_map.py'); w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
        ref = w.m.at_address(orig, 243184, 6080)
        if hits:
            h = hits[0]; code = b[h['off']:h['off'] + h['size']]
            res.update(ata_bytes=len(code), normalized_equal=objfn.norm(code) == objfn.norm(ref))
            a, c = objfn.norm(code), objfn.norm(ref)
            res['first_diff'] = next((k for k in range(0, min(len(a), len(c)), 8) if a[k:k+8] != c[k:k+8]), None)
        else:
            res['ata_bytes'] = 0; res['note'] = 'no ATA section (inlined?)'
    os.remove(OUT / 'ata' / (name + '.ll')) if (OUT / 'ata' / (name + '.ll')).stat().st_size > 0 and not res.get('normalized_equal') else None
print(json.dumps(res)); open(OUT / 'ata' / 'results.jsonl', 'a').write(json.dumps(res) + '\n')
