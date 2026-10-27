"""Complete SDK helper bodies and actual direct-call closure, with archive provenance."""
from pathlib import Path
import gzip,json,tomllib,hashlib,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
H=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def derive():
 p=P/'settlement';o=read(p/'original-function-ledger.json.gz');c=read(p/'candidate-function-ledger.json.gz');m=read(p/'match-ledger.json.gz');w=read(p/'match-witnesses.json.gz');oi={f['start']:i for i,f in enumerate(o)};ci={f['start']:i for i,f in enumerate(c)}
 expected=[4,167,172,240,242,243,244,282,300,332,344];prior=read(ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement/match-ledger.json.gz')
 assert [x['ordinal'] for x,y in zip(m,prior) if x['normalized_candidate_indices'] and not y['normalized_candidate_indices']]==expected
 assert not [x['ordinal'] for x,y in zip(m,prior) if not x['normalized_candidate_indices'] and y['normalized_candidate_indices']]
 rows=[]
 for i in expected:
  assert len(m[i]['normalized_candidate_indices'])==1;i2=m[i]['normalized_candidate_indices'][0];a=o[i];b=c[i2];assert a['bytes']==b['bytes'] and a['normalized_sha256']==b['normalized_sha256'];witness=next(x for x in w if x['original_ordinal']==i and x['candidate_index']==i2);assert witness['recursive_call_shape_closed']
  edges=[]
  for l,r in zip(a['direct_calls'],b['direct_calls']):
   assert l['offset']==r['offset'];left=oi[l['target']];right=ci[r['target']];assert right in m[left]['normalized_candidate_indices'];edges.append(dict(offset=l['offset'],original_ordinal=left,candidate_index=right))
  assert len(a['direct_calls'])==len(b['direct_calls']);rows.append(dict(original_ordinal=i,candidate_index=i2,bytes=a['bytes'],names=b['names'],actual_direct_edges=edges,recursive_direct_call_shape_closed=True))
 for i in [8,108,113,226]:assert any(x['original_ordinal']==i and x['recursive_call_shape_closed'] for x in w)
 old=tomllib.loads((ROOT/'repro/donation-relay/distribution-worker-source-recovery/settlement/source/Cargo.lock').read_text())['package'];new=tomllib.loads((p/'source/Cargo.lock').read_text())['package'];a={(x['name'],x['version']) for x in old};b={(x['name'],x['version']) for x in new};assert ('anchor-lang','0.32.1') in b and ('anchor-spl','0.32.1') in b and ('solana-invoke','0.4.0') in b and ('spl-token-2022','8.0.1') in b
 assert ('anchor-lang','0.31.1') not in b and ('spl-token-2022','7.0.0') not in b
 registry=read(P/'registry-source-audit.json');packages={(x['name'],x['version']):x for x in registry['packages']};assert registry['registry_packages']==177
 sources={('anchor-lang','0.32.1'):'src/common.rs',('solana-invoke','0.4.0'):'src/lib.rs',('solana-account-info','2.3.0'):'src/lib.rs'};snippets={}
 for (name,version),member in sources.items():
  archive=P/'registry-archives'/(name+'-'+version+'.crate');assert H(archive.read_bytes())==packages[(name,version)]['archive_sha256']
  with tarfile.open(archive) as tar:data=tar.extractfile(name+'-'+version+'/'+member).read()
  assert H(data)==packages[(name,version)]['files'][member];snippets[name]=data.decode()
 assert 'info.resize(0)' in snippets['anchor-lang'] and 'StableInstructionBorrowed::new(instruction)' in snippets['solana-invoke'] and 'self.realloc(new_len, true)' in snippets['solana-account-info']
 src=(p/'source/src/settlement_handlers.rs').read_text();assert 'BpsSumDoesNotEqualTenThousand,204).with_values((sum,10000u32))' in src
 assert (p/'source/src/state/v1/swap_receipt.rs').read_text().splitlines()[4]=='#[account]'
 rea=read(P/'rea-rust-inspection.json');assert rea['normalized_result']['summary']['auditable_metadata'] is None and rea['normalized_result']['summary']['rustc_commit'] is None
 return dict(gained_original_ordinals=expected,lost_original_ordinals=[],recovered_bodies=rows,closed_worker_original_ordinal=108,closed_transfer_original_ordinal=226,registry_packages=177,registry_files=registry['files'],registry_bytes=registry['bytes'],removed_packages=[list(x) for x in sorted(a-b)],added_packages=[list(x) for x in sorted(b-a)],rea_evidence_id=rea['evidence_id'],historical_dependency_recipe_proven=False,whole_original_byte_identity=False,interpretation='Measured Anchor0.32.1 and Token2022 8.0.1 dependency boundary recovers eleven complete windows and their direct-call closure without lost matches. Public archives are pinned and rehashed. No embedded dependency metadata authenticates the historical build recipe. Body identity is normalized only; full ELF, indirect calls, data and runtime acceptance remain separate.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
