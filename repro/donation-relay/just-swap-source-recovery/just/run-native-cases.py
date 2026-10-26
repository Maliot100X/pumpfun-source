from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal'
sp=importlib.util.spec_from_file_location('relay_native_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/payer-generated-source-recovery/payer/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='54b75f94118f3ccbdffba7a76bca6d9375a49ac261d2d47448eb4427709e6eb5';assert H(paths['original'].read_bytes())==m.EXPECTED['original']
rows=[];specs=[(name,kind) for name in ['donate_native_v1','donate_native_pubkey_config_id_v1'] for kind in ['prefunded','prefunded_excess','message_long','tip_large','insufficient_from','wrong_temp_pda','temp_readonly','wrong_native_mint']]
for name,kind in specs:
 case=copy.deepcopy(next(c for c in m.CASES if c['name']==(name if kind!='wrong_native_mint' else 'donate_v1')));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);metas=list(ix.accounts);temp=str(metas[4].pubkey)
 if kind in ['prefunded','prefunded_excess']:accounts[temp]['lamports']=1 if kind=='prefunded' else m.minimum(165)+12345
 elif kind=='message_long':
  message=b'm'*256;raw=bytes(ix.data);data=raw[:50]+len(message).to_bytes(4,'little')+message+raw[-32:];ix=m.Instruction(m.RELAY,data,metas);proof['instruction_hex']=data.hex()
 elif kind=='tip_large':
  raw=bytes(ix.data);data=raw[:48]+(10001).to_bytes(2,'little')+raw[50:];ix=m.Instruction(m.RELAY,data,metas);proof['instruction_hex']=data.hex()
 elif kind=='insufficient_from':accounts[str(metas[5].pubkey)]['lamports']=1
 elif kind=='wrong_temp_pda':
  wrong=m.pub('native-case-wrong-temp');accounts[str(wrong)]=m.account(0,b'',m.SYSTEM);metas[4]=m.AccountMeta(wrong,False,True)
 elif kind=='temp_readonly':metas[4]=m.AccountMeta(metas[4].pubkey,False,False)
 elif kind=='wrong_native_mint':
  temp_key,bump=m.pd([b'donate_native_wsol_tmp_v1',bytes(metas[5].pubkey),bytes(m.TOKEN)]);accounts[str(temp_key)]=m.account(0,b'',m.SYSTEM);metas[4]=m.AccountMeta(temp_key,False,True);proof['source_token_or_temp']=str(temp_key);selector=bytes([121,160,15,44,219,43,134,7]) if name=='donate_native_v1' else bytes([192,254,132,16,208,43,154,82]);ix=m.Instruction(m.RELAY,selector+bytes(ix.data)[8:],metas);proof['instruction_hex']=bytes(ix.data).hex()
 ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_accounts']=[dict(pubkey=str(a.pubkey),signer=a.is_signer,writable=a.is_writable) for a in metas]
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']}
 if kind in ['prefunded','prefunded_excess']:
  for row in result.values():assert row['error'] is None and not m.check_effects(case,proof,row)
 else:assert result['original']['error'] is not None
 rows.append(dict(name=name+'/'+kind,instruction=name,kind=kind,base_case=case,base_fixture=base,fixture=proof,results=result,mismatches=mismatch));print(rows[-1]['name'],result['original']['error'],mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not r['mismatches']['candidate'] for r in rows),scope='Frozen owned fixtures; only native temp funding/PDA/permissions, authority funds, argument message/tip, or non-native mint plus canonical temp change. Real signatures/privileges/blockhash/history, frozen comparator; old control mismatches retained.')
(P/'native-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
