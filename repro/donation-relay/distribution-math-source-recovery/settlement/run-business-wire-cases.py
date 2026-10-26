from pathlib import Path
import copy,hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
proposal=ROOT/'repro/donation-relay/local-validation-proposal';sp=importlib.util.spec_from_file_location('relay_business_wire_harness',proposal/'harness_proposal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assert H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
sp=importlib.util.spec_from_file_location('relay_business_wire_verify',proposal/'verify.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v);v.verify(runtime=True)
paths={'original':proposal/'artifacts/original.so','control':ROOT/'repro/donation-relay/anchor-framework-source-recovery/coordinate/candidate.so','candidate':P/'candidate.so'};build=json.loads((P/'build-result.json').read_text());assert build['returncode']==0 and build['source_unchanged'];assert H(paths['candidate'].read_bytes())==build['candidate_sha256'];assert H(paths['control'].read_bytes())=='abfbd582dc434f37d39d829bd0e49ea9b23b83c219f4ae110ae329c706a3b90a';assert H(paths['original'].read_bytes())==m.EXPECTED['original']
idl=json.loads((ROOT/'localnet/relay/idl.json').read_text())
def value(t):
 if isinstance(t,str):
  return {'u64':bytes(8),'u128':bytes(16),'u16':bytes(2),'pubkey':bytes(32),'string':b'\x01\x00\x00\x00A','bytes':b'\x01\x00\x00\x00B'}[t]
 if 'array' in t:return bytes(t['array'][1])
 if 'vec' in t:return b'\x01\x00\x00\x00'+(bytes(32) if t['vec']=='pubkey' else bytes(33)+(10000).to_bytes(2,'little'))
 raise AssertionError(t)
cases=[]
for ix in idl['instructions']:
 fields=[value(a['type']) for a in ix['args']];payload=b''.join(fields);offset=0
 for arg,raw in zip(ix['args'],fields):
  cases.append(dict(name=ix['name']+'/'+arg['name']+'/truncated',instruction=ix['name'],data_hex=(bytes(ix['discriminator'])+payload[:offset+len(raw)-1]).hex(),expected='decode102',expect_control_equal=True))
  if arg['type']=='string':
   b=bytearray(payload);b[offset+4]=255;cases.append(dict(name=ix['name']+'/invalid_utf8',instruction=ix['name'],data_hex=(bytes(ix['discriminator'])+b).hex(),expected='decode102',expect_control_equal=True))
  if isinstance(arg['type'],dict) and arg['type'].get('vec')=={'defined':{'name':'Share'}}:
   b=bytearray(payload);b[offset+4]=3;cases.append(dict(name=ix['name']+'/invalid_share_tag',instruction=ix['name'],data_hex=(bytes(ix['discriminator'])+b).hex(),expected='decode102',expect_control_equal=True))
  offset+=len(raw)
 if ix['name'] in ['just_swap_v1','swap_then_distribute_v1']:
  cases.append(dict(name=ix['name']+'/max_vector_length',instruction=ix['name'],data_hex=(bytes(ix['discriminator'])+b'\xff'*4).hex(),expected='allocation_failure',expect_control_equal=False))
for name in ['donate_v1','donate_pubkey_config_id_v1','donate_pubkey_config_id_with_payer_v1','donate_native_v1','donate_native_pubkey_config_id_v1']:
 cases.append(dict(name=name+'/valid_suffix',instruction=name,data_hex=None,expected='success',expect_control_equal=True))
(P/'business-wire-specs.json').write_text(json.dumps(cases,indent=2)+'\n');rows=[]
for spec in cases:
 base_name=spec['instruction'] if spec['expected']=='success' else 'donate_v1';case=copy.deepcopy(next(c for c in m.CASES if c['name']==base_name));accounts,ix,available,fee,proof=m.prepare(case,ROOT);base=copy.deepcopy(proof)
 data=bytes(ix.data)+b'ignored suffix' if spec['data_hex'] is None else bytes.fromhex(spec['data_hex']);ix=m.Instruction(m.RELAY,data,list(ix.accounts));proof['instruction_hex']=data.hex()
 vms={n:m.vm_for(path,ROOT,accounts) for n,path in paths.items()};assert len({str(vm.latest_blockhash()) for vm in vms.values()})==1
 required={a.pubkey for a in ix.accounts if a.is_signer}|{fee.pubkey()};signers=[s for s in available if s.pubkey() in required];assert {s.pubkey() for s in signers}==required
 tx=m.Transaction.new_signed_with_payer([m.set_compute_unit_limit(1400000),ix],fee.pubkey(),signers,vms['original'].latest_blockhash());assert all(tx.verify_with_results());keys={m.Pubkey.from_string(k) for k in accounts}|set(tx.message.account_keys)
 result={n:m.run_one(vm,tx,keys) for n,vm in vms.items()};left=m.comparable(result['original']);mismatch={n:[k for k in left if left[k]!=m.comparable(result[n])[k]] for n in ['control','candidate']}
 if spec['expected']=='decode102':assert 'Custom(102)' in result['original']['error'].replace(' ','')
 elif spec['expected']=='allocation_failure':assert result['original']['error'] is not None and any('memory allocation failed' in x for x in result['original']['logs'])
 else:
  for row in result.values():assert row['error'] is None and not m.check_effects(case,proof,row)
 rows.append(dict(spec=spec,base_case=case,base_fixture=base,fixture=proof,results=result,mismatches=mismatch));print(spec['name'],mismatch,flush=True)
 if mismatch['candidate'] or (spec['expect_control_equal'] and mismatch['control']):break
report=dict(harness_sha256=H((proposal/'harness_proposal.py').read_bytes()),idl_sha256=H((ROOT/'localnet/relay/idl.json').read_bytes()),binary_hashes={n:H(q.read_bytes()) for n,q in paths.items()},cases=rows,all_requested_completed=len(rows)==len(cases),passed=sum(not r['mismatches']['candidate'] and (not r['spec']['expect_control_equal'] or not r['mismatches']['control']) for r in rows),scope='Only instruction data changes on frozen owned donation fixtures. Normal signatures/blockhash/history and frozen comparator. Same signed transaction in three VMs. Allocation cases intentionally retain a negative previous control.')
(P/'business-wire-cases.json').write_text(json.dumps(report,indent=2)+'\n');assert report['all_requested_completed'] and report['passed']==len(cases)
