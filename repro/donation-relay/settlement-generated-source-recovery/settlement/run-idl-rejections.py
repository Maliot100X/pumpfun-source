from pathlib import Path
import base64,copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
proposal=ROOT/'repro/donation-relay/local-validation-proposal';s=importlib.util.spec_from_file_location('idl_rejection_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
s=importlib.util.spec_from_file_location('idl_rejection_verify',proposal/'verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);v.verify(runtime=True)
paths={'original':proposal/'artifacts/original.so','control':ROOT/'work/relay-full-errors-v148/candidate.so','candidate':P/'candidate.so'}
assert H(paths['original'].read_bytes())==m.EXPECTED['original']
assert H(paths['control'].read_bytes())=='3a0acce9ba33b33132cb4fe40d909cd8e7524ffbea0e488a567b12d94724c46f'
assert H(paths['candidate'].read_bytes())==json.loads((P/'build-result.json').read_text())['candidate_sha256']
cases=[('short0','truncate',0,3001),('short7','truncate',7,3001),('short8','truncate',8,3003),('short39','truncate',39,3003),('short43','truncate',43,3003),('wrong_owner','owner',None,3007),('uninitialized','uninitialized',None,3012),('wrong_authority','authority',None,2001),('readonly','readonly',None,2000)]
rows=[]
for label,kind,value,expected in cases:
 case=copy.deepcopy(next(c for c in m.CASES if c.get('operation')==2 and c.get('kind')=='idl'))
 accounts,ix,available,fee,proof=m.prepare(case,ROOT);base_fixture=copy.deepcopy(proof);target=proof['instruction_accounts'][0]['pubkey'];data=base64.b64decode(accounts[target]['data_base64'])
 if kind=='truncate':accounts[target]['data_base64']=base64.b64encode(data[:value]).decode()
 elif kind=='owner':accounts[target]['owner']=str(m.pub('rejection-wrong-owner'))
 elif kind=='uninitialized':accounts[target]['owner']=str(m.SYSTEM);accounts[target]['lamports']=0;accounts[target]['data_base64']=''
 elif kind=='authority':accounts[target]['data_base64']=base64.b64encode(data[:8]+bytes(m.pub('rejection-wrong-authority'))+data[40:]).decode()
 elif kind=='readonly':
  metas=list(ix.accounts);metas[0]=m.AccountMeta(metas[0].pubkey,metas[0].is_signer,False);ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_accounts'][0]['writable']=False
 else:raise AssertionError(kind)
 assert proof['accounts']==accounts
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in ix.accounts if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']}
 assert 'Custom('+str(expected)+')' in result['original']['error'].replace(' ','')
 rows.append(dict(name=label,case=case,base_fixture=base_fixture,fixture=proof,mutation=dict(kind=kind,value=value,account=target),expected_code=expected,results=result,mismatches=mismatch))
 print(label,mismatch,flush=True)
 if any(mismatch.values()):break
report=dict(harness_sha256=H((proposal/'harness_proposal.py').read_bytes()),binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},cases=rows,all_requested_completed=len(rows)==len(cases),scope='Nine derived owned IDL-write rejection fixtures, changing only specified data/owner/lamports/one writable meta. Same valid normally signed transaction in three isolated VMs; frozen comparator, signature/blockhash/history checks and stop on first mismatch.',passed=sum(not any(x['mismatches'].values()) for x in rows))
(P/'idl-rejections.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(rows)
