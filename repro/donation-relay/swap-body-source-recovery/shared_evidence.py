"""Decode actual original/candidate call edges and compiler-reported Rust layouts."""
from pathlib import Path
import json,gzip,re
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def derive():
 p=P/'swap';original=read(p/'original-function-ledger.json.gz');candidate=read(p/'candidate-function-ledger.json.gz');ledger=read(p/'match-ledger.json.gz');ci={f['start']:i for i,f in enumerate(candidate)};oi={f['start']:i for i,f in enumerate(original)}
 log=(p/'build.log').read_text().splitlines()
 def layout(name,size,fields=None):
  prefix='print-type-size type: `'+name+'`:';locations=[i for i,s in enumerate(log) if s.startswith(prefix)];assert len(locations)==1;start=locations[0];rows=[log[start]]
  for s in log[start+1:]:
   if s.startswith('print-type-size type:'):break
   if s.startswith('print-type-size'):rows.append(s)
  assert rows[0].endswith(str(size)+' bytes, alignment: 8 bytes')
  if fields is not None:assert [(re.search(r'field `\.([^`]+)`',s)[1],int(re.search(r': (\d+) bytes',s)[1])) for s in rows[1:] if 'field `.' in s]==fields
  return rows
 layouts={
 'context':layout("shared_donation::DonationContext<'_, '_>",224,[('epoch_tracker',8),('debouncer',8),('from',8),('mint_whitelist',8),('debouncer_token_account',48),('mint',48),('from_token_account',48),('token_program',48)]),
 'args':layout('shared_donation::DonationArgs',72,[('message',24),('config_id',32),('amount',8),('tip_bps',2),('epoch_tracker_bump',1),('debouncer_bump',1)]),
 'amounts':layout('shared_donation::DonationAmounts',32,[('epoch',16),('gross_amount',8),('tip',8)]),
 'result':layout('std::result::Result<shared_donation::DonationAmounts, anchor_lang::error::Error>',40),
 }
 shared=[(i,f) for i,f in enumerate(candidate) if any('shared_donation13donate_shared' in n for n in f['names'])];assert len(shared)==1;index,body=shared[0];assert body['bytes']==10328 and original[112]['bytes']==10248 and not ledger[112]['normalized_candidate_indices']
 rows=[]
 for name,wrapper,program,handler in [('donate_v1',178,190,94),('donate_pubkey_config_id_v1',179,190,94),('donate_pubkey_config_id_with_payer_v1',182,193,95),('donate_native_v1',180,191,92),('donate_native_pubkey_config_id_v1',181,192,93)]:
  assert program in [oi.get(x['target']) for x in original[wrapper]['direct_calls']] and handler in [oi.get(x['target']) for x in original[program]['direct_calls']] and 112 in [oi.get(x['target']) for x in original[handler]['direct_calls']]
  wrappers=[(i,f) for i,f in enumerate(candidate) if any(re.search(r'__global\d+'+name+r'17h',n) for n in f['names'])];assert len(wrappers)==1;wi,wf=wrappers[0];program_targets=[ci[x['target']] for x in wf['direct_calls'] if x['target'] in ci and any('relay_anchor_idl_reconstruction_probe' in n and 'donate' in n for n in candidate[ci[x['target']]]['names'])];assert len(program_targets)==1;pi=program_targets[0]
  targets=[ci[x['target']] for x in candidate[pi]['direct_calls'] if x['target'] in ci and any('donation_handlers' in n for n in candidate[ci[x['target']]]['names'])];assert len(targets)==1;hi=targets[0];assert body['start'] in {x['target'] for x in candidate[hi]['direct_calls']}
  rows.append(dict(instruction=name,original_wrapper=wrapper,original_program=program,original_handler=handler,original_common=112,candidate_wrapper=wi,candidate_program=pi,candidate_program_bytes=candidate[pi]["bytes"],candidate_handler=hi,candidate_handler_bytes=candidate[hi]['bytes'],candidate_common=index))
 for i in [51,104,107,110,111,178,179,180,181,182,190,191,192,193]:assert ledger[i]['normalized_candidate_indices']
 assert ledger[21]['normalized_candidate_indices']
 return dict(layouts=layouts,original_common_bytes=10248,candidate_common_bytes=body['bytes'],candidate_common_normalized_sha256=body['normalized_sha256'],original_common_normalized_sha256=original[112]['normalized_sha256'],original_common_calls=len(original[112]['direct_calls']),candidate_common_calls=len(body['direct_calls']),complete_common_identity=False,rows=rows,fully_recovered_helpers=[51,104,107,110,111],restored_settlement_specialization=21,interpretation='Layouts agree with decoded offset hypotheses and all five routes actually reach the new common function. Helper body matches and finite runtime evidence do not prove shared-body, wrapper, data or whole-ELF identity.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
