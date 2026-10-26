from pathlib import Path
import subprocess,json,hashlib,os,shutil
P=Path(__file__).resolve().parent;ROOT=P.parents[1];source=P/'source';sdk=Path('/Users/shawwalters/.cache/solana/v1.48/platform-tools');H=lambda b:hashlib.sha256(b).hexdigest()
env=dict(os.environ)
for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','RUSTUP_TOOLCHAIN','RUSTDOCFLAGS']:env.pop(k,None)
env.update(PATH=str(sdk/'rust/bin')+os.pathsep+env.get('PATH',''),RUSTC=str(sdk/'rust/bin/rustc'),CC=str(sdk/'llvm/bin/clang'),AR=str(sdk/'llvm/bin/llvm-ar'),OBJDUMP=str(sdk/'llvm/bin/llvm-objdump'),OBJCOPY=str(sdk/'llvm/bin/llvm-objcopy'),CARGO_HOME=str(ROOT/'work/relay-anchor-idl-scaffold/cargo-home'),CARGO_TARGET_DIR=str(P/'target'),CARGO_TARGET_SBF_SOLANA_SOLANA_RUSTFLAGS='-Zremap-cwd-prefix=',CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='3')
assert not (P/'target').exists(),'fresh target required'
resolve=[str(sdk/'rust/bin/cargo'),'metadata','--offline','--format-version','1','--filter-platform','sbf-solana-solana','--manifest-path',str(source/'Cargo.toml')]
with (P/'resolve.log').open('wb') as f:r=subprocess.run(resolve,env=env,stdout=f,stderr=subprocess.STDOUT)
if r.returncode:
 (P/'resolve-result.json').write_text(json.dumps(dict(returncode=r.returncode),indent=2)+'\n');print((P/'resolve.log').read_text()[-4000:]);raise SystemExit(r.returncode)
files={str(q.relative_to(source)):H(q.read_bytes()) for q in sorted(source.rglob('*')) if q.is_file() and 'target' not in q.relative_to(source).parts and (q.suffix=='.rs' or q.name in ['Cargo.toml','Cargo.lock'])};(P/'source-manifest.json').write_text(json.dumps(files,indent=2)+'\n')
cmd=[str(sdk/'rust/bin/cargo'),'rustc','--release','--target','sbf-solana-solana','--locked','--offline','--manifest-path',str(source/'Cargo.toml'),'--lib','--','--remap-path-prefix=src/=programs/contracts/src/','-Zprint-type-sizes'];(P/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with (P/'build.log').open('wb') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
facts=dict(returncode=r.returncode,source_unchanged=all(H((source/n).read_bytes())==h for n,h in files.items()),log_sha256=H((P/'build.log').read_bytes()),scope='Fresh offline combined Anchor reserved-framework and recovered Relay business Rust build; whole-program byte identity unproven.')
if r.returncode==0:
 q=P/'target/sbf-solana-solana/release/donation_relay_source_proposal.so';shutil.copyfile(q,P/'unstripped.so');strip=[str(sdk/'llvm/bin/llvm-objcopy'),'--strip-all',str(q),str(P/'candidate.so')];subprocess.run(strip,check=True);facts.update(candidate_sha256=H((P/'candidate.so').read_bytes()),candidate_bytes=(P/'candidate.so').stat().st_size,unstripped_sha256=H((P/'unstripped.so').read_bytes()));(P/'strip-command.json').write_text(json.dumps(strip,indent=2)+'\n')
(P/'build-result.json').write_text(json.dumps(facts,indent=2)+'\n');print(json.dumps(facts,indent=2));assert r.returncode==0 and facts['source_unchanged']
