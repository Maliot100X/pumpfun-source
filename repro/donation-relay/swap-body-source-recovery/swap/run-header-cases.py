from pathlib import Path
import base64,copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
proposal=ROOT/'repro/donation-relay/local-validation-proposal';spec=importlib.util.spec_from_file_location('relay_frozen_header_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
spec=importlib.util.spec_from_file_location('relay_frozen_header_verify',proposal/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.verify(runtime=True)
paths={'original':proposal/'artifacts/original.so','baseline':ROOT/'repro/donation-relay/decoded-business-origins/message-and-tip/candidate.so','candidate':P/'candidate.so'}
build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged']
assert H(paths['original'].read_bytes())==m.EXPECTED['original']
assert H(paths['baseline'].read_bytes())=='836d2ffbec4c437cf9447138e4e54de886744cf4841aeadb34aaeaf7e0249a8f'
assert H(paths['candidate'].read_bytes())==build['candidate_sha256']
CASES=[('write',2,0,'idl'),('set_buffer_buffer',3,0,'buffer'),('set_buffer_idl',3,1,'idl'),('set_authority',4,0,'idl'),('close',5,0,'account'),('resize',6,0,'idl')]
rows=[]
for label,op,index,account_name in CASES:
 case=copy.deepcopy(next(c for c in m.CASES if c.get('kind')=='idl' and c.get('operation')==op))
 accounts,ix,available,fee,proof=m.prepare(case,ROOT);base_proof=copy.deepcopy(proof);key=proof['instruction_accounts'][index]['pubkey']
 data=base64.b64decode(accounts[key]['data_base64']);assert data[:8]==m.IDL_DISC
 accounts[key]['data_base64']=base64.b64encode(bytes(8)+data[8:]).decode()
 assert proof['accounts']==accounts
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()}
 assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in ix.accounts if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results())
 keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatches={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['baseline','candidate']}
 assert 'Custom(3002)' in result['original']['error'].replace(' ','')
 expected='AnchorError caused by account: '+account_name+'. Error Code: AccountDiscriminatorMismatch. Error Number: 3002. Error Message: Account discriminator did not match what was expected.'
 assert any(log.endswith(expected) for log in result['original']['logs'])
 assert not mismatches['baseline'] and not mismatches['candidate']
 rows.append(dict(name=label,base_case=case,base_fixture=base_proof,fixture=proof,mutation=dict(account=key,index=index,old_discriminator=data[:8].hex(),new_discriminator=bytes(8).hex()),expected_outer_name=account_name,results=result,mismatches=mismatches))
report=dict(harness_sha256=H((proposal/'harness_proposal.py').read_bytes()),binary_hashes={n:H(path.read_bytes()) for n,path in paths.items()},scope='Derived malformed-header tests: exactly eight discriminator bytes changed in existing owned IDL fixtures. Same valid transaction, signatures, privileges, blockhash and comparator for three isolated VMs. No allocator-failure equivalence claim.',normal_signature_blockhash_history_checks=True,cases=rows,all_passed=True)
(P/'header-cases.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(cases=len(rows),candidate_passed=len(rows),baseline_passed=len(rows),submissions=len(rows)*3,whole_byte_identity=False)))
