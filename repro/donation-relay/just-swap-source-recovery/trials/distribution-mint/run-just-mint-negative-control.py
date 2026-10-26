from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal';sp=importlib.util.spec_from_file_location('just_swap_frozen_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/epoch-close-source-recovery/close/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='e2f674655d6cf2b24b7abfd57fbd789b7cb664e055904f0c73e1679844b622e3';assert H(paths['original'].read_bytes())==m.EXPECTED['original'];assert H((proposal/'artifacts/spl_token.so').read_bytes())==m.EXPECTED['token'] and H((proposal/'artifacts/associated_token.so').read_bytes())==m.EXPECTED['ata']
def fixture():
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_v1'));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);config=bytes(ix.data)[16:48];mint=ix.accounts[3].pubkey;epoch=3;gross=4000000;signer=ix.accounts[5].pubkey;c=proof['canonical_pdas'];dist,db=m.pd([b'distribution_v1',config,bytes(mint),epoch.to_bytes(16,'little')]);receipt,rb=m.pd([b'swap_receipt_v1',bytes(dist)]);output=m.Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');source=m.ata(dist,mint);dest=m.ata(dist,output);jupiter=m.Pubkey.from_string('JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4')
 for k in [proof['source_token_or_temp'],c['mint_whitelist'],c['debouncer_token_account']]:accounts.pop(k)
 for k in ['mint_whitelist','debouncer_token_account']:c.pop(k)
 c.update(distribution=str(dist),swap_receipt=str(receipt),distribution_token_account=str(source),output_distribution_token_account=str(dest))
 for label,disc,size,tail in [('epoch_tracker','EpochTrackerV1',90,(epoch+1).to_bytes(16,'little')),('debouncer','DebouncerV1',82,bytes(8)),('distribution','DistributionV1',98,epoch.to_bytes(16,'little')+gross.to_bytes(8,'little'))]:
  bump=db if label=='distribution' else m.pd([label.encode()+b'_v1',config,bytes(mint)])[1];data=m.disc(disc)+bytes([bump,1])+config+bytes(mint)+tail;assert len(data)==size;accounts[c[label]]=m.account(m.minimum(size),data,m.RELAY)
 accounts[str(source)]=m.account(m.minimum(165),m.token_data(mint,dist,gross),m.TOKEN);accounts[str(output)]=m.account(m.minimum(82),m.mint_data(),m.TOKEN)
 for k in [receipt,dest,jupiter]:accounts[str(k)]=m.account(0,b'',m.SYSTEM)
 names={**{k:m.Pubkey.from_string(v) for k,v in c.items()},'mint':mint,'output_mint':output,'output_mint_program':m.TOKEN,'token_program':m.TOKEN,'jupiter_program':jupiter,'signer':signer,'associated_token_program':m.ATA,'system_program':m.SYSTEM,'program':m.RELAY}
 idef=next(i for i in json.loads((ROOT/'localnet/relay/idl.json').read_text())['instructions'] if i['name']=='just_swap_v1');metas=[m.AccountMeta(names[a['name']],a.get('signer',False),a.get('writable',False)) for a in idef['accounts']];raw=bytes(idef['discriminator'])+bytes(4);ix=m.Instruction(m.RELAY,raw,metas);proof.pop('source_token_or_temp');proof.update(instruction_hex=raw.hex(),instruction_accounts=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas],epoch=epoch,gross=gross,distribution_bump=db,receipt_bump=rb)
 return accounts,ix,available,fee,proof,case,base
