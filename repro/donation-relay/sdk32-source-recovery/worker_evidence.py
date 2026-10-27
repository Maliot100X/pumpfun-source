"""Check full worker instructions, actual direct callees and relocated caller data."""
from pathlib import Path
import json,gzip,struct,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def derive():
 p=P/'settlement';o=read(p/'original-function-ledger.json.gz');c=read(p/'candidate-function-ledger.json.gz');m=read(p/'match-ledger.json.gz');oi={f['start']:i for i,f in enumerate(o)};ci={f['start']:i for i,f in enumerate(c)}
 indices=m[108]['normalized_candidate_indices'];assert len(indices)==1;i=indices[0];a=o[108];b=c[i];assert a['bytes']==b['bytes']==8264 and a['normalized_sha256']==b['normalized_sha256']
 assert len(a['direct_calls'])==len(b['direct_calls'])==51;edges=[]
 for left,right in zip(a['direct_calls'],b['direct_calls']):
  x=oi[left['target']];y=ci[right['target']];assert left['offset']==right['offset'] and y in m[x]['normalized_candidate_indices'];edges.append(dict(offset=left['offset'],original_ordinal=x,candidate_index=y,complete_normalized_callee_match=True))
 assert next(x for x in edges if x['original_ordinal']==226)['offset']==3752
 assert next(x for x in edges if x['original_ordinal']==113)['offset']==2200
 assert next(x for x in edges if x['original_ordinal']==81)['offset']==2632
 witness=next(x for x in read(p/'match-witnesses.json.gz') if x['original_ordinal']==108 and x['candidate_index']==i);assert all(x['normalized_body_pair'] for x in witness['direct_calls'])
 unclosed=sorted({x['target_pair'][0] for x in witness['direct_calls'] if not x['recursive_call_shape_closed']});assert unclosed==[] and witness['recursive_call_shape_closed']
 spec=importlib.util.spec_from_file_location('worker_caller_data_elf',P/'analyze.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf);original=elf.Elf((ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes());candidate=elf.Elf((p/'unstripped.so').read_bytes())
 def locations(e,f):
  rows={}
  for ref in f['data_references']:
   target=ref['target'];rel=e.relocations.get(target)
   if not rel or rel['type']!=8:continue
   packed,size,line,column=struct.unpack('<QQII',e.at(target,24))
   if packed&0xffffffff or not 0<size<200:continue
   try:name=e.at(packed>>32,size).decode()
   except (ValueError,UnicodeDecodeError):continue
   if '.rs' in name:rows[ref['offset']]=dict(filename=name,line=line,column=column)
  return rows
 locations_report=[]
 for ordinal,expected in [(108,{8200:('programs/contracts/src/tools/distribution/shared.rs',91,45),8240:('programs/contracts/src/tools/distribution/shared.rs',118,54)}),(113,{528:('programs/contracts/src/tools/fair_distribution.rs',28,46),560:('programs/contracts/src/tools/fair_distribution.rs',27,32),2200:('programs/contracts/src/tools/fair_distribution.rs',63,45)})]:
  index=m[ordinal]['normalized_candidate_indices'][0];left=locations(original,o[ordinal]);right=locations(candidate,c[index]);assert set(left)==set(right)
  for offset,(name,line,column) in expected.items():
   value=dict(filename=name,line=line,column=column);assert left[offset]==right[offset]==value;locations_report.append(dict(original_ordinal=ordinal,offset=offset,**value))
  for offset,value in left.items():
   if offset in expected:continue
   assert value['filename'].startswith('/home/runner/work/platform-tools/') and right[offset]['filename']==value['filename'].replace('/home/runner/','/Users/runner/',1)
   assert (value['line'],value['column'])==(right[offset]['line'],right[offset]['column'])
 source=(p/'source/src/tools/distribution/shared.rs').read_text();assert 'to:info.clone()' in source and 'to:token.to_account_info()' not in source
 lib=(p/'source/src/lib.rs').read_text();assert 'include!("tools/distribution/shared.rs"); include!("tools/fair_distribution.rs");' in lib
 assert all(m[x]['normalized_candidate_indices'] for x in [282,300,332])
 return dict(original_worker_ordinal=108,candidate_worker_index=i,worker_bytes=8264,complete_normalized_match=True,raw_match=a['raw_sha256']==b['raw_sha256'],actual_direct_edges=edges,direct_callee_count=51,all_direct_callees_complete_normalized_match=True,recursive_direct_call_shape_closed=True,direct_callees_with_unclosed_transitive_shapes=unclosed,matching_application_caller_descriptors=locations_report,application_caller_descriptor_count=5,vendor_sysroot_path_difference_retained=True,compiled_local_rust_files=28,inventoried_rust_config_files=50,privileged_settlement_success_executed=False,whole_original_byte_identity=False,interpretation='Entire worker instruction shape and all actual direct callee bodies match. Five application caller filename/line/column tuples also match from relocated ELF data. Transitive instruction shapes now close. Native versus Linux sysroot strings, indirect/data/allocator behavior and full ELF identity remain open.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
