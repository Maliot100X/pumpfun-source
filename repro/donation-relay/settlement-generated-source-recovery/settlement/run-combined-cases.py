from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal';sp=importlib.util.spec_from_file_location('combined_frozen_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/swap-body-source-recovery/swap/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='53fe5b68ce2eba3634912ac86637a99f342c0884b0d2578d8702282a50b29893';assert H(paths['original'].read_bytes())==m.EXPECTED['original'];assert H((proposal/'artifacts/spl_token.so').read_bytes())==m.EXPECTED['token'] and H((proposal/'artifacts/associated_token.so').read_bytes())==m.EXPECTED['ata']
def fixture():
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_v1'));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);config=bytes(ix.data)[16:48];mint=ix.accounts[3].pubkey;epoch=3;gross=4000000;signer=ix.accounts[5].pubkey;c=proof['canonical_pdas'];dist,db=m.pd([b'distribution_v1',config,bytes(mint),epoch.to_bytes(16,'little')]);output=m.Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');source=m.ata(dist,mint);dest=m.ata(dist,output);jupiter=m.Pubkey.from_string('JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4')
 for k in [proof['source_token_or_temp'],c['mint_whitelist'],c['debouncer_token_account']]:accounts.pop(k)
 for k in ['mint_whitelist','debouncer_token_account']:c.pop(k)
 c.update(distribution=str(dist),distribution_token_account=str(source),output_distribution_token_account=str(dest))
 for label,disc,size,tail in [('epoch_tracker','EpochTrackerV1',90,(epoch+1).to_bytes(16,'little')),('debouncer','DebouncerV1',82,bytes(8)),('distribution','DistributionV1',98,epoch.to_bytes(16,'little')+gross.to_bytes(8,'little'))]:
  bump=db if label=='distribution' else m.pd([label.encode()+b'_v1',config,bytes(mint)])[1];data=m.disc(disc)+bytes([bump,1])+config+bytes(mint)+tail;assert len(data)==size;accounts[c[label]]=m.account(m.minimum(size),data,m.RELAY)
 accounts[str(source)]=m.account(m.minimum(165),m.token_data(mint,dist,gross),m.TOKEN);accounts[str(output)]=m.account(m.minimum(82),m.mint_data(),m.TOKEN)
 for k in [dest,jupiter]:accounts[str(k)]=m.account(0,b'',m.SYSTEM)
 names={**{k:m.Pubkey.from_string(v) for k,v in c.items()},'mint':mint,'output_mint':output,'output_mint_program':m.TOKEN,'token_program':m.TOKEN,'jupiter_program':jupiter,'signer':signer,'associated_token_program':m.ATA,'system_program':m.SYSTEM,'program':m.RELAY}
 idef=next(i for i in json.loads((ROOT/'localnet/relay/idl.json').read_text())['instructions'] if i['name']=='swap_then_distribute_v1');metas=[m.AccountMeta(names[a['name']],a.get('signer',False),a.get('writable',False)) for a in idef['accounts']];raw=bytes(idef['discriminator'])+bytes(4)+(1).to_bytes(4,'little')+b'\0'+bytes(available[2].pubkey())+(10000).to_bytes(2,'little');ix=m.Instruction(m.RELAY,raw,metas);proof.pop('source_token_or_temp');proof.update(instruction_hex=raw.hex(),instruction_accounts=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas],epoch=epoch,gross=gross,distribution_bump=db)
 return accounts,ix,available,fee,proof,case,base
