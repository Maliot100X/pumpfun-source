#!/usr/bin/env python3
"""Read-only ELF analysis; normalization is in-memory, never a byte patch."""
import gzip, hashlib, json, struct
from pathlib import Path
H=lambda b:hashlib.sha256(b).hexdigest()
def encode(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
class Elf:
 def __init__(self,b):
  self.b=b; h=struct.unpack_from('<16sHHIQQQIHHHHHH',b);assert h[0][:6]==b'\x7fELF\x02\x01'
  self.sections=[]
  for i in range(h[12]):
   n,t,f,a,o,z,l,info,al,en=struct.unpack_from('<IIQQQQIIQQ',b,h[6]+i*h[11]);self.sections.append(dict(index=i,name_offset=n,type=t,flags=f,address=a,offset=o,size=z,link=l,info=info,alignment=al,entry_size=en))
  names=self.section_bytes(self.sections[h[13]])
  for s in self.sections:s['name']=self.string(names,s.pop('name_offset'))
  self.by_name={s['name']:s for s in self.sections};self.relocations={};self.symbols=[]
  for s in self.sections:
   if s['type'] in (2,11):
    strings=self.section_bytes(self.sections[s['link']]);ss=[]
    for off in range(s['offset'],s['offset']+s['size'],24):
     n,info,other,section,value,size=struct.unpack_from('<IBBHQQ',b,off)
     ss.append(dict(name=self.string(strings,n),type=info&15,binding=info>>4,section=section,start=value,size=size))
    if s['type']==2:self.symbols=ss
    s['_symbols']=ss
  for s in self.sections:
   if s['type']==9:
    syms=self.sections[s['link']]['_symbols']
    for off in range(s['offset'],s['offset']+s['size'],16):
     a,info=struct.unpack_from('<QQ',b,off);self.relocations[a]=dict(type=info&0xffffffff,symbol=syms[info>>32]['name'],record_offset=off)
  for s in self.sections:s.pop('_symbols',None)
 @staticmethod
 def string(b,i):return b[i:b.find(b'\0',i)].decode('utf8','replace')
 def section_bytes(self,s):return self.b[s['offset']:s['offset']+s['size']]
 def at(self,a,n):
  for s in self.sections:
   if s['type']!=8 and s['flags']&2 and s['address']<=a and a+n<=s['address']+s['size']:
    o=s['offset']+a-s['address'];return self.b[o:o+n]
  raise ValueError((a,n))
 def containing(self,a):
  return next((s for s in self.sections if s['flags']&2 and s['address']<=a<s['address']+s['size']),None)
 def function(self,start,size,names):
  b=self.at(start,size);assert len(b)%8==0;n=bytearray(b);calls=[];refs=[];indirect=[];external=[];stack=[];i=0
  while i<size:
   op,regs,off,imm=struct.unpack_from('<BBhi',b,i);pc=start+i
   if op==0x85:
    rel=self.relocations.get(pc)
    if rel and rel['type']==10:
     external.append(dict(offset=i,pc=pc,immediate=imm,relocation=rel))
    elif regs>>4==1:
     calls.append(dict(offset=i,pc=pc,displacement=imm,target=pc+8+8*imm));n[i+4:i+8]=b'\0'*4
    else:external.append(dict(offset=i,pc=pc,immediate=imm,relocation=rel))
   elif op==0x8d:indirect.append(dict(offset=i,pc=pc,register=imm))
   if op==0x18:
    assert i+16<=size
    rel=self.relocations.get(pc)
    if rel:
     lo=struct.unpack_from('<I',b,i+4)[0];hi=struct.unpack_from('<I',b,i+12)[0];a=lo+(hi<<32);s=self.containing(a)
     ref=dict(offset=i,pc=pc,target=a,relocation=rel,section=None if s is None else s['name'])
     if s:
      count=min(64,s['address']+s['size']-a);literal=self.at(a,count);ref.update(bounded_bytes=count,bounded_hex=literal.hex(),bounded_sha256=H(literal))
     refs.append(ref);n[i+4:i+8]=b'\0'*4;n[i+12:i+16]=b'\0'*4
    i+=16;continue
   # Direct r10 base accesses only; derived frame-pointer aliases are not inferred.
   if (op&7)==1 and regs>>4==10 or (op&7) in (2,3) and (regs&15)==10:
    stack.append(dict(pc=pc,offset=off,opcode=op))
   i+=8
  return dict(start=start,end=start+size,bytes=size,names=names,raw_sha256=H(b),normalized_sha256=H(n),direct_calls=calls,data_references=refs,external_calls=external,indirect_calls=indirect,direct_r10_accesses=stack)
def residual(a,b):
 r=[];i=0;n=min(len(a),len(b))
 while i<n:
  if a[i]==b[i]:i+=1;continue
  start=i
  while i<n and a[i]!=b[i]:i+=1
  r.append(dict(offset=start,original=a[start:i].hex(),candidate=b[start:i].hex()))
 if len(a)!=len(b):r.append(dict(offset=n,original=a[n:].hex(),candidate=b[n:].hex()))
 return r

def analyze(p):
 ob=(p/'original.so').read_bytes();cb=(p/'candidate.so').read_bytes();ub=(p/'unstripped.so').read_bytes();o,c,u=Elf(ob),Elf(cb),Elf(ub)
 windows=json.loads((p/'original-windows.json').read_text());of=[]
 for w in windows:
  f=o.function(w['start'],w['bytes'],[]);assert f['raw_sha256']==w['sha256'];f['ordinal']=w['ordinal'];of.append(f)
 syms={}
 for s in u.symbols:
  if s['type']==2 and s['size']:
   key=(s['start'],s['size']);syms.setdefault(key,[]).append(s['name'])
 cf=[u.function(a,z,sorted(names)) for (a,z),names in sorted(syms.items())]
 coverage={}
 for label,elf,fs in [('original',o,of),('candidate',u,cf)]:
  text=elf.by_name['.text'];end=text['address'];gaps=[]
  for f in fs:
   if f['start']!=end:gaps.append([end,f['start']])
   end=f['end']
  if end!=text['address']+text['size']:gaps.append([end,text['address']+text['size']])
  assert not gaps
  coverage[label]=dict(text_start=text['address'],text_end=end,bytes=text['size'],distinct_windows=len(fs),gaps=gaps)
 coverage['candidate']['STT_FUNC_symbol_count']=sum(s['type']==2 for s in u.symbols)
 coverage['candidate']['symbols']=[s for s in u.symbols if s['type']==2]
 for i,f in enumerate(cf):f['index']=i
 raw={};norm={}
 for f in cf:raw.setdefault((f['bytes'],f['raw_sha256']),[]).append(f['index']);norm.setdefault((f['bytes'],f['normalized_sha256']),[]).append(f['index'])
 pairs=set();ledger=[];omap={f['start']:f['ordinal'] for f in of};cmap={f['start']:f['index'] for f in cf}
 for f in of:
  rk=raw.get((f['bytes'],f['raw_sha256']),[]);nk=norm.get((f['bytes'],f['normalized_sha256']),[])
  ledger.append(dict(ordinal=f['ordinal'],start=f['start'],end=f['end'],bytes=f['bytes'],raw_candidate_indices=rk,normalized_candidate_indices=nk,status='raw-body' if rk else 'normalized-shape-only' if nk else 'no-complete-body-match'))
  pairs.update((f['ordinal'],j) for j in nk)
 # Greatest fixed point of matched call graph: deliberately NOT semantic/data closure.
 closed=set(pairs)
 while True:
  nxt=set()
  for i,j in closed:
   a,b=of[i],cf[j]
   if len(a['direct_calls'])!=len(b['direct_calls']):continue
   if all((omap.get(x['target']),cmap.get(y['target'])) in closed for x,y in zip(a['direct_calls'],b['direct_calls'])):nxt.add((i,j))
  if nxt==closed:break
  closed=nxt
 witnesses=[]
 for i,j in sorted(pairs):
  a,b=of[i],cf[j];calls=[];refs=[]
  for x,y in zip(a['direct_calls'],b['direct_calls']):
   pair=(omap.get(x['target']),cmap.get(y['target']));calls.append(dict(original=x,candidate=y,target_pair=list(pair),normalized_body_pair=pair in pairs,recursive_call_shape_closed=pair in closed))
  for x,y in zip(a['data_references'],b['data_references']):
   refs.append(dict(original=x,candidate=y,equal_bounded_bytes=x.get('bounded_hex')==y.get('bounded_hex') and 'bounded_hex' in x,complete_object_extent_proven=False))
  witnesses.append(dict(original_ordinal=i,candidate_index=j,raw_body=a['raw_sha256']==b['raw_sha256'],recursive_call_shape_closed=(i,j) in closed,direct_calls=calls,data_references=refs,indirect_calls=a['indirect_calls'],interpretation='complete instruction shape only; data extents, runtime ABI and indirect calls are not established'))
 sections=[]
 for name in sorted(set(o.by_name)|set(c.by_name)):
  if not name:continue
  a=o.by_name.get(name);b=c.by_name.get(name);aa=o.section_bytes(a) if a and a['type']!=8 else b'';bb=c.section_bytes(b) if b and b['type']!=8 else b''
  sections.append(dict(name=name,original_bytes=len(aa),candidate_bytes=len(bb),original_sha256=H(aa),candidate_sha256=H(bb),common_position_differences=sum(x!=y for x,y in zip(aa,bb)),length_delta=len(bb)-len(aa),same_bytes=aa==bb))
 alloc=[]
 for s in u.sections:
  if s['flags']&2 and s['type']!=8:
   cs=c.by_name[s['name']];assert s['address']==cs['address'];assert u.section_bytes(s)==c.section_bytes(cs);alloc.append(dict(name=s['name'],bytes=s['size'],sha256=H(u.section_bytes(s))))
 residuals=residual(ob,cb)
 summary=dict(original_sha256=H(ob),candidate_sha256=H(cb),unstripped_sha256=H(ub),original_bytes=len(ob),candidate_bytes=len(cb),unstripped_bytes=len(ub),original_inferred_windows=len(of),candidate_symbol_windows=len(cf),original_raw_match_windows=sum(bool(r['raw_candidate_indices']) for r in ledger),original_normalized_match_windows=sum(bool(r['normalized_candidate_indices']) for r in ledger),unmatched_original_windows=sum(not r['normalized_candidate_indices'] for r in ledger),matched_pairs=len(pairs),recursive_call_shape_closed_pairs=len(closed),whole_file_equal=ob==cb,common_position_different_bytes=sum(x!=y for x,y in zip(ob,cb)),original_only_tail=max(0,len(ob)-len(cb)),candidate_only_tail=max(0,len(cb)-len(ob)),positional_residual_ranges=len(residuals),runtime_cases=0,execution_suitable=False)
 return {'coverage.json':coverage,'original-function-ledger.json':of,'candidate-function-ledger.json':cf,'match-ledger.json':ledger,'match-witnesses.json':witnesses,'section-comparison.json':sections,'allocated-strip-identity.json':alloc,'comparison-summary.json':summary,'whole-file-residuals.json.gz':residuals}
def write(p):
 for name,value in analyze(p).items():
  data=encode(value)
  if name.endswith('.gz'):data=gzip.compress(data,mtime=0)
  (p/name).write_bytes(data)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('package',nargs='?',type=Path,default=Path(__file__).resolve().parent);a=ap.parse_args();write(a.package);print((a.package/'comparison-summary.json').read_text())