specs=['wrong_relayer','suffix','receipt_prefunded','receipt_exists','destination_exists','signer_missing','signer_readonly','receipt_readonly','distribution_readonly','destination_readonly','mint_readonly','output_mint_readonly','input_token_mint','input_token_authority','output_mint_address','mint_address','receipt_pda','distribution_pda','jupiter_address','debouncer_mint_field']+[f'missing_{n}' for n in range(16)]+[f'{name}_{kind}' for name in ['epoch_tracker','debouncer','distribution'] for kind in ['short0','short8','discriminator','owner','invalid_enum','readonly','pda']];specs=list(dict.fromkeys(specs));rows=[]
specs=['debouncer_mint_field']
for kind in specs:
 accounts,ix,available,fee,proof,case,base=fixture();canonical=copy.deepcopy(proof);metas=list(ix.accounts);c=proof['canonical_pdas']
 def set_data(k,b):accounts[k]['data_base64']=base64.b64encode(b).decode()
 if kind=='suffix':ix=m.Instruction(m.RELAY,bytes(ix.data)+b'ignored suffix',metas)
 elif kind=='receipt_prefunded':accounts[c['swap_receipt']]['lamports']=1
 elif kind=='receipt_exists':accounts[c['swap_receipt']]=m.account(m.minimum(49),m.disc('SwapReceiptV1')+bytes([proof['receipt_bump']])+bytes(metas[2].pubkey)+proof['gross'].to_bytes(8,'little'),m.RELAY)
 elif kind=='destination_exists':accounts[c['output_distribution_token_account']]=m.account(m.minimum(165),m.token_data(metas[7].pubkey,metas[2].pubkey,0),m.TOKEN)
 elif kind=='signer_missing':metas[9]=m.AccountMeta(metas[9].pubkey,False,True)
 elif kind in ['signer_readonly','receipt_readonly','distribution_readonly','destination_readonly','mint_readonly','output_mint_readonly']:
  index={'signer':9,'receipt':3,'distribution':2,'destination':5,'mint':6,'output_mint':7}[kind[:-9]];metas[index]=m.AccountMeta(metas[index].pubkey,metas[index].is_signer,False)
 elif kind in ['input_token_mint','input_token_authority']:
  k=c['distribution_token_account'];b=base64.b64decode(accounts[k]['data_base64']);off=0 if kind.endswith('_mint') else 32;set_data(k,b[:off]+bytes(m.pub('just-wrong-token-field'))+b[off+32:])
 elif kind=='debouncer_mint_field':
  k=c['debouncer'];b=base64.b64decode(accounts[k]['data_base64']);set_data(k,b[:42]+bytes(m.pub('just-wrong-debouncer-mint'))+b[74:])
 elif kind in ['mint_address','output_mint_address']:
  index=6 if kind=='mint_address' else 7;wrong=m.pub('just-wrong-mint-address');accounts[str(wrong)]=copy.deepcopy(accounts[str(metas[index].pubkey)]);metas[index]=m.AccountMeta(wrong,False,True)
 elif kind in ['receipt_pda','distribution_pda','jupiter_address']:
  index={'receipt_pda':3,'distribution_pda':2,'jupiter_address':11}[kind];wrong=m.pub('just-'+kind);accounts[str(wrong)]=copy.deepcopy(accounts[str(metas[index].pubkey)]);metas[index]=m.AccountMeta(wrong,False,metas[index].is_writable)
 elif kind.startswith('missing_'):metas=metas[:int(kind.split('_')[1])]
 elif kind!='wrong_relayer':
  label,mutation=next((n,kind[len(n)+1:]) for n in ['epoch_tracker','debouncer','distribution'] if kind.startswith(n+'_'));index={'epoch_tracker':0,'debouncer':1,'distribution':2}[label];k=c[label];b=base64.b64decode(accounts[k]['data_base64'])
  if mutation=='short0':set_data(k,b'')
  elif mutation=='short8':set_data(k,b[:8])
  elif mutation=='discriminator':set_data(k,bytes(8)+b[8:])
  elif mutation=='owner':accounts[k]['owner']=str(m.pub('just-wrong-owner'))
  elif mutation=='invalid_enum':set_data(k,b[:9]+b'\2'+b[10:])
  elif mutation=='readonly':metas[index]=m.AccountMeta(metas[index].pubkey,False,False)
  elif mutation=='pda':
   wrong=m.pub('just-wrong-'+label);accounts[str(wrong)]=copy.deepcopy(accounts[k]);metas[index]=m.AccountMeta(wrong,False,metas[index].is_writable)
  else:raise AssertionError(mutation)
 ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_hex']=bytes(ix.data).hex();proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas]
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys);result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']};assert result['original']['error'] is not None
 rows.append(dict(kind=kind,base_case=case,base_fixture=base,canonical_fixture=canonical,fixture=proof,results=result,mismatches=mismatch));print(kind,result['original']['error'],mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(binary_hashes={n:H(p.read_bytes()) for n,p in paths.items()},cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not r['mismatches']['candidate'] for r in rows),scope='Owned signatures and real privileges; fixed captured relayer is never substituted. These exercise context/init/rollback rejections through the signer address constraint, not privileged swap-body success. Frozen comparator exclusions only.')
(P/'just-mint-negative-control.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
