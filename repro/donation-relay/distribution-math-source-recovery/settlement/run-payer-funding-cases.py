from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal'
sp=importlib.util.spec_from_file_location('relay_payer_funding_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/donation-layout-source-recovery/pubkey/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='4ea6e7fb17caae45252f7fdf109d43f1ceed57b8f640ef6c5f46520d5eeacaac';assert H(paths['original'].read_bytes())==m.EXPECTED['original']
specs=[('payer_readonly','PrivilegeEscalation'),('payer_not_signer',3010),('payer_insufficient',1),('from_one_lamport',None),('payer_alias_from',None)];rows=[]
for label,code in specs:
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_pubkey_config_id_with_payer_v1'));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);metas=list(ix.accounts);assert metas[5].pubkey==m.key('owner').pubkey() and metas[6].pubkey==m.key('separate-payer').pubkey()
 if label=='payer_readonly':metas[6]=m.AccountMeta(metas[6].pubkey,True,False)
 elif label=='payer_not_signer':metas[6]=m.AccountMeta(metas[6].pubkey,False,True)
 elif label=='payer_insufficient':accounts[str(metas[6].pubkey)]['lamports']=1
 elif label=='from_one_lamport':accounts[str(metas[5].pubkey)]['lamports']=1
 elif label=='payer_alias_from':metas[6]=m.AccountMeta(metas[5].pubkey,True,True)
 ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas]
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']}
 if code is None:
  for row in result.values():assert row['error'] is None and not m.check_effects(case,proof,row)
 elif isinstance(code,str):assert code in result['original']['error']
 else:assert 'Custom('+str(code)+')' in result['original']['error'].replace(' ','')
 rows.append(dict(name=label,base_case=case,base_fixture=base,fixture=proof,expected_code=code,results=result,mismatches=mismatch));print(label,mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not r['mismatches']['candidate'] for r in rows),scope='Only separate payer permissions/funding/alias or authority lamports changes on the frozen owned with-payer fixture. Real signatures, aliases, blockhash/history checks and unchanged comparator; no historical authority substitution.')
(P/'payer-funding-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
