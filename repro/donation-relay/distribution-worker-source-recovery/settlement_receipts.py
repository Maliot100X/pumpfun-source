"""Independent saved-fixture, signed-transaction, CPI and rollback checks; no VM execution."""
from pathlib import Path
import json,base64,copy,hashlib
TOKEN='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';ATA='ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL';USDC='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';JUPITER='JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'
H=lambda b:hashlib.sha256(b).hexdigest()
def audit(P,ROOT,d,build,frozen,wire,check_tx,comparable,signatures,counts):
 def pub(label):return wire.b58(hashlib.sha256(('relay-local-data/'+label).encode()).digest())
 def account(data,owner,lamports=None):return dict(lamports=(len(data)+128)*3480*2 if lamports is None else lamports,data_base64=base64.b64encode(data).decode(),owner=owner,executable=False,rent_epoch=0)
 def empty():return account(b'',wire.SYSTEM,0)
 def token(mint,authority,amount):
  b=bytearray(165);b[:32]=wire.un58(mint);b[32:64]=wire.un58(authority);b[64:72]=amount.to_bytes(8,'little');b[108]=1;return bytes(b)
 def pda(key,seeds,program=wire.RELAY):
  found=[b for b in range(256) if hashlib.sha256(b''.join(seeds)+bytes([b])+wire.un58(program)+b'ProgramDerivedAddress').digest()==wire.un58(key)];assert len(found)==1
  if signatures:
   from solders.pubkey import Pubkey
   actual,bump=Pubkey.find_program_address(seeds,Pubkey.from_string(program));assert str(actual)==key and bump==found[0]
  return found[0]
 def canonical(route,row):
  f=frozen['donate_v1'];assert row['base_case']==f['case'] and row['base_fixture']==f['fixture'];e=copy.deepcopy(f['fixture']);base_mint=e['instruction_accounts'][3]['pubkey'];signer=e['instruction_accounts'][5]['pubkey'];recipient=e['test_owned_pubkeys'][2];assert signer!='RLYRf96HAJSbbXCNS6ibQYnkxtb6kbfuFxqEkm9oQUc';config=bytes.fromhex(e['instruction_hex'])[16:48];old=e['canonical_pdas'];new=row['canonical_fixture']['canonical_pdas'];mint=USDC if route=='non_swap' else base_mint;epoch=3;gross=4000000
  remove=[e['source_token_or_temp'],old['mint_whitelist'],old['debouncer_token_account']]
  if route!='combined':remove += [old['epoch_tracker'],old['debouncer']]
  for key in remove:e['accounts'].pop(key)
  if route=='combined':
   c=copy.deepcopy(old);c.pop('mint_whitelist');c.pop('debouncer_token_account');c.update(distribution=new['distribution'],distribution_token_account=new['distribution_token_account'],output_distribution_token_account=new['output_distribution_token_account'])
  else:
   c={key:new[key] for key in ['epoch_tracker','debouncer','distribution']};c['event_authority']=old['event_authority'];c['output_distribution_token_account' if route=='after' else 'distribution_token_account']=new['output_distribution_token_account' if route=='after' else 'distribution_token_account']
   if route=='after':c['swap_receipt']=new['swap_receipt']
  dist=c['distribution'];db=pda(dist,[b'distribution_v1',config,wire.un58(mint),epoch.to_bytes(16,'little')]);e['canonical_pdas']=c
  for label,name,size,tail in [('epoch_tracker','EpochTrackerV1',90,(epoch+1).to_bytes(16,'little')),('debouncer','DebouncerV1',82,bytes(8)),('distribution','DistributionV1',98,epoch.to_bytes(16,'little')+gross.to_bytes(8,'little'))]:
   bump=db if label=='distribution' else pda(c[label],[label.encode()+b'_v1',config,wire.un58(mint)]);data=wire.account_disc(name)+bytes([bump,1])+config+wire.un58(mint)+tail;assert len(data)==size;e['accounts'][c[label]]=account(data,wire.RELAY)
  mint_data=bytearray(82);mint_data[36:44]=(10**12).to_bytes(8,'little');mint_data[44]=6;mint_data[45]=1;e['accounts'][USDC]=account(bytes(mint_data),TOKEN)
  if route=='after':
   rb=pda(c['swap_receipt'],[b'swap_receipt_v1',wire.un58(dist)]);e['accounts'][c['swap_receipt']]=account(wire.account_disc('SwapReceiptV1')+bytes([rb])+wire.un58(dist)+(2000000).to_bytes(8,'little'),wire.RELAY);e['receipt_bump']=rb
  if route=='combined':
   source=c['distribution_token_account'];dest=c['output_distribution_token_account'];pda(source,[wire.un58(dist),wire.un58(TOKEN),wire.un58(mint)],ATA);pda(dest,[wire.un58(dist),wire.un58(TOKEN),wire.un58(USDC)],ATA);e['accounts'][source]=account(token(mint,dist,gross),TOKEN)
   for key in [dest,JUPITER]:e['accounts'][key]=empty()
   names=[c['epoch_tracker'],c['debouncer'],dist,source,dest,mint,USDC,TOKEN,signer,TOKEN,JUPITER,ATA,wire.SYSTEM,c['event_authority'],wire.RELAY];writable={2,3,4,5,6,8};signer_index=8;selector=bytes([218,85,237,178,24,174,102,41]);prefix=bytes(4)
  else:
   source=c['output_distribution_token_account' if route=='after' else 'distribution_token_account'];pda(source,[wire.un58(dist),wire.un58(TOKEN),wire.un58(USDC)],ATA);e['accounts'][source]=account(token(USDC,dist,2000000 if route=='after' else gross),TOKEN)
   if route=='after':names=[c['epoch_tracker'],c['debouncer'],dist,c['swap_receipt'],source,USDC,TOKEN,signer,ATA,wire.SYSTEM,c['event_authority'],wire.RELAY];writable={2,3,4,5,7};signer_index=7;selector=bytes([210,176,49,190,147,105,115,119])
   else:names=[c['epoch_tracker'],c['debouncer'],dist,source,USDC,signer,TOKEN,ATA,wire.SYSTEM,c['event_authority'],wire.RELAY];writable={2,3,4,5};signer_index=5;selector=bytes([152,149,100,48,118,236,9,243])
   prefix=b'';e.update(route=route,output=2000000,recipient=recipient)
  raw=selector+prefix+(1).to_bytes(4,'little')+b'\0'+wire.un58(recipient)+(10000).to_bytes(2,'little');e.pop('source_token_or_temp');e.update(epoch=epoch,gross=gross,distribution_bump=db,instruction_hex=raw.hex(),instruction_accounts=[dict(pubkey=k,signer=i==signer_index,writable=i in writable) for i,k in enumerate(names)]);assert e==row['canonical_fixture'];return e
 def mutation(e,route,kind):
  c=e['canonical_pdas'];metas=e['instruction_accounts'];combined=route=='combined';raw=bytes.fromhex(e['instruction_hex']);prefix=12 if combined else 8;mint_index=5 if combined or route=='after' else 4;signer_index=8 if combined else 7 if route=='after' else 5;source_index=3 if combined or route=='non_swap' else 4;source=c['distribution_token_account' if combined or route=='non_swap' else 'output_distribution_token_account'];dest=c.get('output_distribution_token_account');ata_index=11 if combined else 8 if route=='after' else 7;system_index=ata_index+1;recipient=e.get('recipient',e['test_owned_pubkeys'][2])
  def data(key):return base64.b64decode(e['accounts'][key]['data_base64'])
  def put(key,value):e['accounts'][key]['data_base64']=base64.b64encode(value).decode()
  def wrong_slot(index,key):e['accounts'][key]=copy.deepcopy(e['accounts'][metas[index]['pubkey']]);metas[index]['pubkey']=key
  err=2012
  if kind=='empty_shares':e['instruction_hex']=(raw[:prefix]+bytes(4)).hex()
  elif kind=='suffix':e['instruction_hex']+=b'ignored suffix'.hex()
  elif kind=='three_shares':e['instruction_hex']=(raw[:prefix]+(3).to_bytes(4,'little')+b''.join(bytes([tag])+wire.un58(recipient)+bps.to_bytes(2,'little') for tag,bps in [(0,0),(1,2500),(2,7500)])).hex()
  elif kind=='invalid_share_tag':e['instruction_hex']=(raw[:prefix+4]+b'\3'+raw[prefix+5:]).hex();err=102
  elif kind in ['short_arg_count','short_share','short_share_address','short_share_bps','short_share_count','short_data_count']:
   size={'short_arg_count':8,'short_share':prefix+4,'short_share_address':prefix+36,'short_share_bps':prefix+38,'short_share_count':15,'short_data_count':8}[kind];e['instruction_hex']=raw[:size].hex();err=102
  elif kind=='short_swap_data':e['instruction_hex']=(raw[:8]+(2).to_bytes(4,'little')+b'x').hex();err=102
  elif kind in ['count113_missing','count114_missing']:e['instruction_hex']=(raw[:prefix]+(113 if kind=='count113_missing' else 114).to_bytes(4,'little')+raw[prefix+4:]).hex();err=102
  elif kind=='destination_prefunded':e['accounts'][dest]['lamports']=1
  elif kind=='destination_exists':e['accounts'][dest]=account(token(USDC,c['distribution'],0),TOKEN);err='IllegalOwner'
  elif kind=='signer_missing':metas[signer_index]['signer']=False;err=3010
  elif kind in ['signer_readonly','mint_readonly','source_readonly','distribution_readonly','destination_readonly','output_mint_readonly']:
   index={'signer_readonly':signer_index,'mint_readonly':mint_index,'source_readonly':source_index,'distribution_readonly':2,'destination_readonly':4,'output_mint_readonly':6}[kind];metas[index]['writable']=False;err='PrivilegeEscalation' if combined and kind in ['signer_readonly','destination_readonly'] else 2000
  elif kind in ['source_mint','source_authority','input_token_mint','input_token_authority']:
   off=0 if kind.endswith('_mint') else 32;b=data(source);put(source,b[:off]+wire.un58(pub('combined-wrong-token-field' if combined else 'distribution-wrong-token-field'))+b[off+32:]);err=2012 if off==0 else 2015
  elif kind in ['source_owner','input_token_owner']:e['accounts'][source]['owner']=wire.SYSTEM;err=3007
  elif kind=='source_address':wrong_slot(source_index,pub('distribution-wrong-source'));err=2009
  elif kind in ['mint_address','output_mint_address']:
   index=5 if kind=='mint_address' else 6;wrong_slot(index,pub('combined-wrong-mint-address'));err=2009 if index==5 else 'MissingAccount'
  elif kind=='jupiter_address':wrong_slot(10,pub('combined-wrong-jupiter'))
  elif kind in ['wrong_token_program','wrong_output_program','wrong_system','wrong_ata']:
   index=({'wrong_token_program':9,'wrong_output_program':7,'wrong_system':12,'wrong_ata':11} if combined else {'wrong_token_program':6,'wrong_system':system_index,'wrong_ata':ata_index})[kind];metas[index]['pubkey']=wire.SYSTEM if 'program' in kind else TOKEN;err=3008
  elif kind=='distribution_close_alias':e['accounts'][metas[signer_index]['pubkey']]=copy.deepcopy(e['accounts'][c['distribution']]);metas[2]['pubkey']=metas[signer_index]['pubkey'];err=2006
  elif kind in ['debouncer_mint_field','distribution_mint_field','tracker_config_field','tracker_epoch_equal','distribution_uninitialized']:
   label='debouncer' if kind=='debouncer_mint_field' else 'epoch_tracker' if kind.startswith('tracker_') else 'distribution';key=c[label];b=data(key)
   if kind.endswith('_mint_field'):put(key,b[:42]+wire.un58(pub('combined-wrong-debouncer-mint' if combined else 'distribution-wrong-state-mint'))+b[74:]);err=2006 if kind=='distribution_mint_field' else 2012
   elif kind=='tracker_config_field':put(key,b[:10]+wire.un58(pub('distribution-wrong-state-config'))+b[42:])
   elif kind=='tracker_epoch_equal':put(key,b[:74]+e['epoch'].to_bytes(16,'little'))
   else:put(key,b[:9]+b'\0'+b[10:])
  elif kind=='remaining_extra':metas.append(dict(pubkey=recipient,signer=False,writable=False))
  elif kind in ['mint_owner','mint_short']:
   key=metas[mint_index]['pubkey']
   if kind=='mint_owner':e['accounts'][key]['owner']=wire.SYSTEM;err=3007
   else:put(key,b'');err='InvalidAccountData'
  elif kind.startswith('missing_'):e['instruction_accounts']=metas[:int(kind.split('_')[1])];err=3005
  elif kind!='wrong_relayer':
   label,change=next((n,kind[len(n)+1:]) for n in ['epoch_tracker','debouncer','distribution','receipt'] if kind.startswith(n+'_'));index={'epoch_tracker':0,'debouncer':1,'distribution':2,'receipt':3}[label];key=c['swap_receipt' if label=='receipt' else label];b=data(key);err={'short0':3001,'short8':3003,'discriminator':3002,'owner':3007,'invalid_enum':3003,'pda':'MissingAccount' if combined and label=='distribution' else 2006,'readonly':2000,'distribution':6033,'zero_output':2012,'close_alias':2006}[change]
   if change=='short0':put(key,b'')
   elif change=='short8':put(key,b[:8])
   elif change=='discriminator':put(key,bytes(8)+b[8:])
   elif change=='owner':e['accounts'][key]['owner']=pub('combined-wrong-owner' if combined else 'distribution-wrong-owner')
   elif change=='invalid_enum':put(key,b[:9]+b'\2'+b[10:])
   elif change=='pda':wrong_slot(index,pub(('combined-wrong-' if combined else 'distribution-wrong-')+label))
   elif change=='readonly':metas[index]['writable']=False
   elif change=='distribution':put(key,b[:9]+wire.un58(pub('distribution-wrong-receipt-distribution'))+b[41:])
   elif change=='zero_output':put(key,b[:41]+bytes(8))
   else:e['accounts'][metas[signer_index]['pubkey']]=copy.deepcopy(e['accounts'][key]);metas[index]['pubkey']=metas[signer_index]['pubkey']
  return e,err
 negative=set();seen=set();verified=0
 for filename,size in [('distribution-cases.json',132),('combined-cases.json',68)]:
  report=json.loads((d/filename).read_text());assert report['all_requested_completed'] and report['passed']==len(report['cases'])==report['unique_input_fixtures']==size;assert report['binary_hashes']==dict(original=H((ROOT/'evidence/dependencies/donation_relay/deployed.so').read_bytes()),control=H((ROOT/'repro/donation-relay/swap-body-source-recovery/swap/candidate.so').read_bytes()),candidate=build['candidate_sha256'])
  for row in report['cases']:
   route=row.get('route','combined');kind=row['kind'];e,err=mutation(canonical(route,row),route,kind);assert e==row['fixture'],(route,kind)
   digest=H(json.dumps({k:e[k] for k in ['accounts','instruction_hex','instruction_accounts']},sort_keys=True,separators=(',',':')).encode());assert digest==row['stimulus_sha256'] and digest not in seen;seen.add(digest)
   left,prior,right=[row['results'][n] for n in ['original','control','candidate']];keys=check_tx([left,prior,right],e);assert comparable(left)==comparable(right) and not row['mismatches']['candidate']
   if row['mismatches']['control']:
    assert row['mismatches']['control']==['logs'];negative.add((route,kind))
   else:assert comparable(left)==comparable(prior)
   for label,result in row['results'].items():
    assert result['before'][wire.RELAY]['data_sha256']==report['binary_hashes'][label]
    for program,sha in [(TOKEN,'8190d3f7ceb6cb7a7a8d8924bff89f9f611e15ce1f806f2b6237f3311a98f697'),(ATA,'6804554e69fd3a58caa191dc4a58f4c67223d30ca28ab8987f39fc18d2f7374d')]:
     if program in result['before']:assert result['before'][program]['data_sha256']==sha
    for key,value in e['accounts'].items():
     before=result['before'][key]
     if before is None:assert value==empty()
     else:assert all(before[k]==value[k] for k in ['lamports','owner','executable','rent_epoch','data_base64']) and before['data_sha256']==H(base64.b64decode(value['data_base64']))
    error=result['error'];assert error is not None and (('Custom('+str(err)+')') in error.replace(' ','') if isinstance(err,int) else err in error),(route,kind,err,error)
    assert not result['return_data']['data'] and not any(x.startswith('Program data: ') for x in result['logs'])
    calls=[]
    for group in result['inner_instructions']:
     for call in group:
      ix=call['instruction'];calls.append((keys[ix['programIdIndex']],wire.wire_vec(ix['data']),[keys[i] for i in wire.wire_vec(ix['accounts'])],call['stackHeight']))
    if route!='combined':assert not calls
    elif kind in ['wrong_relayer','suffix','destination_prefunded']:
     dist=e['canonical_pdas']['distribution'];dest=e['canonical_pdas']['output_distribution_token_account'];signer=e['instruction_accounts'][8]['pubkey'];rent=(165+128)*3480*2
     system=[(wire.SYSTEM,(2).to_bytes(4,'little')+(rent-1).to_bytes(8,'little'),[signer,dest],3),(wire.SYSTEM,(8).to_bytes(4,'little')+(165).to_bytes(8,'little'),[dest],3),(wire.SYSTEM,(1).to_bytes(4,'little')+wire.un58(TOKEN),[dest],3)] if kind=='destination_prefunded' else [(wire.SYSTEM,bytes(4)+rent.to_bytes(8,'little')+(165).to_bytes(8,'little')+wire.un58(TOKEN),[signer,dest],3)]
     assert calls==[(ATA,b'\0',[signer,dest,dist,USDC,wire.SYSTEM,TOKEN],2),(TOKEN,b'\x15\7\0',[USDC],3)]+system+[(TOKEN,b'\x16',[dest],3),(TOKEN,b'\x12'+wire.un58(dist),[dest,USDC],3)]
   counts['receipt_cases']+=1;verified+=1
 assert verified==200 and len(seen)==200 and negative=={('after','wrong_system'),('after','wrong_ata'),('non_swap','wrong_system'),('non_swap','wrong_ata'),('combined','wrong_system'),('combined','wrong_ata'),('combined','debouncer_mint_field'),('combined','missing_4')}
 return dict(verified_records=verified,unique_new_input_fixtures=len(seen),negative_controls=[list(x) for x in sorted(negative)],privileged_success_executed=False)
