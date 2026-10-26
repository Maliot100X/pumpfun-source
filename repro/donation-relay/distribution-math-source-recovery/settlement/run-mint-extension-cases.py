from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal'
sp=importlib.util.spec_from_file_location('relay_mint_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
TOKEN22=m.Pubkey.from_string('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb');token22=ROOT/'evidence/dependencies/spl_token_2022/deployed.so';assert H(token22.read_bytes())=='15a2e615a42e20f31714bbaaee43002ae6f1cda2e8d7118243117ab3c1342e2d'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/native-generated-source-recovery/native/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='087057598554b4ced10f0d499362013374fdbf8ea20d4b52ac228a0007a86a5a';assert H(paths['original'].read_bytes())==m.EXPECTED['original']
def tlv(ty,value):return ty.to_bytes(2,'little')+len(value).to_bytes(2,'little')+value
def variant(ty,n,at=None,value=None):
 b=bytearray(n)
 if at is not None:b[at:at+len(value)]=value
 return tlv(ty,b)
key=bytes(m.pub('mint-policy-authority'));specs=[dict(name='base',tlv=None,expected=None),dict(name='empty_extension_header',tlv=b'\0',expected=None)]
for name,ty,n,at,value,expected in [
 ('fee_zero',1,108,None,None,None),('fee_config_authority',1,108,0,key,6031),('fee_withdraw_authority',1,108,32,key,None),('fee_older_bps',1,108,88,b'\x01\0',6031),('fee_newer_bps',1,108,106,b'\x01\0',6031),
 ('hook_none',14,64,None,None,None),('hook_authority',14,64,0,key,6031),('hook_program',14,64,32,key,6031),('permanent_delegate_zero',12,32,None,None,6031),('permanent_delegate_key',12,32,0,key,6031),
 ('mint_close_none',3,32,None,None,None),('mint_close_some',3,32,0,key,6031),('default_initialized',6,1,0,b'\x01',None),('default_frozen',6,1,0,b'\x02',6031),('default_uninitialized',6,1,0,b'\0',6031),('nontransferable',9,0,None,None,6031),
 ('fee_wrong_length',1,107,None,None,None),('unknown_extension',28,0,None,None,None)]:specs.append(dict(name=name,tlv=variant(ty,n,at,value),expected=expected))
for which in ['mint','freeze']:specs.append(dict(name=which+'_authority',tlv=None,authority=which,expected=6031))
specs.append(dict(name='whitelisted_fee_authority',tlv=variant(1,108,0,key),whitelist=True,expected=None))
specs.extend([
 dict(name='scaled_ui_then_fee_authority',tlv=variant(25,56)+variant(1,108,0,key),expected=6031),
 dict(name='pausable_then_hook_authority',tlv=variant(26,33)+variant(14,64,0,key),expected=6031),
 dict(name='scaled_ui_then_delegate',tlv=variant(25,56)+variant(12,32),expected=6031),
 dict(name='unknown_then_fee_authority',tlv=variant(28,0)+variant(1,108,0,key),expected=None),
])
rows=[]
for spec in specs:
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_v1'));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);metas=list(ix.accounts);mint=metas[3].pubkey;deb=metas[1].pubkey;owner=metas[5].pubkey
 def atakey(authority):return m.Pubkey.find_program_address([bytes(authority),bytes(TOKEN22),bytes(mint)],m.ATA)[0]
 target=atakey(deb);source=atakey(owner)
 for i,k in [(2,target),(4,source),(8,TOKEN22)]:metas[i]=m.AccountMeta(k,metas[i].is_signer,metas[i].is_writable)
 accounts.pop(proof['source_token_or_temp']);accounts.pop(proof['canonical_pdas']['debouncer_token_account']);proof['source_token_or_temp']=str(source);proof['canonical_pdas']['debouncer_token_account']=str(target)
 data=bytearray(m.mint_data())
 if spec.get('authority'):
  off=0 if spec['authority']=='mint' else 46;data[off:off+4]=(1).to_bytes(4,'little');data[off+4:off+36]=key
 if spec['tlv'] is not None:data+=bytes(83)+b'\x01'+spec['tlv']
 accounts[str(mint)]=m.account(m.minimum(len(data)),bytes(data),TOKEN22)
 # Initialized fee-aware accounts isolate the policy from ATA creation. All zero withheld balances.
 for k,authority,amount in [(source,owner,10**9),(target,deb,0)]:
  b=m.token_data(mint,authority,amount)+b'\x02'+tlv(2,bytes(8));accounts[str(k)]=m.account(m.minimum(len(b)),b,TOKEN22)
 if spec.get('whitelist'):
  k=str(metas[6].pubkey);b=base64.b64decode(accounts[k]['data_base64']);b=b[:9]+(1).to_bytes(4,'little')+bytes(mint)+b[45:];accounts[k]['data_base64']=base64.b64encode(b).decode()
 ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas]
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()}
 for vm in vms.values():vm.add_program_from_file(TOKEN22,token22)
 assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']}
 effects={}
 for n,row in result.items():
  if spec['expected'] is None:
   assert row['error'] is None,(spec['name'],n,row['error'],row['logs']);effects[n]=m.check_effects(case,proof,row);assert not effects[n]
  else:assert ('Custom('+str(spec['expected'])+')') in row['error'].replace(' ',''),(spec['name'],n,row['error'])
 serial={k:(v.hex() if k=='tlv' and v is not None else v) for k,v in spec.items()}
 rows.append(dict(spec=serial,base_case=case,base_fixture=base,fixture=proof,results=result,mismatches=mismatch,independent_effects=effects));print(spec['name'],result['original']['error'],mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},token2022_sha256=H(token22.read_bytes()),cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not r['mismatches']['candidate'] for r in rows),scope='Owned finite Token-2022 mint-policy fixtures with initialized canonical source/destination ATAs. Real captured Token-2022 program, real signatures, privileges, effects/rollback and frozen comparator. No generalized runtime/whole-byte closure.')
(P/'mint-extension-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
