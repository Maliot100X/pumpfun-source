from pathlib import Path
import base64,copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest();proposal=ROOT/'repro/donation-relay/local-validation-proposal'
sp=importlib.util.spec_from_file_location('relay_donate_context_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/whitelist-generated-source-recovery/constants/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='d8c99c89eba893b030c16733a88300eaf551648853b722bc03b37b67529a2c35';assert H(paths['original'].read_bytes())==m.EXPECTED['original']
specs=[]
for name in ['epoch_tracker','debouncer']:
 for mutation in ['short0','short8','discriminator','owner','config','mint','invalid_enum','readonly','pda']:specs.append((name,mutation))
rows=[]
for target,kind in specs:
 case=copy.deepcopy(next(c for c in m.CASES if c['name']=='donate_native_v1'));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof);c=proof['canonical_pdas'];raw=bytes(ix.data);config=raw[16:48];mint=ix.accounts[3].pubkey
 for name,disc,size,tail in [('epoch_tracker','EpochTrackerV1',90,bytes(16)),('debouncer','DebouncerV1',82,bytes(8))]:
  key=m.Pubkey.from_string(c[name]);_,bump=m.pd([name.encode()+b'_v1',config,bytes(mint)]);data=m.disc(disc)+bytes([bump,1])+config+bytes(mint)+tail;assert len(data)==size;accounts[str(key)]=m.account(m.minimum(size),data,m.RELAY)
 initialized=copy.deepcopy(accounts);key=c[target];data=base64.b64decode(accounts[key]['data_base64']);metas=list(ix.accounts);index=0 if target=='epoch_tracker' else 1
 if kind=='short0':accounts[key]['data_base64']=''
 elif kind=='short8':accounts[key]['data_base64']=base64.b64encode(data[:8]).decode()
 elif kind=='discriminator':accounts[key]['data_base64']=base64.b64encode(bytes(8)+data[8:]).decode()
 elif kind=='owner':accounts[key]['owner']=str(m.pub('donate-context-wrong-owner'))
 elif kind=='config':accounts[key]['data_base64']=base64.b64encode(data[:10]+bytes(m.pub('donate-context-wrong-config'))+data[42:]).decode()
 elif kind=='mint':accounts[key]['data_base64']=base64.b64encode(data[:42]+bytes(m.pub('donate-context-wrong-mint'))+data[74:]).decode()
 elif kind=='invalid_enum':accounts[key]['data_base64']=base64.b64encode(data[:9]+b'\x02'+data[10:]).decode()
 elif kind=='readonly':metas[index]=m.AccountMeta(metas[index].pubkey,False,False)
 elif kind=='pda':
  wrong=m.pub('donate-context-wrong-'+target);accounts[str(wrong)]=copy.deepcopy(accounts[key]);metas[index]=m.AccountMeta(wrong,False,True)
 else:raise AssertionError(kind)
 ix=m.Instruction(m.RELAY,ix.data,metas);proof['instruction_accounts']=[dict(pubkey=str(x.pubkey),signer=x.is_signer,writable=x.is_writable) for x in metas]
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in metas if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']};assert result['original']['error'] is not None
 rows.append(dict(name=target+'/'+kind,base_case=case,base_fixture=base,initialized_accounts=initialized,fixture=proof,mutation=dict(target=target,kind=kind,account=key),results=result,mismatches=mismatch));print(rows[-1]['name'],mismatch,flush=True)
 if mismatch['candidate']:break
report=dict(binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},cases=rows,all_requested_completed=len(rows)==len(specs),passed=sum(not x['mismatches']['candidate'] for x in rows),scope='Only initialized tracker/debouncer state or metadata changes on the frozen owned donate_v1 fixture; real ephemeral signatures and unchanged comparator. Earlier control differences retained, target/candidate equality mandatory.')
(P/'native-context-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(specs)
