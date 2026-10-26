"""Decode the complete balance helper and every actual direct-call target."""
from pathlib import Path
import gzip,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def derive():
 p=P/'settlement';o=read(p/'original-function-ledger.json.gz');c=read(p/'candidate-function-ledger.json.gz');m=read(p/'match-ledger.json.gz');oi={f['start']:i for i,f in enumerate(o)};ci={f['start']:i for i,f in enumerate(c)};indices=m[91]['normalized_candidate_indices'];assert len(indices)==1;index=indices[0];original=o[91];candidate=c[index];assert original['bytes']==candidate['bytes']==2880 and original['normalized_sha256']==candidate['normalized_sha256']
 assert len(original['direct_calls'])==len(candidate['direct_calls'])==19;edges=[]
 for left,right in zip(original['direct_calls'],candidate['direct_calls']):
  assert left['offset']==right['offset'];a=oi[left['target']];b=ci[right['target']];matched=b in m[a]['normalized_candidate_indices'];assert matched or a==90
  if a==90:assert any('settlement_handlers14invoke_jupiter' in n for n in c[b]['names'])
  edges.append(dict(offset=left['offset'],original_ordinal=a,candidate_index=b,complete_callee_normalized_match=matched))
 assert [x['original_ordinal'] for x in edges if not x['complete_callee_normalized_match']]==[90]
 assert [x['original_ordinal'] for x in edges[:3]]==[90,21,21]
 spec=importlib.util.spec_from_file_location('balance_elf',P/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
 filename=b'programs/contracts/src/cpi/jupiter.rs';source_refs={}
 for label,elf,f in [('original',a.Elf((ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()),original),('candidate',a.Elf((p/'unstripped.so').read_bytes()),candidate)]:
  refs=[r['offset'] for r in f['data_references'] if elf.at(r['target'],len(filename))==filename];assert refs==[984,1624];source_refs[label]=refs
 text=(p/'source/src/settlement_handlers.rs').read_text();assert "swap_observed<'info>(program:&AccountInfo<'info>,authority:Pubkey," in text and "remaining:&[AccountInfo<'info>],data:Vec<u8>,seeds:" in text
 assert 'invoke_jupiter(program.key(),authority,remaining,data,seeds)' in text and 'accounts:metas,data};' in text and 'data.to_vec()' not in text and 'data.clone()' not in text
 assert 'if seeds.is_empty()' in text and '::invoke(&ix,&infos)' in text and '::invoke_signed(&ix,&infos,seeds)' in text
 return dict(original_ordinal=91,candidate_index=index,bytes=2880,complete_normalized_match=True,complete_raw_match=original['raw_sha256']==candidate['raw_sha256'],direct_call_edges=edges,source_filename=filename.decode(),source_reference_offsets=source_refs,owned_swap_data_forwarded=True,unmatched_dependency_ordinals=[90],privileged_success_executed=False,whole_original_byte_identity=False,interpretation='Every direct callee except the Jupiter CPI builder also matches completely after call/relocation normalization. Source and operand audit retain owned vector forwarding, exact balance checks and reload order. Builder/body, data/indirect/allocator and whole-ELF identity remain open.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
