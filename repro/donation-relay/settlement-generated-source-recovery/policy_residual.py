"""The entire policy body remains unmatched; retain exact instruction residuals."""
import json,gzip,hashlib,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def derive():
 sp=importlib.util.spec_from_file_location('typed_mint_residual_elf',P/'analyze.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);d=P/'settlement'
 of=json.loads(gzip.decompress((d/'original-function-ledger.json.gz').read_bytes()))[106];fs=json.loads(gzip.decompress((d/'candidate-function-ledger.json.gz').read_bytes()));matches=[(i,f) for i,f in enumerate(fs) if any('typed_mint_safe' in n for n in f['names'])];assert len(matches)==1;index,cf=matches[0];assert of['bytes']==cf['bytes']==3440
 def normalized(e,f):
  data=bytearray(e.at(f['start'],f['bytes']))
  for row in f['direct_calls']:offset=row['offset'];data[offset+4:offset+8]=bytes(4)
  for row in f['data_references']:offset=row['offset'];data[offset+4:offset+8]=bytes(4);data[offset+12:offset+16]=bytes(4)
  assert hashlib.sha256(data).hexdigest()==f['normalized_sha256'];return data
 original=a.Elf((ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes());candidate=a.Elf((d/'unstripped.so').read_bytes());left=normalized(original,of);right=normalized(candidate,cf)
 changes=[dict(offset=i,original_normalized_hex=left[i:i+8].hex(),candidate_normalized_hex=right[i:i+8].hex()) for i in range(0,len(left),8) if left[i:i+8]!=right[i:i+8]];assert [x['offset'] for x in changes]==[1360,1368,1376]
 ledger=json.loads(gzip.decompress((d/'match-ledger.json.gz').read_bytes()));assert not ledger[106]['normalized_candidate_indices']
 edges=[]
 for i in [30,31,32]:
  assert of['direct_calls'] and json.loads(gzip.decompress((d/'original-function-ledger.json.gz').read_bytes()))[i]['start'] in {x['target'] for x in of['direct_calls']}
  targets=[j for j in ledger[i]['normalized_candidate_indices'] if fs[j]['start'] in {x['target'] for x in cf['direct_calls']}];assert targets;edges.append(dict(original_ordinal=i,candidate_indices=targets))
 return dict(original_ordinal=106,candidate_index=index,bytes=3440,normalized_equal=False,instruction_changes=changes,recovered_lookup_calls=edges,interpretation='Three register-choice instructions differ. No register, branch or stack normalization is allowed for function acceptance. Full data/call/allocator closure and whole ELF equality remain unproved.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
