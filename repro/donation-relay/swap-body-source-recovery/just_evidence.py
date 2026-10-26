"""Read-only full-body and actual just-swap call-chain checks."""
from pathlib import Path
import gzip,json,re
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def derive():
 p=P/'swap';o=read(p/'original-function-ledger.json.gz');c=read(p/'candidate-function-ledger.json.gz');m=read(p/'match-ledger.json.gz');oi={f['start']:i for i,f in enumerate(o)};ci={f['start']:i for i,f in enumerate(c)}
 def calls(f,indices):return [indices[x['target']] for x in f['direct_calls']]
 def named(term):
  rows=[i for i,f in enumerate(c) if any(term in n for n in f['names'])];assert len(rows)==1,(term,rows);return rows[0]
 wrapper=named('__global12just_swap_v117h');program=named('probe12just_swap_v117h');body=named('settlement_handlers9just_swap17h');swap=named('settlement_handlers13swap_observed17h');invoke=named('settlement_handlers14invoke_jupiter17h');burn=named('settlement_handlers14burn_and_close17h')
 matched=[91,10,13,20,21,22,43,44,82,118,145,150,151,152,153,161,168,185,202,227,246];assert all(m[i]['normalized_candidate_indices'] for i in matched)
 for j in [150,153,202]:assert j in calls(o[185],oi)
 assert 105 in calls(o[202],oi) and 99 in calls(o[202],oi) and 105 not in calls(o[99],oi)
 assert all(j in calls(o[99],oi) for j in [91,21,109]);assert all(j in calls(o[91],oi) for j in [90,21])
 assert program in calls(c[wrapper],ci) and body in calls(c[program],ci) and any(i in calls(c[program],ci) for i in m[105]['normalized_candidate_indices']);assert not any(i in calls(c[body],ci) for i in m[105]['normalized_candidate_indices'])
 assert swap in calls(c[body],ci) and burn in calls(c[body],ci) and invoke in calls(c[swap],ci)
 assert any(i in calls(c[body],ci) for i in m[21]['normalized_candidate_indices']) and any(i in calls(c[swap],ci) for i in m[21]['normalized_candidate_indices'])
 parser=m[150]['normalized_candidate_indices'][0];assert parser in calls(c[wrapper],ci)
 for j in [151,152]:assert any(i in calls(c[parser],ci) for i in m[j]['normalized_candidate_indices'])
 for exit_index in [145,153]:assert any(c[m[20]['normalized_candidate_indices'][0]]['start']==x['target'] for x in c[m[exit_index]['normalized_candidate_indices'][0]]['direct_calls'])
 assert c[wrapper]['bytes']==1432 and c[program]['bytes']==3096 and c[parser]['bytes']==18568
 source=(p/'source/src/instructions/v1/relayer_only/distribute/just_swap.rs').read_text();assert source.splitlines()[23]=='#[derive(Accounts)]' and "pub jupiter_program: AccountInfo<'info>" in source and 'mint::token_program = token_program, address = debouncer.mint' in source
 log=(p/'build.log').read_text();assert "type: `anchor_framework::JustSwapV1<'_>`: 976 bytes" in log
 control=read(ROOT/'repro/donation-relay/just-swap-source-recovery/trials/distribution-mint/just-mint-negative-control.json');assert len(control['cases'])==1 and not control['passed'];row=control['cases'][0];assert row['kind']=='debouncer_mint_field' and row['mismatches']['candidate']==['logs']
 # The former owned framework selector has no emitted implementation after its legitimate caller was replaced.
 assert not any('framework_codes9ErrorCode4name' in n for f in c for n in f['names'])
 unresolved={}
 for ordinal,index in [(99,body),(90,invoke),(109,burn)]:assert not m[ordinal]['normalized_candidate_indices'];unresolved[str(ordinal)]=dict(original_bytes=o[ordinal]['bytes'],candidate_bytes=c[index]['bytes'],candidate_index=index,complete_normalized_match=False)
 return dict(original_chain=[185,202,99],candidate_chain=[wrapper,program,body],original_parser=150,candidate_parser=parser,parser_bytes=18568,receipt_init_bytes=6664,ata_init_bytes=3584,exit_bytes=4056,close_exit_bytes=3304,restored_shared_serializer=20,restored_token_reload=21,fully_matched=matched,unmatched_bodies=unresolved,complete_swap_balance_match=True,swap_balance_bytes=2880,privileged_success_executed=False,owned_framework_selector_emitted=False,interpretation='Exact complete normalized parser, wrapper, program and exits match. Actual program guard retained. Finite owned-key rejection cases do not prove fixed-relayer/Jupiter success, body equivalence or whole-ELF identity.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
