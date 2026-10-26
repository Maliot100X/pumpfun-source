from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal';sp=importlib.util.spec_from_file_location('close_epoch_frozen_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/shared-donation-source-recovery/shared/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='6dfbc4d8339c9a6046d61cac6ee932fd15838abc73dd0369f7ea70979c4dd45e';assert H(paths['original'].read_bytes())==m.EXPECTED['original'];assert H((proposal/'artifacts/spl_token.so').read_bytes())==m.EXPECTED['token'] and H((proposal/'artifacts/associated_token.so').read_bytes())==m.EXPECTED['ata']
def fixture():
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_v1'));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);config=bytes(ix.data)[16:48];mint=ix.accounts[3].pubkey;epoch=3;gross=4000000;signer=ix.accounts[5].pubkey;c=proof['canonical_pdas'];dist,dist_bump=m.pd([b'distribution_v1',config,bytes(mint),epoch.to_bytes(16,'little')]);dest=m.ata(dist,mint);source=m.ata(m.Pubkey.from_string(c['debouncer']),mint)
 accounts.pop(proof['source_token_or_temp']);accounts.pop(c['mint_whitelist']);accounts.pop(c['debouncer_token_account']);c.pop('mint_whitelist');c['distribution']=str(dist);c['distribution_token_account']=str(dest);c['debouncer_token_account']=str(source)
 for label,disc,size,tail in [('epoch_tracker','EpochTrackerV1',90,epoch.to_bytes(16,'little')),('debouncer','DebouncerV1',82,gross.to_bytes(8,'little'))]:
  _,bump=m.pd([label.encode()+b'_v1',config,bytes(mint)]);data=m.disc(disc)+bytes([bump,1])+config+bytes(mint)+tail;assert len(data)==size;accounts[c[label]]=m.account(m.minimum(size),data,m.RELAY)
 accounts[str(source)]=m.account(m.minimum(165),m.token_data(mint,m.Pubkey.from_string(c['debouncer']),gross),m.TOKEN)
 for k in [dist,dest]:accounts[str(k)]=m.account(0,b'',m.SYSTEM)
 names={**{k:m.Pubkey.from_string(v) for k,v in c.items()},'mint':mint,'token_program':m.TOKEN,'signer':signer,'associated_token_program':m.ATA,'system_program':m.SYSTEM,'program':m.RELAY}
 idef=next(i for i in json.loads((ROOT/'localnet/relay/idl.json').read_text())['instructions'] if i['name']=='close_donation_epoch_v1');metas=[m.AccountMeta(names[a['name']],a.get('signer',False),a.get('writable',False)) for a in idef['accounts']];raw=bytes(idef['discriminator'])+config+epoch.to_bytes(16,'little');ix=m.Instruction(m.RELAY,raw,metas);proof['instruction_hex']=raw.hex();proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas];proof.pop('source_token_or_temp');proof['epoch']=epoch;proof['gross']=gross;proof['distribution_bump']=dist_bump
 return accounts,ix,available,fee,proof,case,base
specs=['wrong_relayer','suffix','distribution_prefunded','distribution_exists','destination_exists','signer_missing','signer_readonly','distribution_readonly','destination_readonly','mint_readonly','debouncer_token_mint','debouncer_token_authority','mint_address','distribution_pda']+[f'missing_{n}' for n in range(12)]+[f'{name}_{kind}' for name in ['epoch_tracker','debouncer'] for kind in ['short0','short8','discriminator','owner','invalid_enum','readonly','pda']];rows=[]
for kind in specs:
 accounts,ix,available,fee,proof,case,base=fixture();canonical=copy.deepcopy(proof);metas=list(ix.accounts);c=proof['canonical_pdas'];mint=metas[5].pubkey
 def set_data(k,b):accounts[k]['data_base64']=base64.b64encode(b).decode()
 if kind=='suffix':ix=m.Instruction(m.RELAY,bytes(ix.data)+b'ignored suffix',metas)
 elif kind=='distribution_prefunded':accounts[c['distribution']]['lamports']=1
 elif kind=='distribution_exists':
  b=m.disc('DistributionV1')+bytes([proof['distribution_bump'],1])+bytes.fromhex(proof['instruction_hex'])[8:40]+bytes(mint)+proof['epoch'].to_bytes(16,'little')+proof['gross'].to_bytes(8,'little');assert len(b)==98;accounts[c['distribution']]=m.account(m.minimum(98),b,m.RELAY)
 elif kind=='destination_exists':accounts[c['distribution_token_account']]=m.account(m.minimum(165),m.token_data(mint,m.Pubkey.from_string(c['distribution']),0),m.TOKEN)
 elif kind=='signer_missing':metas[7]=m.AccountMeta(metas[7].pubkey,False,True)
 elif kind.endswith('_readonly') and kind.split('_')[0] in ['signer','distribution','destination','mint']:
  index={'signer':7,'distribution':0,'destination':1,'mint':5}[kind[:-9]];metas[index]=m.AccountMeta(metas[index].pubkey,metas[index].is_signer,False)
 elif kind in ['debouncer_token_mint','debouncer_token_authority']:
  k=c['debouncer_token_account'];b=base64.b64decode(accounts[k]['data_base64']);off=0 if kind.endswith('_mint') else 32;set_data(k,b[:off]+bytes(m.pub('close-wrong-token-field'))+b[off+32:])
 elif kind=='mint_address':
  k=c['debouncer'];b=base64.b64decode(accounts[k]['data_base64']);set_data(k,b[:42]+bytes(m.pub('close-wrong-mint'))+b[74:])
 elif kind=='distribution_pda':
  key=m.pub('close-wrong-distribution');accounts[str(key)]=m.account(0,b'',m.SYSTEM);metas[0]=m.AccountMeta(key,False,True)
 elif kind.startswith('missing_'):metas=metas[:int(kind.split('_')[1])]
 elif kind!='wrong_relayer':
  label,mutation=next((n,kind[len(n)+1:]) for n in ['epoch_tracker','debouncer'] if kind.startswith(n+'_'));index=2 if label=='epoch_tracker' else 3;k=c[label];b=base64.b64decode(accounts[k]['data_base64'])
  if mutation=='short0':set_data(k,b'')
  elif mutation=='short8':set_data(k,b[:8])
  elif mutation=='discriminator':set_data(k,bytes(8)+b[8:])
  elif mutation=='owner':accounts[k]['owner']=str(m.pub('close-wrong-owner'))
  elif mutation=='invalid_enum':set_data(k,b[:9]+b'\2'+b[10:])
  elif mutation=='readonly':metas[index]=m.AccountMeta(metas[index].pubkey,False,False)
  elif mutation=='pda':
   wrong=m.pub('close-wrong-'+label);accounts[str(wrong)]=copy.deepcopy(accounts[k]);metas[index]=m.AccountMeta(wrong,False,True)
  else:raise AssertionError(mutation)
 ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_hex']=bytes(ix.data).hex();proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas]
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys);result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']};assert result['original']['error'] is not None
 rows.append(dict(kind=kind,base_case=case,base_fixture=base,canonical_fixture=canonical,fixture=proof,results=result,mismatches=mismatch));print(kind,result['original']['error'],mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(binary_hashes={n:H(p.read_bytes()) for n,p in paths.items()},cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not r['mismatches']['candidate'] for r in rows),scope='Owned signatures and real privileges; fixed captured relayer is never substituted. These exercise context/init/rollback rejections through the signer address constraint, not privileged close-body success. Frozen comparator exclusions only.')
(P/'close-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
