#!/usr/bin/env python3
"""Offline full-body/data/receipt verification. No VM or target execution."""
import argparse,base64,copy,gzip,hashlib,importlib.util,json,re,struct,tomllib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
H=lambda b:hashlib.sha256(b).hexdigest()
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read_json(path):
 raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def comparable(row):
 out={k:row[k] for k in ['error','inner_instructions','return_data']}
 out['logs']=[x for x in row['logs'] if re.fullmatch(r'Program \S+ consumed \d+ of \d+ compute units',x) is None]
 relay='RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu'
 for when in ['before','after']:
  out[when]=copy.deepcopy(row[when]);v=out[when].get(relay)
  if v:
   for field in ['data_length','data_sha256','data_base64']:v.pop(field)
   v['lamports']-=row['before'][relay]['lamports']
 return out

def main(signatures=False):
 wire=mod('anchor_receipt_wire',P/'receipt_helpers.py')
 frozen={x['case']['name']:x for x in read_json(ROOT/'repro/donation-relay/local-validation-proposal/fixture-blueprints.json')}
 counts=dict(receipt_cases=0,signature_fields=0)
 class Original:
  b=(ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()
 original=Original()
 def check_tx(rows,fixture):
  raw=base64.b64decode(rows[0]['transaction_base64']);assert all(r['transaction_base64']==rows[0]['transaction_base64'] for r in rows)
  tx=wire.parse(raw);keys=list(map(wire.b58,tx['keys']));budget,call=tx['instructions'];assert len(tx['instructions'])==2
  assert keys[budget[0]]=='ComputeBudget111111111111111111111111111111' and budget[2]==b'\2'+(1400000).to_bytes(4,'little')
  assert keys[call[0]]==wire.RELAY and call[2].hex()==fixture['instruction_hex']
  assert [keys[i] for i in call[1]]==[x['pubkey'] for x in fixture['instruction_accounts']]
  privileges={x['pubkey']:(x['signer'],x['writable']) for x in fixture['instruction_accounts']};privileges[keys[0]]=(True,True);privileges[wire.RELAY]=(False,False);privileges[keys[budget[0]]]=(False,False);assert set(keys)==set(privileges)
  for i,k in enumerate(keys):
   signer=i<tx['required'];writable=i<tx['required']-tx['readonly_signers'] if signer else i<len(keys)-tx['readonly_unsigned'];assert (signer,writable)==privileges[k]
  for row in rows:
   assert row['signature_verification']==[True]*tx['required'] and row['metadata']['signature']==wire.b58(tx['signatures'][0])
   for field in ['logs','inner_instructions','return_data']:assert row[field]==row['metadata'][field]
   if row['error'] is not None:assert all(row['before'][k]==row['after'][k] for k in row['before'] if k!=keys[0])
   counts['signature_fields']+=tx['required']
  if signatures:
   from solders.signature import Signature
   from solders.pubkey import Pubkey
   assert all(Signature.from_bytes(s).verify(Pubkey.from_bytes(k),tx['message']) for s,k in zip(tx['signatures'],tx['keys']))
  return keys
 for name in read_json(P/'stages.json'):
  d=P/name
  build=read_json(d/'build-result.json')
  for rd in sorted(d.glob('runtime-*')):
   if not rd.is_dir():continue
   run=read_json(rd/'comparison.json');proc=read_json(rd/'process-result.json');launch=read_json(rd/'launch.json')
   assert proc['returncode']==0 and proc['candidate_unchanged'] and proc['harness_unchanged']
   assert launch['bindings']==dict(launch['old_bindings'],candidate=build['candidate_sha256'])
   assert run['candidate_sha256']==build['candidate_sha256'] and run['all_requested_completed'] and run['passed']==run['case_count']
   for result in run['cases']:
    case=result['case'];f=frozen[case['name']];assert result['fixture']==f['fixture'] and case==f['case']
    left,right=result['original'],result['candidate'];keys=check_tx([left,right],f['fixture'])
    assert not result['mismatches'] and comparable(left)==comparable(right)
    if left['error'] is None:
     assert case['expected_error'] is None
     for row in [left,right]:wire.independent_effects(case,f['fixture'],row,keys)
    counts['receipt_cases']+=1
  if (d/'header-cases.json').exists():
   report=read_json(d/'header-cases.json');assert report['all_passed'] and report['normal_signature_blockhash_history_checks'] and len(report['cases'])==6
   assert report['binary_hashes']['candidate']==build['candidate_sha256']
   assert report['binary_hashes']['original']==H(original.b) and report['binary_hashes']['baseline']=='836d2ffbec4c437cf9447138e4e54de886744cf4841aeadb34aaeaf7e0249a8f'
   for row in report['cases']:
    f=frozen[row['base_case']['name']];assert f['case']==row['base_case'] and f['fixture']==row['base_fixture']
    expected=copy.deepcopy(row['base_fixture']);mutation=row['mutation'];account=mutation['account'];raw=base64.b64decode(expected['accounts'][account]['data_base64']);assert raw[:8].hex()==mutation['old_discriminator'] and mutation['new_discriminator']=='00'*8
    expected['accounts'][account]['data_base64']=base64.b64encode(bytes(8)+raw[8:]).decode();assert expected==row['fixture']
    left,prior,right=[row['results'][n] for n in ['original','baseline','candidate']];check_tx([left,prior,right],row['fixture']);assert comparable(left)==comparable(prior)==comparable(right)
    assert 'Custom(3002)' in left['error'].replace(' ','')
    assert any(('AnchorError caused by account: '+row['expected_outer_name']+'. Error Code: AccountDiscriminatorMismatch.') in log for log in left['logs'])
    counts['receipt_cases']+=1
  if (d/'instruction-cases.json').exists():
   report=read_json(d/'instruction-cases.json')
   assert report['all_requested_completed'] and report['passed']==7 and len(report['cases'])==7
   assert report['binary_hashes']['original']==H(original.b)
   assert report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/idl-owned-abi-recovery/pubkey-type/candidate.so').read_bytes())
   assert report['binary_hashes']['candidate']==H((d/'candidate.so').read_bytes())
   for result in report['cases']:
    f=frozen[result['base_case']['name']];assert result['base_case']==f['case'] and result['base_fixture']==f['fixture']
    expected=copy.deepcopy(f['fixture'])
    if result['mutated_args_hex'] is None:
     assert result['suffix_hex']==(b'ignored suffix').hex();expected['instruction_hex']+=result['suffix_hex']
    else:expected['instruction_hex']=expected['instruction_hex'][:16]+result['mutated_args_hex']
    assert expected==result['fixture']
    left,prior,right=[result['results'][n] for n in ['original','control','candidate']];keys=check_tx([left,prior,right],result['fixture'])
    assert comparable(left)==comparable(prior)==comparable(right) and all(not x for x in result['mismatches'].values())
    if result['expected_error'] is None:
     assert all(x['error'] is None for x in [left,prior,right])
     for row in [left,prior,right]:wire.independent_effects(result['base_case'],f['fixture'],row,keys)
    else:assert result['expected_error']==102 and 'Custom(102)' in left['error'].replace(' ','')
    counts['receipt_cases']+=1
  if (d/'idl-rejections.json').exists():
   report=read_json(d/'idl-rejections.json');assert report['all_requested_completed'] and report['passed']==9 and len(report['cases'])==9
   assert report['binary_hashes']['candidate']==H((d/'candidate.so').read_bytes())
   assert report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/framework-crate-recovery/full-enums-v148/candidate.so').read_bytes())
   assert report['binary_hashes']['original']==H(original.b)
   for result in report['cases']:
    f=frozen[result['case']['name']];assert result['case']==f['case'] and result['base_fixture']==f['fixture']
    expected=copy.deepcopy(f['fixture']);mutation=result['mutation'];kind=mutation['kind'];account=mutation['account'];data=base64.b64decode(expected['accounts'][account]['data_base64'])
    if kind=='truncate':expected['accounts'][account]['data_base64']=base64.b64encode(data[:mutation['value']]).decode()
    elif kind=='owner':
     name='relay-local-data/rejection-wrong-owner';expected['accounts'][account]['owner']=wire.b58(hashlib.sha256(name.encode()).digest())
    elif kind=='uninitialized':expected['accounts'][account].update(owner=wire.SYSTEM,lamports=0,data_base64='')
    elif kind=='authority':
     authority=hashlib.sha256(b'relay-local-data/rejection-wrong-authority').digest();expected['accounts'][account]['data_base64']=base64.b64encode(data[:8]+authority+data[40:]).decode()
    elif kind=='readonly':expected['instruction_accounts'][0]['writable']=False
    else:raise AssertionError(kind)
    assert expected==result['fixture']
    left,control,right=[result['results'][n] for n in ['original','control','candidate']];check_tx([left,control,right],result['fixture'])
    assert comparable(left)==comparable(control)==comparable(right) and all(not x for x in result['mismatches'].values())
    assert 'Custom('+str(result['expected_code'])+')' in left['error'].replace(' ','')
    counts['receipt_cases']+=1
  if (d/'business-wire-cases.json').exists():
   report=read_json(d/'business-wire-cases.json');specs=read_json(d/'business-wire-specs.json');assert len(specs)==48 and report['all_requested_completed'] and report['passed']==48 and len(report['cases'])==48
   assert report['binary_hashes']['candidate']==build['candidate_sha256'] and report['binary_hashes']['original']==H(original.b)
   assert report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/anchor-framework-source-recovery/coordinate/candidate.so').read_bytes())
   idl=read_json(P/'captured-idl.json');assert report['idl_sha256']==H((P/'captured-idl.json').read_bytes());ixs={x['name']:x for x in idl['instructions']}
   allocation_controls=0
   for result,spec in zip(report['cases'],specs):
    assert result['spec']==spec;f=frozen[result['base_case']['name']];assert result['base_case']==f['case'] and result['base_fixture']==f['fixture'];expected=copy.deepcopy(f['fixture'])
    expected['instruction_hex']=f['fixture']['instruction_hex']+(b'ignored suffix').hex() if spec['data_hex'] is None else spec['data_hex'];assert expected==result['fixture']
    assert bytes.fromhex(expected['instruction_hex'])[:8]==bytes(ixs[spec['instruction']]['discriminator'])
    left,prior,right=[result['results'][n] for n in ['original','control','candidate']];keys=check_tx([left,prior,right],result['fixture']);assert comparable(left)==comparable(right) and not result['mismatches']['candidate']
    if spec['expect_control_equal']:assert comparable(left)==comparable(prior) and not result['mismatches']['control']
    if spec['expected']=='success':
     assert all(x['error'] is None for x in [left,prior,right])
     for row in [left,prior,right]:wire.independent_effects(result['base_case'],f['fixture'],row,keys)
    elif spec['expected']=='decode102':assert 'Custom(102)' in left['error'].replace(' ','')
    else:
     assert spec['expected']=='allocation_failure' and not spec['expect_control_equal'];assert left['error'] is not None and any('memory allocation failed' in x for x in left['logs']);assert set(result['mismatches']['control'])=={'error','logs'} and 'Custom(102)' in prior['error'].replace(' ','');allocation_controls+=1
    counts['receipt_cases']+=1
   assert allocation_controls==2
  if (d/'whitelist-cases.json').exists():
   report=read_json(d/'whitelist-cases.json');assert report['all_requested_completed'] and report['passed']==len(report['cases']) and len(report['cases']) in [15,18]
   assert report['binary_hashes']['candidate']==build['candidate_sha256'] and report['binary_hashes']['original']==H(original.b)
   assert report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/business-wire-source-recovery/framework-writer/candidate.so').read_bytes())
   from_fixture=frozen['donate_v1'];negative_controls=set()
   for result in report['cases']:
    assert result['base_case']==from_fixture['case'] and result['base_fixture']==from_fixture['fixture'];expected=copy.deepcopy(from_fixture['fixture']);mutation=result['mutation'];kind=mutation['kind'];key=mutation['account'];assert key==expected['canonical_pdas']['mint_whitelist'];owner=next(x['pubkey'] for x in expected['instruction_accounts'] if x['signer'] and x['pubkey']!=wire.RELAY)
    # The owner signer is the original donate_v1 `from` account (index5).
    owner=expected['instruction_accounts'][5]['pubkey'];assert owner in expected['test_owned_pubkeys']
    metas=[dict(pubkey=key,signer=False,writable=True),dict(pubkey=owner,signer=True,writable=True),dict(pubkey=wire.SYSTEM,signer=False,writable=False)]
    raw=base64.b64decode(expected['accounts'][key]['data_base64'])
    if kind=='readonly_whitelist':metas[0]['writable']=False
    elif kind=='discriminator':expected['accounts'][key]['data_base64']=base64.b64encode(bytes(8)+raw[8:]).decode()
    elif kind=='truncate':expected['accounts'][key]['data_base64']=base64.b64encode(raw[:mutation['value']]).decode()
    elif kind=='owner':expected['accounts'][key]['owner']=wire.b58(hashlib.sha256(b'relay-local-data/whitelist-wrong-owner').digest())
    elif kind=='pda':
     wrong=wire.b58(hashlib.sha256(b'relay-local-data/whitelist-wrong-pda').digest());assert mutation['new_account']==wrong;expected['accounts'][wrong]=copy.deepcopy(expected['accounts'][key]);metas[0]['pubkey']=wrong
    elif kind=='rent':expected['accounts'][key]['lamports']-=1
    elif kind=='readonly_signer':metas[1]['writable']=False
    elif kind=='not_signer':metas[1]['signer']=False
    elif kind=='system':
     wrong=wire.b58(hashlib.sha256(b'relay-local-data/whitelist-wrong-system').digest());assert mutation['new_account']==wrong;expected['accounts'][wrong]=dict(lamports=1,data_base64='',owner=wire.SYSTEM,executable=False,rent_epoch=0);metas[2]['pubkey']=wrong
    elif kind=='missing':metas=metas[:mutation['value']]
    elif kind.startswith('initialize_'):
     assert kind in ['initialize_create','initialize_prefunded','initialize_insufficient'];expected['accounts'][key].update(owner=wire.SYSTEM,data_base64='',lamports=1 if kind=='initialize_prefunded' else 0)
     if kind=='initialize_insufficient':expected['accounts'][owner]['lamports']=1
    else:assert kind=='none'
    expected['instruction_accounts']=metas;expected['instruction_hex']='d185fd0c5009e780'+'00000000';assert expected==result['fixture']
    left,prior,right=[result['results'][n] for n in ['original','control','candidate']];keys=check_tx([left,prior,right],result['fixture']);assert comparable(left)==comparable(right) and not result['mismatches']['candidate'];assert 'Custom('+str(result['expected_code'])+')' in left['error'].replace(' ','')
    if result['name'] in ['wrong_space','wrong_system','missing0']:assert result['mismatches']['control']==['logs'];negative_controls.add(result['name'])
    else:assert comparable(left)==comparable(prior) and not result['mismatches']['control']
    for row in [left,prior,right]:
     calls=[c for group in row['inner_instructions'] for c in group]
     if kind.startswith('initialize_'):
      rent=(1037+128)*3480*2;ops=[2,8,1] if kind=='initialize_prefunded' else [0];assert len(calls)==len(ops)
      for call,op in zip(calls,ops):
       ix=call['instruction'];data=wire.wire_vec(ix['data']);accounts=[keys[x] for x in wire.wire_vec(ix['accounts'])];assert keys[ix['programIdIndex']]==wire.SYSTEM and call['stackHeight']==2 and int.from_bytes(data[:4],'little')==op
       if op==0:assert len(data)==52 and int.from_bytes(data[4:12],'little')==rent and int.from_bytes(data[12:20],'little')==1037 and data[20:]==wire.un58(wire.RELAY) and accounts==[owner,key]
       elif op==2:assert len(data)==12 and int.from_bytes(data[4:],'little')==rent-1 and accounts==[owner,key]
       elif op==8:assert len(data)==12 and int.from_bytes(data[4:],'little')==1037 and accounts==[key]
       else:assert len(data)==36 and data[4:]==wire.un58(wire.RELAY) and accounts==[key]
     else:assert not calls
    counts['receipt_cases']+=1
   assert negative_controls=={'wrong_space','wrong_system','missing0'}
  for context_file,base_case_name in [('donate-context-cases.json','donate_v1'),('pubkey-context-cases.json','donate_pubkey_config_id_v1'),('payer-context-cases.json','donate_pubkey_config_id_with_payer_v1'),('native-context-cases.json','donate_native_v1'),('native-pubkey-context-cases.json','donate_native_pubkey_config_id_v1')]:
   if not (d/context_file).exists():continue
   report=read_json(d/context_file);assert report['all_requested_completed'] and report['passed']==18 and len(report['cases'])==18
   assert report['binary_hashes']['candidate']==build['candidate_sha256'] and report['binary_hashes']['original']==H(original.b) and report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/whitelist-generated-source-recovery/constants/candidate.so').read_bytes())
   seen=set();negative=set()
   for result in report['cases']:
    f=frozen[base_case_name];assert result['base_case']==f['case'] and result['base_fixture']==f['fixture'];expected=copy.deepcopy(f['fixture']);raw=bytes.fromhex(expected['instruction_hex']);config=raw[16:48];mint=wire.un58(expected['instruction_accounts'][3]['pubkey'])
    for label,type_name,size,tail in [('epoch_tracker','EpochTrackerV1',90,bytes(16)),('debouncer','DebouncerV1',82,bytes(8))]:
     key=expected['canonical_pdas'][label];fixture_state=result['initialized_accounts'][key];b=base64.b64decode(fixture_state['data_base64']);bump=b[8];assert hashlib.sha256(label.encode()+b'_v1'+config+mint+bytes([bump])+wire.un58(wire.RELAY)+b'ProgramDerivedAddress').digest()==wire.un58(key)
     data=wire.account_disc(type_name)+bytes([bump,1])+config+mint+tail;assert len(data)==size
     expected['accounts'][key]=dict(lamports=(size+128)*3480*2,data_base64=base64.b64encode(data).decode(),owner=wire.RELAY,executable=False,rent_epoch=0)
    assert expected['accounts']==result['initialized_accounts']
    mutation=result['mutation'];label=mutation['target'];kind=mutation['kind'];assert label in ['epoch_tracker','debouncer'];key=expected['canonical_pdas'][label];assert mutation['account']==key;data=base64.b64decode(expected['accounts'][key]['data_base64']);index=0 if label=='epoch_tracker' else 1
    if kind=='short0':expected['accounts'][key]['data_base64']=''
    elif kind=='short8':expected['accounts'][key]['data_base64']=base64.b64encode(data[:8]).decode()
    elif kind=='discriminator':expected['accounts'][key]['data_base64']=base64.b64encode(bytes(8)+data[8:]).decode()
    elif kind=='owner':expected['accounts'][key]['owner']=wire.b58(hashlib.sha256(b'relay-local-data/donate-context-wrong-owner').digest())
    elif kind=='config':expected['accounts'][key]['data_base64']=base64.b64encode(data[:10]+hashlib.sha256(b'relay-local-data/donate-context-wrong-config').digest()+data[42:]).decode()
    elif kind=='mint':expected['accounts'][key]['data_base64']=base64.b64encode(data[:42]+hashlib.sha256(b'relay-local-data/donate-context-wrong-mint').digest()+data[74:]).decode()
    elif kind=='invalid_enum':expected['accounts'][key]['data_base64']=base64.b64encode(data[:9]+b'\x02'+data[10:]).decode()
    elif kind=='readonly':expected['instruction_accounts'][index]['writable']=False
    else:
     assert kind=='pda';wrong=wire.b58(hashlib.sha256(('relay-local-data/donate-context-wrong-'+label).encode()).digest());expected['accounts'][wrong]=copy.deepcopy(expected['accounts'][key]);expected['instruction_accounts'][index]['pubkey']=wrong
    assert expected==result['fixture'];assert result['name']==label+'/'+kind;seen.add(result['name'])
    left,prior,right=[result['results'][n] for n in ['original','control','candidate']];check_tx([left,prior,right],result['fixture']);assert left['error'] is not None and comparable(left)==comparable(right) and not result['mismatches']['candidate']
    if kind in ['config','mint']:
     assert result['mismatches']['control']==['logs'];negative.add(result['name']);line={('epoch_tracker','config'):102,('debouncer','config'):110,('epoch_tracker','mint'):127,('debouncer','mint'):118}[(label,kind)]
     assert any('programs/contracts/src/tools/donate/shared.rs:'+str(line)+'.' in x for x in left['logs'])
     if kind=='mint':assert sum(x in ['Program log: Left:','Program log: Right:'] for x in left['logs'])==2
    else:assert comparable(left)==comparable(prior) and not result['mismatches']['control']
    counts['receipt_cases']+=1
   assert len(seen)==18 and len(negative)==4
  if (d/'payer-funding-cases.json').exists():
   report=read_json(d/'payer-funding-cases.json');assert report['all_requested_completed'] and report['passed']==5 and len(report['cases'])==5;assert report['binary_hashes']['candidate']==build['candidate_sha256'] and report['binary_hashes']['original']==H(original.b) and report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/donation-layout-source-recovery/pubkey/candidate.so').read_bytes())
   codes={'payer_readonly':'PrivilegeEscalation','payer_not_signer':3010,'payer_insufficient':1,'from_one_lamport':None,'payer_alias_from':None};seen=set();f=frozen['donate_pubkey_config_id_with_payer_v1']
   for result in report['cases']:
    label=result['name'];assert label in codes and label not in seen;seen.add(label);assert result['base_case']==f['case'] and result['base_fixture']==f['fixture'];expected=copy.deepcopy(f['fixture']);authority=expected['instruction_accounts'][5]['pubkey'];payer=expected['instruction_accounts'][6]['pubkey']
    if label=='payer_readonly':expected['instruction_accounts'][6]['writable']=False
    elif label=='payer_not_signer':expected['instruction_accounts'][6]['signer']=False
    elif label=='payer_insufficient':expected['accounts'][payer]['lamports']=1
    elif label=='from_one_lamport':expected['accounts'][authority]['lamports']=1
    else:expected['instruction_accounts'][6]['pubkey']=authority;payer=authority
    assert expected==result['fixture'] and result['expected_code']==codes[label];left,prior,right=[result['results'][n] for n in ['original','control','candidate']];keys=check_tx([left,prior,right],result['fixture']);assert comparable(left)==comparable(prior)==comparable(right) and all(not x for x in result['mismatches'].values())
    if codes[label] is None:
     for row in [left,prior,right]:
      assert row['error'] is None;wire.independent_effects(result['base_case'],expected,row,keys)
      assert row['before'][payer]['lamports']-row['after'][payer]['lamports']==sum((size+128)*3480*2 for size in [90,82,165])
      if label=='from_one_lamport':assert row['after'][authority]['lamports']==1
      creates=[call['instruction'] for group in row['inner_instructions'] for call in group if keys[call['instruction']['programIdIndex']]==wire.SYSTEM and int.from_bytes(wire.wire_vec(call['instruction']['data'])[:4],'little')==0]
      assert len(creates)==3
      expected_creates={expected['canonical_pdas']['epoch_tracker']:(90,wire.RELAY),expected['canonical_pdas']['debouncer']:(82,wire.RELAY),expected['canonical_pdas']['debouncer_token_account']:(165,expected['instruction_accounts'][9]['pubkey'])}
      for ix in creates:
       metas=[keys[i] for i in wire.wire_vec(ix['accounts'])];assert len(metas)==2 and metas[0]==payer;data=wire.wire_vec(ix['data']);size,owner=expected_creates.pop(metas[1]);assert len(data)==52 and int.from_bytes(data[4:12],'little')==(size+128)*3480*2 and int.from_bytes(data[12:20],'little')==size and data[20:]==wire.un58(owner)
      assert not expected_creates
    elif isinstance(codes[label],str):assert codes[label] in left['error']
    else:assert 'Custom('+str(codes[label])+')' in left['error'].replace(' ','')
    counts['receipt_cases']+=1
   assert seen==set(codes)
  if (d/'native-cases.json').exists():
   report=read_json(d/'native-cases.json');assert report['all_requested_completed'] and report['passed']==16 and len(report['cases'])==16;assert report['binary_hashes']['candidate']==build['candidate_sha256'] and report['binary_hashes']['original']==H(original.b) and report['binary_hashes']['control']==H((ROOT/'repro/donation-relay/payer-generated-source-recovery/payer/candidate.so').read_bytes());seen=set()
   kinds={'prefunded','prefunded_excess','message_long','tip_large','insufficient_from','wrong_temp_pda','temp_readonly','wrong_native_mint'}
   for result in report['cases']:
    instruction=result['instruction'];kind=result['kind'];assert instruction in ['donate_native_v1','donate_native_pubkey_config_id_v1'] and kind in kinds;assert result['name']==instruction+'/'+kind and result['name'] not in seen;seen.add(result['name']);f=frozen[instruction if kind!='wrong_native_mint' else 'donate_v1'];assert result['base_case']==f['case'] and result['base_fixture']==f['fixture'];expected=copy.deepcopy(f['fixture']);temp=expected['instruction_accounts'][4]['pubkey'];authority=expected['instruction_accounts'][5]['pubkey'];raw=bytes.fromhex(expected['instruction_hex'])
    if kind in ['prefunded','prefunded_excess']:expected['accounts'][temp]['lamports']=1 if kind=='prefunded' else (165+128)*3480*2+12345
    elif kind=='message_long':expected['instruction_hex']=(raw[:50]+(256).to_bytes(4,'little')+b'm'*256+raw[-32:]).hex()
    elif kind=='tip_large':expected['instruction_hex']=(raw[:48]+(10001).to_bytes(2,'little')+raw[50:]).hex()
    elif kind=='insufficient_from':expected['accounts'][authority]['lamports']=1
    elif kind=='wrong_temp_pda':
     wrong=wire.b58(hashlib.sha256(b'relay-local-data/native-case-wrong-temp').digest());expected['accounts'][wrong]=dict(lamports=0,data_base64='',owner=wire.SYSTEM,executable=False,rent_epoch=0);expected['instruction_accounts'][4]['pubkey']=wrong
    elif kind=='temp_readonly':expected['instruction_accounts'][4]['writable']=False
    else:
     temp=frozen[instruction]['fixture']['source_token_or_temp'];expected['accounts'][temp]=dict(lamports=0,data_base64='',owner=wire.SYSTEM,executable=False,rent_epoch=0);expected['instruction_accounts'][4]['pubkey']=temp;expected['source_token_or_temp']=temp;selector=bytes([121,160,15,44,219,43,134,7]) if instruction=='donate_native_v1' else bytes([192,254,132,16,208,43,154,82]);expected['instruction_hex']=(selector+raw[8:]).hex()
    assert expected==result['fixture'];left,prior,right=[result['results'][n] for n in ['original','control','candidate']];keys=check_tx([left,prior,right],expected);assert comparable(left)==comparable(prior)==comparable(right) and all(not x for x in result['mismatches'].values())
    if kind in ['prefunded','prefunded_excess']:
     for row in [left,prior,right]:
      assert row['error'] is None;wire.independent_effects(result['base_case'],expected,row,keys);amount=int.from_bytes(bytes.fromhex(expected['instruction_hex'])[8:16],'little');prefund=expected['accounts'][temp]['lamports'];rent=sum((size+128)*3480*2 for size in [90,82,165]);assert row['before'][authority]['lamports']-row['after'][authority]['lamports']==rent+amount-prefund
      systems=[];tokens=[]
      token_program=expected['instruction_accounts'][8]['pubkey']
      for group in row['inner_instructions']:
       for call in group:
        ix=call['instruction'];data=wire.wire_vec(ix['data']);metas=[keys[i] for i in wire.wire_vec(ix['accounts'])]
        if keys[ix['programIdIndex']]==wire.SYSTEM:systems.append((data,metas))
        elif keys[ix['programIdIndex']]==token_program:tokens.append((data,metas))
      allocations=[(data,metas) for data,metas in systems if data[:4]==(8).to_bytes(4,'little')];assignments=[(data,metas) for data,metas in systems if data[:4]==(1).to_bytes(4,'little')];transfers=[(int.from_bytes(data[4:],'little'),metas) for data,metas in systems if data[:4]==(2).to_bytes(4,'little')]
      assert allocations==[((8).to_bytes(4,'little')+(165).to_bytes(8,'little'),[temp])];assert assignments==[((1).to_bytes(4,'little')+wire.un58(token_program),[temp])]
      topup=max((165+128)*3480*2-prefund,0);expected_transfers=([(topup,[authority,temp])] if topup else [])+[(amount,[authority,temp])];assert transfers==expected_transfers
      assert [data[0] for data,metas in tokens][-3:]==[17,12,9];sync,transfer,close=tokens[-3:];assert sync==(bytes([17]),[temp]);assert transfer[0]==bytes([12])+amount.to_bytes(8,'little')+bytes([9]) and transfer[1]==[temp,expected['instruction_accounts'][3]['pubkey'],expected['canonical_pdas']['debouncer_token_account'],authority];assert close==(bytes([9]),[temp,authority,authority])
    elif kind=='temp_readonly':assert 'PrivilegeEscalation' in left['error']
    else:
     code={'message_long':6009,'tip_large':6018,'insufficient_from':1,'wrong_temp_pda':2006,'wrong_native_mint':6006}[kind];assert 'Custom('+str(code)+')' in left['error'].replace(' ','')
    counts['receipt_cases']+=1
   assert len(seen)==16
  if (d/'mint-extension-cases.json').exists():
   report=read_json(d/'mint-extension-cases.json');assert report['all_requested_completed'] and report['passed']==27 and len(report['cases'])==27
   assert report['binary_hashes']=={'original':H(original.b),'control':H((ROOT/'repro/donation-relay/native-generated-source-recovery/native/candidate.so').read_bytes()),'candidate':build['candidate_sha256']}
   token='TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb';ata='ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL';assert report['token2022_sha256']==H((ROOT/'evidence/dependencies/spl_token_2022/deployed.so').read_bytes())=='15a2e615a42e20f31714bbaaee43002ae6f1cda2e8d7118243117ab3c1342e2d'
   authority=hashlib.sha256(b'relay-local-data/mint-policy-authority').digest()
   def extension(tag,length,offset=None,value=b''):
    data=bytearray(length)
    if offset is not None:data[offset:offset+len(value)]=value
    return tag.to_bytes(2,'little')+length.to_bytes(2,'little')+bytes(data)
   expected_specs={'base':(None,None),'empty_extension_header':(b'\0',None),'mint_authority':(None,6031),'freeze_authority':(None,6031)}
   for name,tag,length,offset,value,error in [('fee_zero',1,108,None,b'',None),('fee_config_authority',1,108,0,authority,6031),('fee_withdraw_authority',1,108,32,authority,None),('fee_older_bps',1,108,88,b'\1\0',6031),('fee_newer_bps',1,108,106,b'\1\0',6031),('hook_none',14,64,None,b'',None),('hook_authority',14,64,0,authority,6031),('hook_program',14,64,32,authority,6031),('permanent_delegate_zero',12,32,None,b'',6031),('permanent_delegate_key',12,32,0,authority,6031),('mint_close_none',3,32,None,b'',None),('mint_close_some',3,32,0,authority,6031),('default_initialized',6,1,0,b'\1',None),('default_frozen',6,1,0,b'\2',6031),('default_uninitialized',6,1,0,b'\0',6031),('nontransferable',9,0,None,b'',6031),('fee_wrong_length',1,107,None,b'',None),('unknown_extension',28,0,None,b'',None)]:expected_specs[name]=(extension(tag,length,offset,value),error)
   expected_specs.update({'whitelisted_fee_authority':(extension(1,108,0,authority),None),'scaled_ui_then_fee_authority':(extension(25,56)+extension(1,108,0,authority),6031),'pausable_then_hook_authority':(extension(26,33)+extension(14,64,0,authority),6031),'scaled_ui_then_delegate':(extension(25,56)+extension(12,32),6031),'unknown_then_fee_authority':(extension(28,0)+extension(1,108,0,authority),None)})
   seen=set()
   for result in report['cases']:
    spec=result['spec'];name=spec['name'];assert name not in seen;seen.add(name);payload,error=expected_specs[name];assert spec['expected']==error and spec['tlv']==(None if payload is None else payload.hex())
    f=frozen['donate_v1'];assert result['base_case']==f['case'] and result['base_fixture']==f['fixture'];expected=copy.deepcopy(f['fixture']);metas=expected['instruction_accounts'];mint=metas[3]['pubkey'];deb=metas[1]['pubkey'];owner=metas[5]['pubkey'];new=result['fixture']
    target=new['canonical_pdas']['debouncer_token_account'];source=new['source_token_or_temp']
    for key,signer in [(target,deb),(source,owner)]:
     seeds=wire.un58(signer)+wire.un58(token)+wire.un58(mint);assert any(hashlib.sha256(seeds+bytes([bump])+wire.un58(ata)+b'ProgramDerivedAddress').digest()==wire.un58(key) for bump in range(256))
     if signatures:
      from solders.pubkey import Pubkey
      assert str(Pubkey.find_program_address([wire.un58(signer),wire.un58(token),wire.un58(mint)],Pubkey.from_string(ata))[0])==key
    expected['accounts'].pop(expected['source_token_or_temp']);expected['accounts'].pop(expected['canonical_pdas']['debouncer_token_account']);expected['source_token_or_temp']=source;expected['canonical_pdas']['debouncer_token_account']=target
    for index,key in [(2,target),(4,source),(8,token)]:metas[index]['pubkey']=key
    mint_data=bytearray(base64.b64decode(expected['accounts'][mint]['data_base64']))
    if name in ['mint_authority','freeze_authority']:
     offset=0 if name=='mint_authority' else 46;mint_data[offset:offset+4]=(1).to_bytes(4,'little');mint_data[offset+4:offset+36]=authority;assert spec['authority']==('mint' if offset==0 else 'freeze')
    else:assert 'authority' not in spec
    if payload is not None:mint_data+=bytes(83)+b'\1'+payload
    def account(data):return {'lamports':(len(data)+128)*3480*2,'data_base64':base64.b64encode(data).decode(),'owner':token,'executable':False,'rent_epoch':0}
    expected['accounts'][mint]=account(bytes(mint_data))
    for key,signer,amount in [(source,owner,10**9),(target,deb,0)]:
     data=bytearray(165);data[:32]=wire.un58(mint);data[32:64]=wire.un58(signer);data[64:72]=amount.to_bytes(8,'little');data[108]=1;expected['accounts'][key]=account(bytes(data)+b'\2'+extension(2,8))
    assert bool(spec.get('whitelist'))==(name=='whitelisted_fee_authority')
    if name=='whitelisted_fee_authority':
     key=metas[6]['pubkey'];data=base64.b64decode(expected['accounts'][key]['data_base64']);expected['accounts'][key]['data_base64']=base64.b64encode(data[:9]+(1).to_bytes(4,'little')+wire.un58(mint)+data[45:]).decode()
    assert expected==new
    left,prior,right=[result['results'][label] for label in ['original','control','candidate']];keys=check_tx([left,prior,right],new);assert all(not x for x in result['mismatches'].values()) and comparable(left)==comparable(prior)==comparable(right)
    for row in [left,prior,right]:
     assert row['before'][token]['executable'] and row['before'][token]['data_sha256']==report['token2022_sha256'] and row['before'][token]['data_length']==1382016
     for key,value in expected['accounts'].items():
      before=row['before'][key]
     if before is None:assert value=={'lamports':0,'data_base64':'','owner':wire.SYSTEM,'executable':False,'rent_epoch':0}
     else:assert all(before[field]==value[field] for field in ['lamports','owner','executable','rent_epoch','data_base64']) and before['data_sha256']==H(base64.b64decode(value['data_base64']))
     if error is None:
      assert row['error'] is None;wire.independent_effects(f['case'],new,row,keys)
      token_calls=[]
      for group in row['inner_instructions']:
       for call in group:
        ix=call['instruction']
        if keys[ix['programIdIndex']]==token:token_calls.append((wire.wire_vec(ix['data']),[keys[i] for i in wire.wire_vec(ix['accounts'])]))
      assert token_calls==[(b'\x0c'+(1000000).to_bytes(8,'little')+b'\6',[source,mint,target,owner])]
      # Only tracker/debouncer need rent because both token accounts already exist.
      assert row['before'][owner]['lamports']-row['after'][owner]['lamports']==((90+128)+(82+128))*3480*2
     else:
      assert 'Custom(6031)' in row['error'].replace(' ','') and any('MintNotSafeForDonation' in log for log in row['logs'])
      assert not row['return_data']['data'] and not any(log.startswith('Program data: ') for log in row['logs'])
    counts['receipt_cases']+=1
   assert seen==set(expected_specs)
  if (d/'close-cases.json').exists():
   report=read_json(d/'close-cases.json');assert report['all_requested_completed'] and report['passed']==40 and len(report['cases'])==40
   assert report['binary_hashes']=={'original':H(original.b),'control':H((ROOT/'repro/donation-relay/shared-donation-source-recovery/shared/candidate.so').read_bytes()),'candidate':build['candidate_sha256']}
   token='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';ata='ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL';relayer='RLYRf96HAJSbbXCNS6ibQYnkxtb6kbfuFxqEkm9oQUc';seen=set();negative=set();f=frozen['donate_v1']
   def pub(label):return wire.b58(hashlib.sha256(('relay-local-data/'+label).encode()).digest())
   def state_account(data,program):return {'lamports':(len(data)+128)*3480*2,'data_base64':base64.b64encode(data).decode(),'owner':program,'executable':False,'rent_epoch':0}
   def pda_bump(key,seeds,program):
    matches=[b for b in range(256) if hashlib.sha256(b''.join(seeds)+bytes([b])+wire.un58(program)+b'ProgramDerivedAddress').digest()==wire.un58(key)];assert len(matches)==1
    if signatures:
     from solders.pubkey import Pubkey
     actual,bump=Pubkey.find_program_address(seeds,Pubkey.from_string(program));assert str(actual)==key and bump==matches[0]
    return matches[0]
   for result in report['cases']:
    kind=result['kind'];assert kind not in seen;seen.add(kind);assert result['base_case']==f['case'] and result['base_fixture']==f['fixture'];expected=copy.deepcopy(f['fixture']);new=result['canonical_fixture'];config=bytes.fromhex(expected['instruction_hex'])[16:48];mint=expected['instruction_accounts'][3]['pubkey'];signer=expected['instruction_accounts'][5]['pubkey'];assert signer!=relayer;epoch=3;gross=4000000;c=expected['canonical_pdas'];dist=new['canonical_pdas']['distribution'];dest=new['canonical_pdas']['distribution_token_account'];source=new['canonical_pdas']['debouncer_token_account'];db=pda_bump(dist,[b'distribution_v1',config,wire.un58(mint),epoch.to_bytes(16,'little')],wire.RELAY)
    pda_bump(dest,[wire.un58(dist),wire.un58(token),wire.un58(mint)],ata);pda_bump(source,[wire.un58(c['debouncer']),wire.un58(token),wire.un58(mint)],ata)
    expected['accounts'].pop(expected['source_token_or_temp']);expected['accounts'].pop(c['mint_whitelist']);expected['accounts'].pop(c['debouncer_token_account']);c.pop('mint_whitelist');c.update(distribution=dist,distribution_token_account=dest,debouncer_token_account=source)
    for label,name,tail in [('epoch_tracker','EpochTrackerV1',epoch.to_bytes(16,'little')),('debouncer','DebouncerV1',gross.to_bytes(8,'little'))]:
     bump=pda_bump(c[label],[label.encode()+b'_v1',config,wire.un58(mint)],wire.RELAY);expected['accounts'][c[label]]=state_account(wire.account_disc(name)+bytes([bump,1])+config+wire.un58(mint)+tail,wire.RELAY)
    source_data=bytearray(165);source_data[:32]=wire.un58(mint);source_data[32:64]=wire.un58(c['debouncer']);source_data[64:72]=gross.to_bytes(8,'little');source_data[108]=1;expected['accounts'][source]=state_account(bytes(source_data),token)
    for key in [dist,dest]:expected['accounts'][key]={'lamports':0,'data_base64':'','owner':wire.SYSTEM,'executable':False,'rent_epoch':0}
    expected['instruction_hex']=(bytes([171,28,54,214,140,137,101,90])+config+epoch.to_bytes(16,'little')).hex();expected.pop('source_token_or_temp');expected.update(epoch=epoch,gross=gross,distribution_bump=db)
    names=[dist,dest,c['epoch_tracker'],c['debouncer'],source,mint,token,signer,ata,wire.SYSTEM,c['event_authority'],wire.RELAY];writable={0,1,2,3,4,5,7};expected['instruction_accounts']=[dict(pubkey=k,signer=i==7,writable=i in writable) for i,k in enumerate(names)];assert expected==new
    expected=copy.deepcopy(expected);metas=expected['instruction_accounts'];error=None
    def change_data(key,data):expected['accounts'][key]['data_base64']=base64.b64encode(data).decode()
    if kind in ['wrong_relayer','suffix','distribution_prefunded']:
     error=2012
     if kind=='suffix':expected['instruction_hex']+=b'ignored suffix'.hex()
     if kind=='distribution_prefunded':expected['accounts'][dist]['lamports']=1
    elif kind=='distribution_exists':expected['accounts'][dist]=state_account(wire.account_disc('DistributionV1')+bytes([db,1])+config+wire.un58(mint)+epoch.to_bytes(16,'little')+gross.to_bytes(8,'little'),wire.RELAY);error=0
    elif kind=='destination_exists':
     data=bytearray(165);data[:32]=wire.un58(mint);data[32:64]=wire.un58(dist);data[108]=1;expected['accounts'][dest]=state_account(bytes(data),token);error='IllegalOwner'
    elif kind=='signer_missing':metas[7]['signer']=False;error=3010
    elif kind in ['signer_readonly','distribution_readonly','destination_readonly','mint_readonly']:
     metas[{'signer_readonly':7,'distribution_readonly':0,'destination_readonly':1,'mint_readonly':5}[kind]]['writable']=False;error=2000 if kind=='mint_readonly' else 'PrivilegeEscalation'
    elif kind in ['debouncer_token_mint','debouncer_token_authority']:
     data=base64.b64decode(expected['accounts'][source]['data_base64']);off=0 if kind.endswith('_mint') else 32;change_data(source,data[:off]+wire.un58(pub('close-wrong-token-field'))+data[off+32:]);error=2012 if off==0 else 2015
    elif kind=='mint_address':
     key=c['debouncer'];data=base64.b64decode(expected['accounts'][key]['data_base64']);change_data(key,data[:42]+wire.un58(pub('close-wrong-mint'))+data[74:]);error=2012
    elif kind=='distribution_pda':
     key=pub('close-wrong-distribution');expected['accounts'][key]={'lamports':0,'data_base64':'','owner':wire.SYSTEM,'executable':False,'rent_epoch':0};metas[0]['pubkey']=key;error=2006
    elif kind.startswith('missing_'):expected['instruction_accounts']=metas[:int(kind.split('_')[1])];error=3005
    else:
     label,mutation=next((name,kind[len(name)+1:]) for name in ['epoch_tracker','debouncer'] if kind.startswith(name+'_'));index=2 if label=='epoch_tracker' else 3;key=c[label];data=base64.b64decode(expected['accounts'][key]['data_base64']);error={'short0':3001,'short8':3003,'discriminator':3002,'owner':3007,'invalid_enum':3003,'readonly':2000,'pda':2006}[mutation]
     if mutation=='short0':change_data(key,b'')
     elif mutation=='short8':change_data(key,data[:8])
     elif mutation=='discriminator':change_data(key,bytes(8)+data[8:])
     elif mutation=='owner':expected['accounts'][key]['owner']=pub('close-wrong-owner')
     elif mutation=='invalid_enum':change_data(key,data[:9]+b'\2'+data[10:])
     elif mutation=='readonly':metas[index]['writable']=False
     else:
      wrong=pub('close-wrong-'+label);expected['accounts'][wrong]=copy.deepcopy(expected['accounts'][key]);metas[index]['pubkey']=wrong
    assert expected==result['fixture'];left,prior,right=[result['results'][k] for k in ['original','control','candidate']];keys=check_tx([left,prior,right],expected);assert not result['mismatches']['candidate'] and comparable(left)==comparable(right)
    if result['mismatches']['control']:assert kind in ['missing_0','missing_1'] and result['mismatches']['control']==['logs'];negative.add(kind)
    else:assert comparable(left)==comparable(prior)
    for label,row in result['results'].items():
     assert row['before'][wire.RELAY]['data_sha256']==report['binary_hashes'][label]
     for key,value in expected['accounts'].items():
      before=row['before'][key]
      if before is None:assert value=={'lamports':0,'data_base64':'','owner':wire.SYSTEM,'executable':False,'rent_epoch':0}
      else:assert all(before[field]==value[field] for field in ['lamports','owner','executable','rent_epoch','data_base64']) and before['data_sha256']==H(base64.b64decode(value['data_base64']))
     assert row['error'] is not None and (('Custom('+str(error)+')') in row['error'].replace(' ','') if isinstance(error,int) else error in row['error']);assert not row['return_data']['data'] and not any(s.startswith('Program data: ') for s in row['logs'])
     if kind in ['wrong_relayer','suffix','distribution_prefunded']:
      assert any('account: signer.' in s and 'ConstraintAddress' in s for s in row['logs']) and any(signer in s for s in row['logs']) and any(relayer in s for s in row['logs'])
      calls=[]
      for group in row['inner_instructions']:
       for call in group:
        ix=call['instruction'];calls.append((keys[ix['programIdIndex']],wire.wire_vec(ix['data']),[keys[i] for i in wire.wire_vec(ix['accounts'])],call['stackHeight']))
      system=[(data,accounts,height) for pid,data,accounts,height in calls if pid==wire.SYSTEM];rent=(98+128)*3480*2
      distribution_calls=[((2).to_bytes(4,'little')+(rent-1).to_bytes(8,'little'),[signer,dist],2),((8).to_bytes(4,'little')+(98).to_bytes(8,'little'),[dist],2),((1).to_bytes(4,'little')+wire.un58(wire.RELAY),[dist],2)] if kind=='distribution_prefunded' else [((0).to_bytes(4,'little')+rent.to_bytes(8,'little')+(98).to_bytes(8,'little')+wire.un58(wire.RELAY),[signer,dist],2)]
      ata_create=((0).to_bytes(4,'little')+((165+128)*3480*2).to_bytes(8,'little')+(165).to_bytes(8,'little')+wire.un58(token),[signer,dest],3);assert system==distribution_calls+[ata_create]
      assert [(data,accounts,height) for pid,data,accounts,height in calls if pid==ata]==[(b'\0',[signer,dest,dist,mint,wire.SYSTEM,token],2)]
      assert [(data,accounts,height) for pid,data,accounts,height in calls if pid==token]==[(b'\x15\x07\0',[mint],3),(b'\x16',[dest],3),(b'\x12'+wire.un58(dist),[dest,mint],3)]
    counts['receipt_cases']+=1
   expected_kinds={'wrong_relayer','suffix','distribution_prefunded','distribution_exists','destination_exists','signer_missing','signer_readonly','distribution_readonly','destination_readonly','mint_readonly','debouncer_token_mint','debouncer_token_authority','mint_address','distribution_pda'}|{'missing_'+str(i) for i in range(12)}|{name+'_'+kind for name in ['epoch_tracker','debouncer'] for kind in ['short0','short8','discriminator','owner','invalid_enum','readonly','pda']};assert seen==expected_kinds and negative=={'missing_0','missing_1'}
  if (d/'just-cases.json').exists():
   report=read_json(d/'just-cases.json');assert report['all_requested_completed'] and report['passed']==55 and len(report['cases'])==55
   assert report['binary_hashes']=={'original':H(original.b),'control':H((ROOT/'repro/donation-relay/epoch-close-source-recovery/close/candidate.so').read_bytes()),'candidate':build['candidate_sha256']}
   token='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';ata='ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL';relayer='RLYRf96HAJSbbXCNS6ibQYnkxtb6kbfuFxqEkm9oQUc';output='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';jupiter='JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4';seen=set();negative=set();f=frozen['donate_v1']
   def pub(label):return wire.b58(hashlib.sha256(('relay-local-data/'+label).encode()).digest())
   def state_account(data,program):return {'lamports':(len(data)+128)*3480*2,'data_base64':base64.b64encode(data).decode(),'owner':program,'executable':False,'rent_epoch':0}
   def pda_bump(key,seeds,program):
    matches=[b for b in range(256) if hashlib.sha256(b''.join(seeds)+bytes([b])+wire.un58(program)+b'ProgramDerivedAddress').digest()==wire.un58(key)];assert len(matches)==1
    if signatures:
     from solders.pubkey import Pubkey
     actual,bump=Pubkey.find_program_address(seeds,Pubkey.from_string(program));assert str(actual)==key and bump==matches[0]
    return matches[0]
   def token_bytes(mint,authority,amount):
    b=bytearray(165);b[:32]=wire.un58(mint);b[32:64]=wire.un58(authority);b[64:72]=amount.to_bytes(8,'little');b[108]=1;return bytes(b)
   for result in report['cases']:
    kind=result['kind'];assert kind not in seen;seen.add(kind);assert result['base_case']==f['case'] and result['base_fixture']==f['fixture'];expected=copy.deepcopy(f['fixture']);new=result['canonical_fixture'];config=bytes.fromhex(expected['instruction_hex'])[16:48];mint=expected['instruction_accounts'][3]['pubkey'];signer=expected['instruction_accounts'][5]['pubkey'];assert signer!=relayer;epoch=3;gross=4000000;c=expected['canonical_pdas'];nc=new['canonical_pdas'];dist=nc['distribution'];receipt=nc['swap_receipt'];source=nc['distribution_token_account'];dest=nc['output_distribution_token_account'];db=pda_bump(dist,[b'distribution_v1',config,wire.un58(mint),epoch.to_bytes(16,'little')],wire.RELAY);rb=pda_bump(receipt,[b'swap_receipt_v1',wire.un58(dist)],wire.RELAY)
    pda_bump(source,[wire.un58(dist),wire.un58(token),wire.un58(mint)],ata);pda_bump(dest,[wire.un58(dist),wire.un58(token),wire.un58(output)],ata)
    for k in [expected['source_token_or_temp'],c['mint_whitelist'],c['debouncer_token_account']]:expected['accounts'].pop(k)
    for k in ['mint_whitelist','debouncer_token_account']:c.pop(k)
    c.update(distribution=dist,swap_receipt=receipt,distribution_token_account=source,output_distribution_token_account=dest)
    for label,name,tail in [('epoch_tracker','EpochTrackerV1',(epoch+1).to_bytes(16,'little')),('debouncer','DebouncerV1',bytes(8)),('distribution','DistributionV1',epoch.to_bytes(16,'little')+gross.to_bytes(8,'little'))]:
     bump=db if label=='distribution' else pda_bump(c[label],[label.encode()+b'_v1',config,wire.un58(mint)],wire.RELAY);expected['accounts'][c[label]]=state_account(wire.account_disc(name)+bytes([bump,1])+config+wire.un58(mint)+tail,wire.RELAY)
    expected['accounts'][source]=state_account(token_bytes(mint,dist,gross),token);mint_data=bytearray(82);mint_data[36:44]=(10**12).to_bytes(8,'little');mint_data[44]=6;mint_data[45]=1;expected['accounts'][output]=state_account(bytes(mint_data),token)
    for key in [receipt,dest,jupiter]:expected['accounts'][key]={'lamports':0,'data_base64':'','owner':wire.SYSTEM,'executable':False,'rent_epoch':0}
    expected.pop('source_token_or_temp');expected.update(epoch=epoch,gross=gross,distribution_bump=db,receipt_bump=rb,instruction_hex=(bytes([204,159,132,117,132,86,223,73])+bytes(4)).hex())
    names=[c['epoch_tracker'],c['debouncer'],dist,receipt,source,dest,mint,output,token,signer,token,jupiter,ata,wire.SYSTEM,c['event_authority'],wire.RELAY];writable={2,3,4,5,6,7,9};expected['instruction_accounts']=[dict(pubkey=k,signer=i==9,writable=i in writable) for i,k in enumerate(names)];assert expected==new
    expected=copy.deepcopy(expected);metas=expected['instruction_accounts'];error=None
    def change_data(key,data):expected['accounts'][key]['data_base64']=base64.b64encode(data).decode()
    if kind in ['wrong_relayer','suffix','receipt_prefunded']:
     error=2012
     if kind=='suffix':expected['instruction_hex']+=b'ignored suffix'.hex()
     if kind=='receipt_prefunded':expected['accounts'][receipt]['lamports']=1
    elif kind=='receipt_exists':expected['accounts'][receipt]=state_account(wire.account_disc('SwapReceiptV1')+bytes([rb])+wire.un58(dist)+gross.to_bytes(8,'little'),wire.RELAY);error=0
    elif kind=='destination_exists':expected['accounts'][dest]=state_account(token_bytes(output,dist,0),token);error='IllegalOwner'
    elif kind=='signer_missing':metas[9]['signer']=False;error=3010
    elif kind in ['signer_readonly','receipt_readonly','distribution_readonly','destination_readonly','mint_readonly','output_mint_readonly']:
     metas[{'signer_readonly':9,'receipt_readonly':3,'distribution_readonly':2,'destination_readonly':5,'mint_readonly':6,'output_mint_readonly':7}[kind]]['writable']=False;error=2000 if kind in ['distribution_readonly','mint_readonly','output_mint_readonly'] else 'PrivilegeEscalation'
    elif kind in ['input_token_mint','input_token_authority']:
     data=base64.b64decode(expected['accounts'][source]['data_base64']);off=0 if kind.endswith('_mint') else 32;change_data(source,data[:off]+wire.un58(pub('just-wrong-token-field'))+data[off+32:]);error=2012 if off==0 else 2015
    elif kind=='debouncer_mint_field':
     key=c['debouncer'];data=base64.b64decode(expected['accounts'][key]['data_base64']);change_data(key,data[:42]+wire.un58(pub('just-wrong-debouncer-mint'))+data[74:]);error=2012
    elif kind in ['mint_address','output_mint_address']:
     index=6 if kind=='mint_address' else 7;wrong=pub('just-wrong-mint-address');expected['accounts'][wrong]=copy.deepcopy(expected['accounts'][metas[index]['pubkey']]);metas[index]['pubkey']=wrong;error=2009 if index==6 else 'MissingAccount'
    elif kind in ['receipt_pda','distribution_pda','jupiter_address']:
     index={'receipt_pda':3,'distribution_pda':2,'jupiter_address':11}[kind];wrong=pub('just-'+kind);expected['accounts'][wrong]=copy.deepcopy(expected['accounts'][metas[index]['pubkey']]);metas[index]['pubkey']=wrong;error=2012 if index==11 else 2006
    elif kind.startswith('missing_'):expected['instruction_accounts']=metas[:int(kind.split('_')[1])];error=3005
    else:
     label,mutation=next((name,kind[len(name)+1:]) for name in ['epoch_tracker','debouncer','distribution'] if kind.startswith(name+'_'));index={'epoch_tracker':0,'debouncer':1,'distribution':2}[label];key=c[label];data=base64.b64decode(expected['accounts'][key]['data_base64']);error={'short0':3001,'short8':3003,'discriminator':3002,'owner':3007,'invalid_enum':3003,'readonly':2012,'pda':2006}[mutation]
     if mutation=='short0':change_data(key,b'')
     elif mutation=='short8':change_data(key,data[:8])
     elif mutation=='discriminator':change_data(key,bytes(8)+data[8:])
     elif mutation=='owner':expected['accounts'][key]['owner']=pub('just-wrong-owner')
     elif mutation=='invalid_enum':change_data(key,data[:9]+b'\2'+data[10:])
     elif mutation=='readonly':metas[index]['writable']=False
     else:
      wrong=pub('just-wrong-'+label);expected['accounts'][wrong]=copy.deepcopy(expected['accounts'][key]);metas[index]['pubkey']=wrong
    assert expected==result['fixture'];left,prior,right=[result['results'][k] for k in ['original','control','candidate']];keys=check_tx([left,prior,right],expected);assert not result['mismatches']['candidate'] and comparable(left)==comparable(right)
    if result['mismatches']['control']:assert kind in ['missing_3','missing_5','debouncer_mint_field'] and result['mismatches']['control']==['logs'];negative.add(kind)
    else:assert comparable(left)==comparable(prior)
    for label,row in result['results'].items():
     assert row['before'][wire.RELAY]['data_sha256']==report['binary_hashes'][label]
     for key,value in expected['accounts'].items():
      before=row['before'][key]
      if before is None:assert value=={'lamports':0,'data_base64':'','owner':wire.SYSTEM,'executable':False,'rent_epoch':0}
      else:assert all(before[field]==value[field] for field in ['lamports','owner','executable','rent_epoch','data_base64']) and before['data_sha256']==H(base64.b64decode(value['data_base64']))
     assert row['error'] is not None and (('Custom('+str(error)+')') in row['error'].replace(' ','') if isinstance(error,int) else error in row['error']);assert not row['return_data']['data'] and not any(s.startswith('Program data: ') for s in row['logs'])
     if kind in ['wrong_relayer','suffix','receipt_prefunded']:
      assert any('account: signer.' in s and 'ConstraintAddress' in s for s in row['logs']) and any(signer in s for s in row['logs']) and any(relayer in s for s in row['logs'])
      calls=[]
      for group in row['inner_instructions']:
       for call in group:
        ix=call['instruction'];calls.append((keys[ix['programIdIndex']],wire.wire_vec(ix['data']),[keys[i] for i in wire.wire_vec(ix['accounts'])],call['stackHeight']))
      system=[(data,accounts,height) for pid,data,accounts,height in calls if pid==wire.SYSTEM];rent=(49+128)*3480*2
      receipt_calls=[((2).to_bytes(4,'little')+(rent-1).to_bytes(8,'little'),[signer,receipt],2),((8).to_bytes(4,'little')+(49).to_bytes(8,'little'),[receipt],2),((1).to_bytes(4,'little')+wire.un58(wire.RELAY),[receipt],2)] if kind=='receipt_prefunded' else [((0).to_bytes(4,'little')+rent.to_bytes(8,'little')+(49).to_bytes(8,'little')+wire.un58(wire.RELAY),[signer,receipt],2)]
      ata_create=((0).to_bytes(4,'little')+((165+128)*3480*2).to_bytes(8,'little')+(165).to_bytes(8,'little')+wire.un58(token),[signer,dest],3);assert system==receipt_calls+[ata_create]
      assert [(data,accounts,height) for pid,data,accounts,height in calls if pid==ata]==[(b'\0',[signer,dest,dist,output,wire.SYSTEM,token],2)]
      assert [(data,accounts,height) for pid,data,accounts,height in calls if pid==token]==[(b'\x15\x07\0',[output],3),(b'\x16',[dest],3),(b'\x12'+wire.un58(dist),[dest,output],3)]
    counts['receipt_cases']+=1
   expected_kinds={'wrong_relayer','suffix','receipt_prefunded','receipt_exists','destination_exists','signer_missing','signer_readonly','receipt_readonly','distribution_readonly','destination_readonly','mint_readonly','output_mint_readonly','input_token_mint','input_token_authority','output_mint_address','mint_address','receipt_pda','distribution_pda','jupiter_address','debouncer_mint_field'}|{'missing_'+str(i) for i in range(16)}|{name+'_'+kind for name in ['epoch_tracker','debouncer','distribution'] for kind in ['short0','short8','discriminator','owner','invalid_enum','readonly','pda']};assert seen==expected_kinds and negative=={'missing_3','missing_5','debouncer_mint_field'}
 print(json.dumps(dict(verified=True,**counts,cryptographic_signatures_checked=signatures,vm_execution=False)))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',action='store_true');args=ap.parse_args();main(args.runtime)
