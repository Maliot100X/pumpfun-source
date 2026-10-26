from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal';sp=importlib.util.spec_from_file_location('distribution_frozen_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/swap-body-source-recovery/swap/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='53fe5b68ce2eba3634912ac86637a99f342c0884b0d2578d8702282a50b29893';assert H(paths['original'].read_bytes())==m.EXPECTED['original'];assert H((proposal/'artifacts/spl_token.so').read_bytes())==m.EXPECTED['token'] and H((proposal/'artifacts/associated_token.so').read_bytes())==m.EXPECTED['ata']
def fixture(route):
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_v1'));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);config=bytes(ix.data)[16:48];input_mint=ix.accounts[3].pubkey if route=='after' else m.Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');settlement=m.Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');epoch=3;gross=4000000;output=2000000;signer=ix.accounts[5].pubkey;recipient=available[2].pubkey();oldc=proof['canonical_pdas']
 for k in [proof['source_token_or_temp'],oldc['mint_whitelist'],oldc['debouncer_token_account'],oldc['epoch_tracker'],oldc['debouncer']]:accounts.pop(k)
 tracker,tb=m.pd([b'epoch_tracker_v1',config,bytes(input_mint)]);deb,bb=m.pd([b'debouncer_v1',config,bytes(input_mint)]);dist,db=m.pd([b'distribution_v1',config,bytes(input_mint),epoch.to_bytes(16,'little')]);receipt,rb=m.pd([b'swap_receipt_v1',bytes(dist)]);source=m.ata(dist,settlement)
 c={'epoch_tracker':str(tracker),'debouncer':str(deb),'distribution':str(dist),'event_authority':oldc['event_authority']};c['output_distribution_token_account' if route=='after' else 'distribution_token_account']=str(source)
 if route=='after':c['swap_receipt']=str(receipt)
 proof['canonical_pdas']=c
 for label,name,bump,size,tail in [('epoch_tracker','EpochTrackerV1',tb,90,(epoch+1).to_bytes(16,'little')),('debouncer','DebouncerV1',bb,82,bytes(8)),('distribution','DistributionV1',db,98,epoch.to_bytes(16,'little')+gross.to_bytes(8,'little'))]:
  data=m.disc(name)+bytes([bump,1])+config+bytes(input_mint)+tail;assert len(data)==size;accounts[c[label]]=m.account(m.minimum(size),data,m.RELAY)
 if route=='after':accounts[str(receipt)]=m.account(m.minimum(49),m.disc('SwapReceiptV1')+bytes([rb])+bytes(dist)+output.to_bytes(8,'little'),m.RELAY)
 accounts[str(settlement)]=m.account(m.minimum(82),m.mint_data(),m.TOKEN);accounts[str(source)]=m.account(m.minimum(165),m.token_data(settlement,dist,output if route=='after' else gross),m.TOKEN)
 names={**{k:m.Pubkey.from_string(v) for k,v in c.items()},'mint':settlement,'output_mint':settlement,'token_program':m.TOKEN,'output_mint_program':m.TOKEN,'signer':signer,'associated_token_program':m.ATA,'system_program':m.SYSTEM,'program':m.RELAY}
 name='distribute_after_just_swapping_v1' if route=='after' else 'distribute_non_swap_output_mint_v1';idef=next(i for i in json.loads((ROOT/'localnet/relay/idl.json').read_text())['instructions'] if i['name']==name);metas=[m.AccountMeta(names[a['name']],a.get('signer',False),a.get('writable',False)) for a in idef['accounts']];raw=bytes(idef['discriminator'])+(1).to_bytes(4,'little')+b'\0'+bytes(recipient)+(10000).to_bytes(2,'little');proof.pop('source_token_or_temp');proof.update(route=route,epoch=epoch,gross=gross,output=output,distribution_bump=db,recipient=str(recipient),instruction_hex=raw.hex(),instruction_accounts=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas])
 if route=='after':proof['receipt_bump']=rb
 return accounts,m.Instruction(m.RELAY,raw,metas),available,fee,proof,case,base
