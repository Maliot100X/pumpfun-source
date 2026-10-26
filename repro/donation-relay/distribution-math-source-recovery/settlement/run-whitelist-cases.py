from pathlib import Path
import copy,base64,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal'
sp=importlib.util.spec_from_file_location('relay_whitelist_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
sp=importlib.util.spec_from_file_location('relay_whitelist_verify',proposal/'verify.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v);v.verify(runtime=True)
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/business-wire-source-recovery/framework-writer/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='4be6d422c4b8879c06239a2c47b0e4fe7c7ef131acdb018da4284a036672ca0e';assert H(paths['original'].read_bytes())==m.EXPECTED['original']
specs=[('owned_wrong_relayer','none',None,2012),('readonly_whitelist','readonly_whitelist',None,2000),('bad_discriminator','discriminator',None,3002),('short0','truncate',0,3001),('short8','truncate',8,3003),('wrong_owner','owner',None,3007),('wrong_pda','pda',None,2006),('wrong_space','truncate',1036,2019),('rent_deficit','rent',None,2005),('readonly_signer','readonly_signer',None,2000),('not_signer','not_signer',None,3010),('wrong_system','system',None,3008),('missing0','missing',0,3005),('missing1','missing',1,3005),('missing2','missing',2,3005),('initialize_create','initialize_create',None,2012),('initialize_prefunded','initialize_prefunded',None,2012),('initialize_insufficient','initialize_insufficient',None,1)]
rows=[]
for label,kind,value,expected in specs:
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_v1'));accounts,old_ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);whitelist=m.Pubkey.from_string(proof['canonical_pdas']['mint_whitelist']);signer=m.key('owner').pubkey();metas=[m.AccountMeta(whitelist,False,True),m.AccountMeta(signer,True,True),m.AccountMeta(m.SYSTEM,False,False)];mutation={'kind':kind,'value':value,'account':str(whitelist)}
 if kind.startswith('initialize_'):
  accounts[str(whitelist)].update(owner=str(m.SYSTEM),data_base64='',lamports=1 if kind=='initialize_prefunded' else 0)
  if kind=='initialize_insufficient':accounts[str(signer)]['lamports']=1
 elif kind=='readonly_whitelist':metas[0]=m.AccountMeta(whitelist,False,False)
 elif kind=='discriminator':
  b=base64.b64decode(accounts[str(whitelist)]['data_base64']);accounts[str(whitelist)]['data_base64']=base64.b64encode(bytes(8)+b[8:]).decode()
 elif kind=='truncate':accounts[str(whitelist)]['data_base64']=base64.b64encode(base64.b64decode(accounts[str(whitelist)]['data_base64'])[:value]).decode()
 elif kind=='owner':accounts[str(whitelist)]['owner']=str(m.pub('whitelist-wrong-owner'))
 elif kind=='pda':
  wrong=m.pub('whitelist-wrong-pda');accounts[str(wrong)]=copy.deepcopy(accounts[str(whitelist)]);metas[0]=m.AccountMeta(wrong,False,True);mutation['new_account']=str(wrong)
 elif kind=='rent':accounts[str(whitelist)]['lamports']-=1
 elif kind=='readonly_signer':metas[1]=m.AccountMeta(signer,True,False)
 elif kind=='not_signer':metas[1]=m.AccountMeta(signer,False,True)
 elif kind=='system':
  wrong=m.pub('whitelist-wrong-system');accounts[str(wrong)]=m.account(1,b'',m.SYSTEM);metas[2]=m.AccountMeta(wrong,False,False);mutation['new_account']=str(wrong)
 elif kind=='missing':metas=metas[:value]
 elif kind!='none':raise AssertionError(kind)
 data=bytes([209,133,253,12,80,9,231,128])+bytes(4);ix=m.Instruction(m.RELAY,data,metas);proof['instruction_hex']=data.hex();proof['instruction_accounts']=[{'pubkey':str(x.pubkey),'signer':x.is_signer,'writable':x.is_writable} for x in metas]
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in ix.accounts if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']};assert 'Custom('+str(expected)+')' in result['original']['error'].replace(' ','')
 rows.append(dict(name=label,base_case=case,base_fixture=base,fixture=proof,mutation=mutation,expected_code=expected,results=result,mismatches=mismatch));print(label,mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(harness_sha256=H((proposal/'harness_proposal.py').read_bytes()),binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not x['mismatches']['candidate'] for x in rows),scope='Owned whitelist/account fixtures and real ephemeral signatures only. The historical relayer key is never replaced, signer privileges are never invented, and all cases must reject before business success. The earlier manual control may differ; all its differences remain recorded. Original/candidate comparison is mandatory. Frozen comparator and normal signature/blockhash/history checks remain enabled.')
(P/'whitelist-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
