from pathlib import Path
import copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
proposal=ROOT/'repro/donation-relay/local-validation-proposal';sp=importlib.util.spec_from_file_location('relay_idl_wire_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
sp=importlib.util.spec_from_file_location('relay_idl_wire_verify',proposal/'verify.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v);v.verify(runtime=True)
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/idl-owned-abi-recovery/pubkey-type/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='880ee38d64e196d430fb1c3ea3713674c014e579da6b40762a7898480419b98b';assert H(paths['original'].read_bytes())==m.EXPECTED['original']
cases=[('no_tag',b'',102),('bad_tag',b'\xff',102),('create_short',b'\0'+bytes(7),102),('write_short',b'\2'+(10).to_bytes(4,'little')+b'x',102),('authority_short',b'\4'+bytes(31),102),('resize_short',b'\6'+bytes(7),102),('write_prefix_suffix',None,None)]
rows=[]
for label,args,error in cases:
 case=copy.deepcopy(next(c for c in m.CASES if c.get('kind')=='idl' and c.get('operation')==2));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof)
 data=bytes(ix.data)+b'ignored suffix' if args is None else m.IDL_SELECTOR+args
 ix=m.Instruction(m.RELAY,data,list(ix.accounts));proof['instruction_hex']=data.hex()
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in ix.accounts if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']}
 if error is not None:assert 'Custom('+str(error)+')' in result['original']['error'].replace(' ','')
 else:
  for row in result.values():assert row['error'] is None and not m.check_effects(case,proof,row)
 rows.append(dict(name=label,base_case=case,base_fixture=base,fixture=proof,mutated_args_hex=None if args is None else args.hex(),suffix_hex=(b'ignored suffix').hex() if args is None else None,expected_error=error,results=result,mismatches=mismatch));print(label,mismatch,flush=True)
 if any(mismatch.values()):break
report=dict(harness_sha256=H((proposal/'harness_proposal.py').read_bytes()),binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},cases=rows,all_requested_completed=len(rows)==len(cases),passed=sum(not any(r['mismatches'].values()) for r in rows),scope='Only instruction-data prefix/truncation/suffix changes in the frozen owned IDL-write fixture; normal signatures/blockhash/history and frozen comparator. Same signed transaction in three VMs; no allocation-failure equivalence claim.')
(P/'instruction-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(cases)