specs=['wrong_relayer','empty_shares','suffix','three_shares','invalid_share_tag','short_data_count','short_swap_data','short_share_count','short_share','short_share_address','short_share_bps','count113_missing','destination_prefunded','destination_exists','signer_missing','signer_readonly','distribution_readonly','destination_readonly','source_readonly','mint_readonly','output_mint_readonly','input_token_mint','input_token_authority','input_token_owner','mint_address','output_mint_address','debouncer_mint_field','jupiter_address','wrong_token_program','wrong_output_program','wrong_system','wrong_ata','distribution_uninitialized','tracker_epoch_equal','remaining_extra']+[f'missing_{i}' for i in range(15)]+[f'{name}_{kind}' for name in ['epoch_tracker','debouncer','distribution'] for kind in ['short0','short8','discriminator','owner','invalid_enum','pda']];rows=[];seen=set()
for kind in specs:
 accounts,ix,available,fee,proof,case,base=fixture();canonical=copy.deepcopy(proof);metas=list(ix.accounts);c=proof['canonical_pdas'];recipient=available[2].pubkey()
 def set_data(k,b):accounts[k]['data_base64']=base64.b64encode(b).decode()
 if kind=='empty_shares':ix=m.Instruction(m.RELAY,bytes(ix.data)[:12]+bytes(4),metas)
 elif kind=='suffix':ix=m.Instruction(m.RELAY,bytes(ix.data)+b'ignored suffix',metas)
 elif kind=='three_shares':ix=m.Instruction(m.RELAY,bytes(ix.data)[:12]+(3).to_bytes(4,'little')+b''.join(bytes([tag])+bytes(recipient)+bps.to_bytes(2,'little') for tag,bps in [(0,0),(1,2500),(2,7500)]),metas)
 elif kind=='invalid_share_tag':ix=m.Instruction(m.RELAY,bytes(ix.data)[:16]+b'\3'+bytes(ix.data)[17:],metas)
 elif kind=='short_data_count':ix=m.Instruction(m.RELAY,bytes(ix.data)[:8],metas)
 elif kind=='short_swap_data':ix=m.Instruction(m.RELAY,bytes(ix.data)[:8]+(2).to_bytes(4,'little')+b'x',metas)
 elif kind in ['short_share_count','short_share','short_share_address','short_share_bps']:
  size={'short_share_count':15,'short_share':16,'short_share_address':48,'short_share_bps':50}[kind];ix=m.Instruction(m.RELAY,bytes(ix.data)[:size],metas)
 elif kind=='count113_missing':ix=m.Instruction(m.RELAY,bytes(ix.data)[:12]+(113).to_bytes(4,'little')+bytes(ix.data)[16:],metas)
 elif kind=='destination_prefunded':accounts[c['output_distribution_token_account']]['lamports']=1
 elif kind=='destination_exists':accounts[c['output_distribution_token_account']]=m.account(m.minimum(165),m.token_data(metas[6].pubkey,metas[2].pubkey,0),m.TOKEN)
 elif kind=='signer_missing':metas[8]=m.AccountMeta(metas[8].pubkey,False,True)
 elif kind in ['signer_readonly','distribution_readonly','destination_readonly','source_readonly','mint_readonly','output_mint_readonly']:
  index={'signer_readonly':8,'distribution_readonly':2,'destination_readonly':4,'source_readonly':3,'mint_readonly':5,'output_mint_readonly':6}[kind];metas[index]=m.AccountMeta(metas[index].pubkey,metas[index].is_signer,False)
 elif kind in ['input_token_mint','input_token_authority']:
  k=c['distribution_token_account'];b=base64.b64decode(accounts[k]['data_base64']);off=0 if kind.endswith('_mint') else 32;set_data(k,b[:off]+bytes(m.pub('combined-wrong-token-field'))+b[off+32:])
 elif kind=='input_token_owner':accounts[c['distribution_token_account']]['owner']=str(m.SYSTEM)
 elif kind in ['mint_address','output_mint_address']:
  index=5 if kind=='mint_address' else 6;wrong=m.pub('combined-wrong-mint-address');accounts[str(wrong)]=copy.deepcopy(accounts[str(metas[index].pubkey)]);metas[index]=m.AccountMeta(wrong,False,True)
 elif kind=='debouncer_mint_field':
  k=c['debouncer'];b=base64.b64decode(accounts[k]['data_base64']);set_data(k,b[:42]+bytes(m.pub('combined-wrong-debouncer-mint'))+b[74:])
 elif kind=='jupiter_address':
  wrong=m.pub('combined-wrong-jupiter');accounts[str(wrong)]=copy.deepcopy(accounts[str(metas[10].pubkey)]);metas[10]=m.AccountMeta(wrong,False,False)
 elif kind in ['wrong_token_program','wrong_output_program','wrong_system','wrong_ata']:
  index={'wrong_token_program':9,'wrong_output_program':7,'wrong_system':12,'wrong_ata':11}[kind];metas[index]=m.AccountMeta(m.SYSTEM if 'program' in kind else m.TOKEN,False,False)
 elif kind in ['distribution_uninitialized','tracker_epoch_equal']:
  k=c['distribution' if kind=='distribution_uninitialized' else 'epoch_tracker'];b=base64.b64decode(accounts[k]['data_base64']);set_data(k,b[:9]+b'\0'+b[10:] if kind=='distribution_uninitialized' else b[:74]+proof['epoch'].to_bytes(16,'little'))
 elif kind=='remaining_extra':metas.append(m.AccountMeta(available[2].pubkey(),False,False))
 elif kind.startswith('missing_'):metas=metas[:int(kind.split('_')[1])]
 elif kind!='wrong_relayer':
  label,mutation=next((n,kind[len(n)+1:]) for n in ['epoch_tracker','debouncer','distribution'] if kind.startswith(n+'_'));index={'epoch_tracker':0,'debouncer':1,'distribution':2}[label];k=c[label];b=base64.b64decode(accounts[k]['data_base64'])
  if mutation=='short0':set_data(k,b'')
  elif mutation=='short8':set_data(k,b[:8])
  elif mutation=='discriminator':set_data(k,bytes(8)+b[8:])
  elif mutation=='owner':accounts[k]['owner']=str(m.pub('combined-wrong-owner'))
  elif mutation=='invalid_enum':set_data(k,b[:9]+b'\2'+b[10:])
  elif mutation=='pda':
   wrong=m.pub('combined-wrong-'+label);accounts[str(wrong)]=copy.deepcopy(accounts[k]);metas[index]=m.AccountMeta(wrong,False,metas[index].is_writable)
  else:raise AssertionError(mutation)
 ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_hex']=bytes(ix.data).hex();proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas];stimulus={k:proof[k] for k in ['accounts','instruction_hex','instruction_accounts']};digest=H(json.dumps(stimulus,sort_keys=True,separators=(',',':')).encode());assert digest not in seen,kind;seen.add(digest)
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys);result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']};assert result['original']['error'] is not None
 rows.append(dict(kind=kind,stimulus_sha256=digest,base_case=case,base_fixture=base,canonical_fixture=canonical,fixture=proof,results=result,mismatches=mismatch));print(kind,result['original']['error'],mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(binary_hashes={n:H(p.read_bytes()) for n,p in paths.items()},cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not r['mismatches']['candidate'] for r in rows),unique_input_fixtures=len(seen),scope='Owned signatures and real privileges; fixed captured relayer is never substituted. These exercise context/init/rollback rejections through the signer address constraint, not privileged combined-body success. Frozen comparator exclusions only.')
(P/'combined-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
