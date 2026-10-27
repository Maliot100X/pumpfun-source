#!/usr/bin/env python3
"""Independent saved-run verifier; no VM construction or target execution."""
import argparse,base64,hashlib,importlib.util,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
ALPHABET='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
RELAY='RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu';SYSTEM='11111111111111111111111111111111'
def b58(b):
 n=int.from_bytes(b,'big');s=''
 while n:n,r=divmod(n,58);s=ALPHABET[r]+s
 return '1'*(len(b)-len(b.lstrip(b'\0')))+s

def un58(s):
 n=0
 for c in s:n=n*58+ALPHABET.index(c)
 return b'\0'*(len(s)-len(s.lstrip('1')))+(n.to_bytes((n.bit_length()+7)//8,'big') if n else b'')
def short(data,pos):
 n=0;shift=0
 while True:
  c=data[pos];pos+=1;n|=(c&127)<<shift
  if not c&128:return n,pos
  shift+=7;assert shift<=21

def parse(raw):
 count,p=short(raw,0);sig=[raw[p+i*64:p+(i+1)*64] for i in range(count)];p+=count*64;message=raw[p:];n,ro,ru=raw[p:p+3];p+=3;assert n==count
 count,p=short(raw,p);keys=[raw[p+i*32:p+(i+1)*32] for i in range(count)];p+=count*32;blockhash=raw[p:p+32];p+=32
 count,p=short(raw,p);instructions=[]
 for _ in range(count):
  program=raw[p];p+=1;length,p=short(raw,p);accounts=list(raw[p:p+length]);p+=length;length,p=short(raw,p);data=raw[p:p+length];p+=length;instructions.append((program,accounts,data))
 assert p==len(raw)
 return {'signatures':sig,'message':message,'keys':keys,'blockhash':blockhash,'instructions':instructions,'required':n,'readonly_signers':ro,'readonly_unsigned':ru}

def wire_vec(x):
 assert isinstance(x[0],list);n,_=short(bytes(x[0]),0);assert n==len(x)-1
 return bytes(x[1:])
def data(row,k,stage='after'):
 a=row[stage].get(k);return b'' if a is None else base64.b64decode(a['data_base64'])
def integer(b):return int.from_bytes(b,'little')
def account_disc(name):return hashlib.sha256(('account:'+name).encode()).digest()[:8]
def independent_effects(case,fixture,row,keys):
 ix=bytes.fromhex(fixture['instruction_hex']);metas=fixture['instruction_accounts']
 if case['kind']=='donation':
  c=fixture['canonical_pdas'];tracker=data(row,c['epoch_tracker']);debouncer=data(row,c['debouncer']);vault=data(row,c['debouncer_token_account']);mint=un58(metas[3]['pubkey']);config=ix[16:48];amount=integer(ix[8:16]);tip=integer(ix[48:50]);length=integer(ix[50:54]);message=ix[54:54+length];credited=ix[54+length:]
  assert tracker[:8]==account_disc('EpochTrackerV1') and tracker[9:10]==b'\1' and tracker[10:42]==config and tracker[42:74]==mint and integer(tracker[74:90])==0
  assert debouncer[:8]==account_disc('DebouncerV1') and debouncer[9:10]==b'\1' and debouncer[10:42]==config and debouncer[42:74]==mint and integer(debouncer[74:82])==amount
  assert vault[:32]==mint and vault[32:64]==un58(c['debouncer']) and integer(vault[64:72])==amount
  source=fixture['source_token_or_temp']
  if 'native' in case['name']:
   a=row['after'].get(source);assert a is None or (a['lamports']==0 and a['owner']==SYSTEM and a['data_length']==0)
  else:assert integer(data(row,source,'before')[64:72])-integer(data(row,source)[64:72])==amount
  payload=b'\0'+config+mint+bytes(16)+amount.to_bytes(8,'little')+(amount*tip//10000).to_bytes(8,'little')+length.to_bytes(4,'little')+message+credited
  assert bytes(row['return_data']['program_id'])==un58(RELAY) and bytes(row['return_data']['data'])==payload
  event=bytes.fromhex('a5e556edf44d26de')+payload
  assert [s for s in row['logs'] if s.startswith('Program data: ')]==['Program data: '+base64.b64encode(event).decode()]
  calls=[c['instruction'] for group in row['inner_instructions'] for c in group if keys[c['instruction']['programIdIndex']]==RELAY]
  assert len(calls)==1 and wire_vec(calls[0]['data'])==bytes.fromhex('e445a52e51cb9a1d')+event
  assert [keys[x] for x in wire_vec(calls[0]['accounts'])]==[c['event_authority']]
 else:
  op=case['operation'];header=bytes.fromhex('184662bf3a907b9e');k=metas[0]['pubkey'];b=data(row,k)
  assert not row['return_data']['data'] and not any(s.startswith('Program data: ') for s in row['logs'])
  if op==0:
   k=fixture['canonical_pdas']['canonical_idl'];b=data(row,k);authority=un58(metas[0]['pubkey']);assert b==header+authority+bytes(132)
  elif op==1:assert b==header+un58(metas[1]['pubkey'])+bytes(132)
  elif op==2:
   length=integer(ix[9:13]);payload=ix[13:];assert length==len(payload);assert b==header+un58(metas[1]['pubkey'])+length.to_bytes(4,'little')+payload+bytes(128-length)
  elif op==3:
   src=data(row,k,'before');length=integer(src[40:44]);assert data(row,k)==src;target=data(row,metas[1]['pubkey']);assert target==header+un58(metas[2]['pubkey'])+length.to_bytes(4,'little')+src[44:44+length]+bytes(128-length)
  elif op==4:assert b==header+ix[9:41]+bytes(132)
  elif op==5:
   a=row['after'].get(k);assert a is None or (a['lamports']==0 and a['owner']==SYSTEM and a['data_length']==0)
   destination=metas[2]['pubkey'];assert row['after'][destination]['lamports']-row['before'][destination]['lamports']==row['before'][k]['lamports']
  elif op==6:
   assert b==header+un58(metas[1]['pubkey'])+bytes(88)
   authority=metas[1]['pubkey'];assert row['before'][authority]['lamports']-row['after'][authority]['lamports']==row['after'][k]['lamports']-row['before'][k]['lamports']

def verify(repo,runtime=False):
 manifest=json.loads((P/'manifest.json').read_text());assert H((P/'manifest.json').read_bytes())==(P/'manifest.sha256').read_text().split()[0]
 files={str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and str(p.relative_to(P)) not in ['manifest.json','manifest.sha256']};assert files==set(manifest)
 for n,h in manifest.items():assert not(P/n).is_symlink() and H((P/n).read_bytes())==h,n
 proposal=repo/'repro/donation-relay/local-validation-proposal'
 build=P.parent
 assert H((proposal/'manifest.json').read_bytes())=='2ecc00fa48a19065fae6a2e8a43a9ab5ad4fe5de7c514b6fd3cd93faa118012c'
 assert H((build/'pre-runtime-manifest.json').read_bytes())=='58cfd337ed90725dfee23e1cc347f19f65db8d3ce0aa2c62f54e43d846a0c7a4'
 spec=importlib.util.spec_from_file_location('frozen_relay_proposal_verify',proposal/'verify.py');pv=importlib.util.module_from_spec(spec);spec.loader.exec_module(pv);pv.verify(runtime=runtime)
 run=json.loads((P/'ordinary.json').read_text());process=json.loads((P/'process-result.json').read_text());launch=json.loads((P/'launch.json').read_text());frozen=json.loads((proposal/'fixture-blueprints.json').read_text());frozen=[x for x in frozen if x['case']['group']=='ordinary']
 assert process=={'returncode':0,'harness_unchanged':True,'candidate_unchanged':True,'report_exists':True}
 assert launch['harness_sha256']==H((proposal/'harness_proposal.py').read_bytes())=='fd6df62699bc5732fffca65d7e6b5c1c872746180563ca3e320f7dbe11f7cb1b'
 assert launch['adapter_sha256']==H((P/'adapter.py').read_bytes())
 assert launch['proposal_seal']==H((proposal/'manifest.json').read_bytes()) and launch['build07_seal']==H((build/'pre-runtime-manifest.json').read_bytes())
 assert launch['source_map']==json.loads((build/'launcher/resolved-source-sha256.json').read_text())
 expected='34c54b8e1e625a46fd446bb8e6fa7c7f17afcb1fd7d2ef3719a16f630c98ce91'
 assert launch['runtime_expected']==dict(launch['original_expected'],candidate=expected)
 assert launch['original_expected']['candidate']=='4954fdc437beed0f73e00d25f1df656ce7fdf0279f8f9bb8e70ca0bced4b53dd'
 bindings={'candidate_sha256':expected,'original_sha256':launch['runtime_expected']['original'],'proposal_manifest_sha256':launch['proposal_seal']}
 assert H((build/'candidate.so').read_bytes())==expected
 assert run['group']=='ordinary' and run['case_count']==run['passed']==len(run['cases'])==12 and run['all_requested_completed']
 assert run['candidate_sha256']==bindings['candidate_sha256'] and run['original_sha256']==bindings['original_sha256']
 assert run['harness_sha256']==launch['harness_sha256'] and run['proposal_manifest_sha256']==bindings['proposal_manifest_sha256']
 assert run['normal_signature_blockhash_history_checks'] and not run['historical_transactions_rewritten']
 assert run['runtime_sha256_map']==json.loads((proposal/'loader-results.json').read_text())['runtime_files']
 signatures=0;unique=set();effects=0
 for result,f in zip(run['cases'],frozen):
  assert result['case']==f['case'] and result['fixture']==f['fixture'] and not result['mismatches']
  a,b=result['original'],result['candidate'];assert a['transaction_base64']==b['transaction_base64'];raw=base64.b64decode(a['transaction_base64']);tx=parse(raw);unique.add(H(raw));keys=list(map(b58,tx['keys']))
  assert b58(tx['blockhash'])==json.loads((proposal/'loader-results.json').read_text())['results'][0]['latest_blockhash']
  assert keys[0]==f['fee_payer'] and set(keys[:tx['required']])==set(f['required_test_owned_signers'])
  assert len(tx['instructions'])==2
  budget,call=tx['instructions'];assert keys[budget[0]]=='ComputeBudget111111111111111111111111111111' and not budget[1] and budget[2]==b'\2'+(1400000).to_bytes(4,'little')
  assert keys[call[0]]==RELAY and call[2].hex()==f['fixture']['instruction_hex'] and [keys[x] for x in call[1]]==[x['pubkey'] for x in f['fixture']['instruction_accounts']]
  privileges={x['pubkey']:(x['signer'],x['writable']) for x in f['fixture']['instruction_accounts']};privileges[f['fee_payer']]=(True,True);privileges[RELAY]=(False,False);privileges[keys[budget[0]]]=(False,False)
  assert set(keys)==set(privileges)
  for index,k in enumerate(keys):
   signer=index<tx['required'];writable=index<tx['required']-tx['readonly_signers'] if signer else index<len(keys)-tx['readonly_unsigned'];assert (signer,writable)==privileges[k],k
  if runtime:
   from solders.signature import Signature
   from solders.pubkey import Pubkey
   assert all(Signature.from_bytes(s).verify(Pubkey.from_bytes(k),tx['message']) for s,k in zip(tx['signatures'],tx['keys']))
  for row in [a,b]:
   assert row['error'] is None and row['signature_verification']==[True]*tx['required'];signatures+=tx['required']
   assert row['metadata']['signature']==b58(tx['signatures'][0])
   for key in ['logs','inner_instructions','return_data']:assert row[key]==row['metadata'][key]
   expected_watch=set(f['fixture']['accounts'])|set(keys);assert set(row['before'])==set(row['after'])==expected_watch
   for k,x in f['fixture']['accounts'].items():
    y=row['before'][k]
    if y is None:assert x['lamports']==0 and x['data_base64']=='' and x['owner']==SYSTEM and not x['executable']
    else:
     assert all(y[field]==x[field] for field in x);assert y['data_length']==len(base64.b64decode(x['data_base64'])) and y['data_sha256']==H(base64.b64decode(x['data_base64']))
   for stage in ['before','after']:
    for account in row[stage].values():
     if account is not None and not account['executable']:
      rawdata=base64.b64decode(account['data_base64']);assert len(rawdata)==account['data_length'] and H(rawdata)==account['data_sha256']
   assert sum(x['lamports'] for x in row['before'].values() if x)-sum(x['lamports'] for x in row['after'].values() if x)==5000*tx['required']
   independent_effects(f['case'],f['fixture'],row,keys);effects+=1
  for key in ['error','inner_instructions','return_data']:assert a[key]==b[key]
  meter=lambda logs:[x for x in logs if re.fullmatch(r'Program \S+ consumed \d+ of \d+ compute units',x) is None]
  assert meter(a['logs'])==meter(b['logs'])
  for stage in ['before','after']:
   for k in a[stage]:
    x,y=a[stage][k],b[stage][k]
    if k!=RELAY:assert x==y
    else:
     assert x['executable'] and y['executable']
     assert all(x[field]==y[field] for field in ['owner','executable','rent_epoch'])
     assert x['lamports']-a['before'][k]['lamports']==y['lamports']-b['before'][k]['lamports']
     assert x['data_sha256']==bindings['original_sha256'] and y['data_sha256']==bindings['candidate_sha256']
 assert len(unique)==12 and signatures==50 and effects==24
 return {'verified':True,'cases':12,'transaction_submissions':24,'unique_transactions':12,'encoded_signature_fields_checked':signatures,'unique_transaction_signatures':signatures//2,'effects_checked':effects,'runtime_signature_reverification':runtime,'new_transactions_executed_by_verifier':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--runtime',action='store_true');a=p.parse_args();print(json.dumps(verify(a.repo.resolve(),a.runtime),indent=2))