common=['wrong_relayer','empty_shares','suffix','three_shares','invalid_share_tag','short_arg_count','short_share','short_share_address','short_share_bps','count113_missing','count114_missing','signer_missing','signer_readonly','mint_readonly','source_readonly','source_mint','source_authority','source_owner','source_address','wrong_token_program','distribution_close_alias','debouncer_mint_field','distribution_mint_field','tracker_config_field','tracker_epoch_equal','distribution_uninitialized','remaining_extra','wrong_system','wrong_ata','mint_owner','mint_short']
rows=[];seen=set();requested=[]
for route in ['after','non_swap']:
 count=12 if route=='after' else 11;specs=common+[f'missing_{n}' for n in range(count)]+[f'{name}_{kind}' for name in ['epoch_tracker','debouncer','distribution'] for kind in ['short0','short8','discriminator','owner','invalid_enum','pda']]+['distribution_readonly']
 if route=='after':specs+=['receipt_'+kind for kind in ['short0','short8','discriminator','owner','pda','readonly','distribution','zero_output','close_alias']]
 for kind in specs:
  requested.append([route,kind]);accounts,ix,available,fee,proof,case,base=fixture(route);canonical=copy.deepcopy(proof);metas=list(ix.accounts);c=proof['canonical_pdas'];source=c['output_distribution_token_account' if route=='after' else 'distribution_token_account'];mint_index=5 if route=='after' else 4;signer_index=7 if route=='after' else 5;source_index=4 if route=='after' else 3;program_index=6;ata_index=8 if route=='after' else 7;system_index=9 if route=='after' else 8
  def set_data(k,b):accounts[k]['data_base64']=base64.b64encode(b).decode()
  if kind=='empty_shares':ix=m.Instruction(m.RELAY,bytes(ix.data)[:8]+bytes(4),metas)
  elif kind=='suffix':ix=m.Instruction(m.RELAY,bytes(ix.data)+b'ignored suffix',metas)
  elif kind=='three_shares':
   data=(3).to_bytes(4,'little')+b''.join(bytes([tag])+bytes(m.Pubkey.from_string(proof['recipient']))+bps.to_bytes(2,'little') for tag,bps in [(0,0),(1,2500),(2,7500)]);ix=m.Instruction(m.RELAY,bytes(ix.data)[:8]+data,metas)
  elif kind=='invalid_share_tag':ix=m.Instruction(m.RELAY,bytes(ix.data)[:12]+b'\3'+bytes(ix.data)[13:],metas)
  elif kind in ['short_arg_count','short_share','short_share_address','short_share_bps']:
   size={'short_arg_count':8,'short_share':12,'short_share_address':44,'short_share_bps':46}[kind];ix=m.Instruction(m.RELAY,bytes(ix.data)[:size],metas)
  elif kind in ['count113_missing','count114_missing']:ix=m.Instruction(m.RELAY,bytes(ix.data)[:8]+(113 if kind=='count113_missing' else 114).to_bytes(4,'little')+bytes(ix.data)[12:],metas)
  elif kind=='signer_missing':metas[signer_index]=m.AccountMeta(metas[signer_index].pubkey,False,True)
  elif kind in ['signer_readonly','mint_readonly','source_readonly','distribution_readonly']:
   index={'signer_readonly':signer_index,'mint_readonly':mint_index,'source_readonly':source_index,'distribution_readonly':2}[kind];metas[index]=m.AccountMeta(metas[index].pubkey,metas[index].is_signer,False)
  elif kind in ['source_mint','source_authority']:
   b=base64.b64decode(accounts[source]['data_base64']);off=0 if kind=='source_mint' else 32;set_data(source,b[:off]+bytes(m.pub('distribution-wrong-token-field'))+b[off+32:])
  elif kind=='source_owner':accounts[source]['owner']=str(m.SYSTEM)
  elif kind=='source_address':
   wrong=m.pub('distribution-wrong-source');accounts[str(wrong)]=copy.deepcopy(accounts[source]);metas[source_index]=m.AccountMeta(wrong,False,True)
  elif kind=='wrong_token_program':metas[program_index]=m.AccountMeta(m.SYSTEM,False,False)
  elif kind=='distribution_close_alias':accounts[str(metas[signer_index].pubkey)]=copy.deepcopy(accounts[c['distribution']]);metas[2]=m.AccountMeta(metas[signer_index].pubkey,False,True)
  elif kind in ['debouncer_mint_field','distribution_mint_field','tracker_config_field','tracker_epoch_equal','distribution_uninitialized']:
   label='debouncer' if kind=='debouncer_mint_field' else 'epoch_tracker' if kind.startswith('tracker_') else 'distribution';k=c[label];b=base64.b64decode(accounts[k]['data_base64'])
   if kind.endswith('_mint_field'):set_data(k,b[:42]+bytes(m.pub('distribution-wrong-state-mint'))+b[74:])
   elif kind=='tracker_config_field':set_data(k,b[:10]+bytes(m.pub('distribution-wrong-state-config'))+b[42:])
   elif kind=='tracker_epoch_equal':set_data(k,b[:74]+proof['epoch'].to_bytes(16,'little'))
   else:set_data(k,b[:9]+b'\0'+b[10:])
  elif kind=='remaining_extra':metas.append(m.AccountMeta(available[2].pubkey(),False,False))
  elif kind in ['wrong_system','wrong_ata']:metas[system_index if kind=='wrong_system' else ata_index]=m.AccountMeta(m.TOKEN,False,False)
  elif kind in ['mint_owner','mint_short']:
   k=str(metas[mint_index].pubkey)
   if kind=='mint_owner':accounts[k]['owner']=str(m.SYSTEM)
   else:set_data(k,b'')
  elif kind.startswith('missing_'):metas=metas[:int(kind.split('_')[1])]
  elif kind!='wrong_relayer':
   label,mutation=next((n,kind[len(n)+1:]) for n in ['epoch_tracker','debouncer','distribution','receipt'] if kind.startswith(n+'_'));index={'epoch_tracker':0,'debouncer':1,'distribution':2,'receipt':3}[label];k=c['swap_receipt' if label=='receipt' else label];b=base64.b64decode(accounts[k]['data_base64'])
   if mutation=='short0':set_data(k,b'')
   elif mutation=='short8':set_data(k,b[:8])
   elif mutation=='discriminator':set_data(k,bytes(8)+b[8:])
   elif mutation=='owner':accounts[k]['owner']=str(m.pub('distribution-wrong-owner'))
   elif mutation=='invalid_enum':set_data(k,b[:9]+b'\2'+b[10:])
   elif mutation=='readonly':metas[index]=m.AccountMeta(metas[index].pubkey,False,False)
   elif mutation=='pda':
    wrong=m.pub('distribution-wrong-'+label);accounts[str(wrong)]=copy.deepcopy(accounts[k]);metas[index]=m.AccountMeta(wrong,False,metas[index].is_writable)
   elif mutation=='distribution':set_data(k,b[:9]+bytes(m.pub('distribution-wrong-receipt-distribution'))+b[41:])
   elif mutation=='zero_output':set_data(k,b[:41]+bytes(8))
   elif mutation=='close_alias':accounts[str(metas[signer_index].pubkey)]=copy.deepcopy(accounts[k]);metas[index]=m.AccountMeta(metas[signer_index].pubkey,False,True)
   else:raise AssertionError(mutation)
  ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_hex']=bytes(ix.data).hex();proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas];stimulus={k:proof[k] for k in ['accounts','instruction_hex','instruction_accounts']};digest=H(json.dumps(stimulus,sort_keys=True,separators=(',',':')).encode());assert digest not in seen,(route,kind);seen.add(digest)
  vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
  required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
  tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys);result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']};assert result['original']['error'] is not None
  rows.append(dict(route=route,kind=kind,stimulus_sha256=digest,base_case=case,base_fixture=base,canonical_fixture=canonical,fixture=proof,results=result,mismatches=mismatch));print(route,kind,result['original']['error'],mismatch,flush=True)
  if mismatch['candidate']:break
 if rows[-1]['mismatches']['candidate']:break
report=dict(binary_hashes={n:H(p.read_bytes()) for n,p in paths.items()},requested=requested,cases=rows,all_requested_completed=len(rows)==len(requested) and len(requested)==132,passed=sum(not r['mismatches']['candidate'] for r in rows),unique_input_fixtures=len(seen),scope='Owned signatures, real privileges, blockhash/history checks; fixed relayer never substituted. Parser/rollback rejections only, not privileged distribution-body success. Frozen comparator.')
(P/'distribution-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(requested)
