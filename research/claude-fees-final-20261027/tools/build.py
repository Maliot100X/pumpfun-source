#!/usr/bin/env python3
"""Lane fees-final build controller (adapted from the frontier's builds/controller.py).

usage: build.py REL   where REL is a source tree under out/work (container /work/REL)
Runs cargo rustc in container claude-fees-final-build holding the sbf (6) and podman (2) slot locks.
Writes REL-launch.json, REL-build.log, REL-result.json, REL-symbols.so, REL-candidate.so, REL.map next to the tree.
If REL/linker.sh is absent, writes one from the frontier template with REL paths.
"""
from pathlib import Path
import hashlib, json, subprocess, sys, time
SP = Path('/private/tmp/claude-501/-Users-shawwalters-Documents-Codex-2026-10-24-pumpfun-source/bf960843-6806-451b-a211-62c8b228d301/scratchpad')
L = SP / 'lanes/fees-final'
WORK = L / 'out/work'
CONTAINER = 'claude-fees-final-build'
rel = sys.argv[1].strip('/')
extra = sys.argv[2:]
no_link = any(a.startswith('--emit=') and 'link' not in a for a in extra)
src = WORK / rel
cw = '/work/' + rel
sha = lambda b: hashlib.sha256(b).hexdigest()
def inputs():
    return {str(p.relative_to(src)): sha(p.read_bytes()) for p in sorted(src.rglob('*')) if p.is_file()}
linker = src / 'linker.sh'
if not linker.exists():
    linker.write_text(f'''#!/bin/bash
set -e
printf '%s\\n' "$@" > {cw}-link-args.txt
args=("$@")
for ((i=0; i<${{#args[@]}}; i++)); do
  if [[ "${{args[i]}}" == "-T" || "${{args[i]}}" == "--script" ]]; then
    cp "${{args[i+1]}}" /work/sdk-default-{rel.replace('/','_')}.ld
    args[i+1]={cw}/ordered.ld
  elif [[ "${{args[i]}}" == --script=* ]]; then
    cp "${{args[i]#--script=}}" /work/sdk-default-{rel.replace('/','_')}.ld
    args[i]=--script={cw}/ordered.ld
  fi
done
printf '%s\\n' "${{args[@]}}" > {cw}-effective-args.txt
exec /work/sdk/rust/lib/rustlib/x86_64-unknown-linux-gnu/bin/rust-lld "${{args[@]}}"
''')
    linker.chmod(0o755)
env = {'PATH': '/work/sdk/rust/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
       'RUSTC': '/work/sdk/rust/bin/rustc', 'CC': '/work/sdk/llvm/bin/clang', 'AR': '/work/sdk/llvm/bin/llvm-ar',
       'CARGO_HOME': '/cargo', 'CARGO_TARGET_DIR': '/work/target', 'CARGO_BUILD_JOBS': '1',
       'CARGO_NET_OFFLINE': 'true', 'RUSTFLAGS': '-Zremap-cwd-prefix='}
cmd = ['podman', 'exec']
for k, v in env.items():
    cmd += ['-e', k + '=' + v]
cmd += ['-w', cw, CONTAINER, '/work/sdk/rust/bin/cargo', 'rustc', '--verbose', '--manifest-path',
        cw + '/programs/pump-fees/Cargo.toml', '--release', '--target', 'sbpf-solana-solana', '--locked',
        '--offline', '--jobs', '1', '--lib', '--',
        f'--remap-path-prefix={cw}/programs/pump-fees/src/../../../pump-fees-math/=pump-fees-math/',
        f'--remap-path-prefix={cw}/pump-fees-math/=pump-fees-math/',
        '--remap-path-prefix=programs/pump-fees/src/../../../pump-fees-math/=pump-fees-math/',
        '-C', 'link-arg=-Map=' + cw + '.map', '-C', 'linker=' + cw + '/linker.sh'] + extra
locked = ['python3', str(SP / 'sbf_lock.py'), '--slots', '6', '--name', 'sbf', '--',
          'python3', str(SP / 'sbf_lock.py'), '--slots', '2', '--name', 'podman', '--'] + cmd
initial = inputs()
out = lambda suffix: WORK / (rel + suffix)
out('-launch.json').write_text(json.dumps({'command': cmd, 'inputs': initial}, indent=2) + '\n')
so_path = L / 'target/sbpf-solana-solana/release/pump_fees_candidate.so'
if so_path.exists() and not no_link: so_path.unlink()
start = time.monotonic()
with out('-build.log').open('wb') as log:
    r = subprocess.run(locked, stdout=log, stderr=subprocess.STDOUT)
result = {'exit_code': r.returncode, 'elapsed_seconds': time.monotonic() - start,
          'source_unchanged': inputs() == initial, 'log_sha256': sha(out('-build.log').read_bytes())}
if r.returncode == 0 and not no_link:
    raw = so_path.read_bytes()
    out('-symbols.so').write_bytes(raw)
    strip = ['/Users/shawwalters/.cache/solana/v1.52/platform-tools/llvm/bin/llvm-objcopy', '--strip-all',
             str(out('-symbols.so')), str(out('-candidate.so'))]
    subprocess.run(strip, check=True)
    result.update(symbols_sha256=sha(raw), candidate_sha256=sha(out('-candidate.so').read_bytes()), strip_command=strip)
out('-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
sys.exit(r.returncode)
