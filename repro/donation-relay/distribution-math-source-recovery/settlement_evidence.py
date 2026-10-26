"""Full generated settlement bodies, source layouts and actual dispatch/call targets."""
from pathlib import Path
import gzip,json,re,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def derive():
 p=P/'settlement';o=read(p/'original-function-ledger.json.gz');c=read(p/'candidate-function-ledger.json.gz');m=read(p/'match-ledger.json.gz');oi={f['start']:i for i,f in enumerate(o)};ci={f['start']:i for i,f in enumerate(c)}
 def calls(f,indices):return [indices[x['target']] for x in f['direct_calls']]
 def named(term):
  rows=[i for i,f in enumerate(c) if any(term in n for n in f['names'])];assert len(rows)==1,(term,rows);return rows[0]
 def matched(ordinal,index):assert index in m[ordinal]['normalized_candidate_indices']
 entries=[]
 for name,wrapper,parser,ex,program,body in [('distribute_after_just_swapping_v1',186,146,147,201,97),('distribute_non_swap_output_mint_v1',187,148,149,200,98),('swap_then_distribute_v1',184,154,155,203,100)]:
  wi=named('__global'+str(len(name))+name+'17h');pi=named('probe'+str(len(name))+name+'17h');matched(wrapper,wi);matched(program,pi);assert program in calls(o[wrapper],oi) and parser in calls(o[wrapper],oi) and ex in calls(o[wrapper],oi)
  assert pi in calls(c[wi],ci) and any(i in calls(c[wi],ci) for i in m[parser]['normalized_candidate_indices']) and any(i in calls(c[wi],ci) for i in m[ex]['normalized_candidate_indices'])
  assert 105 in calls(o[program],oi) and body in calls(o[program],oi);assert any(i in calls(c[pi],ci) for i in m[105]['normalized_candidate_indices'])
  term={97:'settlement_handlers16distribute_after',98:'settlement_handlers19distribute_non_swap',100:'settlement_handlers20swap_then_distribute'}[body];bi=named(term);assert bi in calls(c[pi],ci) and not any(i in calls(c[bi],ci) for i in m[105]['normalized_candidate_indices']);assert not m[body]['normalized_candidate_indices']
  entries.append(dict(instruction=name,original_wrapper=wrapper,candidate_wrapper=wi,original_parser=parser,parser_bytes=o[parser]['bytes'],original_exit=ex,exit_bytes=o[ex]['bytes'],original_program=program,candidate_program=pi,program_bytes=o[program]['bytes'],original_body=body,candidate_body=bi,original_body_bytes=o[body]['bytes'],candidate_body_bytes=c[bi]['bytes'],complete_body_match=False))
 entry=named('anchor_framework5entry17h');matched(169,entry);assert o[169]['bytes']==c[entry]['bytes']==2216
 edges=[]
 for left,right in zip(o[169]['direct_calls'],c[entry]['direct_calls']):
  assert left['offset']==right['offset'];a=oi[left['target']];b=ci[right['target']];matched(a,b);edges.append(dict(offset=left['offset'],original_ordinal=a,candidate_index=b))
 business=[row for row in edges if 178<=row['original_ordinal']<=188];assert [row['original_ordinal'] for row in business]==list(range(178,189))
 expected=['donate_v1','donate_pubkey_config_id_v1','donate_native_v1','donate_native_pubkey_config_id_v1','donate_pubkey_config_id_with_payer_v1','close_donation_epoch_v1','swap_then_distribute_v1','just_swap_v1','distribute_after_just_swapping_v1','distribute_non_swap_output_mint_v1','upsert_mint_whitelist_v1']
 for name,row in zip(expected,business):assert any('__global'+str(len(name))+name+'17h' in n for n in c[row['candidate_index']]['names'])
 sdk=next(i for i,f in enumerate(c) if 'entrypoint' in f['names']);matched(194,sdk);assert c[sdk]['bytes']==448
 for left,right in zip(o[194]['direct_calls'],c[sdk]['direct_calls']):assert left['offset']==right['offset'];matched(oi[left['target']],ci[right['target']])
 worker=named('shared_distribution10distribute17h');math=named('shared_distribution12fair_amounts17h');receipt=m[81]['normalized_candidate_indices'];assert len(receipt)==1 and receipt[0] in calls(c[worker],ci) and c[receipt[0]]['bytes']==808
 for row in entries:assert worker in calls(c[row['candidate_body']],ci)
 assert math in calls(c[worker],ci) and not m[108]['normalized_candidate_indices'] and m[113]['normalized_candidate_indices']
 # The actual shared worker argument fields are source, mint, program, authority.
 log=(p/'build.log').read_text();layouts={"DistributeAfterJustSwappingV1<'_>":696,"DistributeNonSwapOutputMintV1<'_>":640,"SwapThenDistributeV1<'_>":920}
 for name,size in layouts.items():assert 'type: `anchor_framework::'+name+'`: '+str(size)+' bytes' in log
 assert "type: `shared_distribution::DistributionContext<'_, '_>`: 208 bytes" in log and "type: `shared_distribution::DistributionArgs<'_, '_, '_>`: 80 bytes" in log
 source=(p/'source/src/lib.rs').read_text();assert source.splitlines()[35].strip()=='#[program]' and 'let reserved =' not in source and 'anchor_framework::entry(program_id, accounts, data)' in source
 assert re.findall(r'        pub fn (\w+)',source)==expected
 worker_source=(p/'source/src/shared_distribution.rs').read_text();assert 'let DistributionContext {remaining,source,mint,program,authority}=ctx;' in worker_source and 'shares.iter().zip(amounts.iter())' in worker_source and 'if amount!=0' in worker_source
 source=(p/'source/src/settlement_handlers.rs').read_text();part=source[source.index("pub fn swap_then_distribute<'info>"):];assert 'InvalidState' not in part and 'InvalidMint' not in part and 'remaining.split_at(shares.len())' in part
 assert m[69]['normalized_candidate_indices'] and not m[332]['normalized_candidate_indices']
 return dict(routes=entries,dispatch_original_ordinal=169,dispatch_candidate_index=entry,dispatch_bytes=2216,dispatch_direct_edges=edges,all_eleven_business_wrappers_match=True,sdk_entrypoint_bytes=448,layouts=layouts,worker_context_bytes=208,worker_args_bytes=80,receipt_original_ordinal=81,receipt_candidate_index=receipt[0],receipt_bytes=808,shared_worker_original_bytes=8264,shared_worker_candidate_bytes=c[worker]['bytes'],shared_worker_complete_match=False,fair_math_original_bytes=2224,fair_math_candidate_bytes=c[math]['bytes'],fair_math_complete_match=True,lost_original_windows=[332],privileged_success_executed=False,whole_original_byte_identity=False,interpretation='Complete generated parser/wrapper/program/exit and dispatch windows match after existing normalization, with actual call targets checked. Business workers, account-close transitive helpers, allocator/indirect/data and whole-ELF identity remain open. No dummy callers retain dropped growth/resize specializations.')
if __name__=='__main__':print(json.dumps(derive(),indent=2))
