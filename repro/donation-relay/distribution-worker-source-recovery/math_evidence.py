"""Recheck complete math, actual call targets, and compiler-reported local inputs."""
from pathlib import Path
import json,gzip,hashlib
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def derive():
 p=P/'settlement';o=read(p/'original-function-ledger.json.gz');c=read(p/'candidate-function-ledger.json.gz');m=read(p/'match-ledger.json.gz');oi={f['start']:i for i,f in enumerate(o)};ci={f['start']:i for i,f in enumerate(c)}
 matches=m[113]['normalized_candidate_indices'];assert len(matches)==1;i=matches[0];a=o[113];b=c[i]
 assert a['bytes']==b['bytes']==2224 and a['normalized_sha256']==b['normalized_sha256'] and m[108]['normalized_candidate_indices']
 assert len(a['direct_calls'])==len(b['direct_calls'])==14
 edges=[]
 for left,right in zip(a['direct_calls'],b['direct_calls']):
  assert left['offset']==right['offset'];x=oi[left['target']];y=ci[right['target']];assert y in m[x]['normalized_candidate_indices']
  if x==490:assert c[y]['names']==['__multi3']
  if x==480:assert c[y]['names']==['__udivti3']
  edges.append(dict(offset=left['offset'],original_ordinal=x,candidate_index=y,names=c[y]['names'],complete_normalized_match=True))
 assert [x['original_ordinal'] for x in edges]==[490,382,382,490,480,490,68,69,115,59,115,58,115,405]
 witness=next(x for x in read(p/'match-witnesses.json.gz') if x['original_ordinal']==113 and x['candidate_index']==i)
 assert witness['recursive_call_shape_closed'] and all(x['recursive_call_shape_closed'] for x in witness['direct_calls'])
 for n in ['settlement','current-source-proof']:
  q=P/n;compiled=read(q/'compiled-local-inputs.json');assert H((q/'local-inputs.d').read_bytes())==compiled['dep_info_sha256'];names=(q/'local-inputs.d').read_text().splitlines()[0].split(': ',1)[1].split();assert set(names)==set(compiled['inputs']) and len(names)==len(set(names))==28
  source=read(q/'source-manifest.json');assert all(source[name]==digest for name,digest in compiled['inputs'].items())
  assert not set(names)&{'src/arithmetic.rs','src/handlers.rs','src/runtime.rs','src/solana_runtime.rs','src/entrypoint.rs','src/generated_exit.rs','src/dispatch.rs','src/model.rs'}
 assert read(p/'compiled-local-inputs.json')['inputs']==read(P/'current-source-proof/compiled-local-inputs.json')['inputs']
 text=(p/'source/src/tools/distribution/shared.rs').read_text()+(p/'source/src/tools/fair_distribution.rs').read_text();assert 'let remainder=product%10000' in text and 'for position in 0..(left as usize).min(remainders.len())' in text
 assert 'allocated.checked_add(amount)' in text and 'total.checked_sub(allocated)' in text and 'checked_add(1)' in text
 assert 'let info=&remaining[index]' in text and text.index('let amount=amounts[index]')>text.index('InvalidTokenAccountProgram,112')
 worker=next(x for x in c if any('shared_distribution10distribute' in n for n in x['names']));assert worker['bytes']==8264
 growth=m[69]['normalized_candidate_indices'];assert len(growth)==1 and c[growth[0]]['bytes']==o[69]['bytes']==440
 return dict(original_math_ordinal=113,candidate_math_index=i,math_bytes=2224,complete_normalized_match=True,raw_match=a['raw_sha256']==b['raw_sha256'],direct_edges=edges,recursive_direct_call_shape_closed=True,recovered_growth_ordinal=69,growth_bytes=440,compiled_local_rust_inputs=28,inventoried_rust_config_files=50,shared_worker_original_bytes=8264,shared_worker_candidate_bytes=8264,shared_worker_complete_match=True,privileged_success_executed=False,whole_original_byte_identity=False,interpretation='Full math instruction body and all actual direct callees match under the existing call/relocation-only normalization. Compiler dep-info distinguishes 28 reachable local Rust files from 50 inventoried Rust/config files. This is not ELF identity or privileged settlement execution.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
