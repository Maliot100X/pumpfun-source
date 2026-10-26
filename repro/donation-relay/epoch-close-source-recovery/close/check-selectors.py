from pathlib import Path
import hashlib,importlib.util,json,struct
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('relay_selector_elf',P/'analyze.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
H=lambda b:hashlib.sha256(b).hexdigest()

def select(elf,lo,size,code,kind):
 regs=[0]*11;regs[2 if kind=='name' else 1]=code;pc=lo+8;trace=[]
 for _ in range(256):
  assert lo<=pc<lo+size
  trace.append(pc);op,rs,off,imm=struct.unpack('<BBhi',elf.at(pc,8));d=rs&15;src=rs>>4
  if op==0x18:
   b=elf.at(pc,16);regs[d]=struct.unpack_from('<I',b,4)[0]+(struct.unpack_from('<I',b,12)[0]<<32);pc+=16
  elif op==0xb7:regs[d]=imm;pc+=8
  elif op==0xbf:regs[d]=regs[src];pc+=8
  elif op==0x05:pc+=8+8*off
  elif op in (0x15,0x55,0x65,0x75,0x25,0x35,0xa5,0xb5):
   x=regs[d];take={0x15:x==imm,0x55:x!=imm,0x65:x>imm,0x75:x>=imm,0x25:x>imm,0x35:x>=imm,0xa5:x<imm,0xb5:x<=imm}[op];pc+=8+(8*off if take else 0)
  elif op==0x85 and kind=='name':return dict(pointer=regs[2],length=regs[3],trace=trace)
  elif op==0x7b and kind=='message':
   pointer,length=struct.unpack('<QQ',elf.at(regs[1],16));assert pointer & 0xffffffff == 0 and elf.relocations[regs[1]]['type']==8;pointer >>= 32;return dict(descriptor=regs[1],pointer=pointer,length=length,trace=trace)
  else:raise AssertionError((pc,hex(op)))
 raise AssertionError('selector did not reach terminal')

def derive(namespace="owned"):
 original=m.Elf((P/'original.so').read_bytes());candidate=m.Elf((P/'unstripped.so').read_bytes());rows=json.loads((P/'framework-codes.json').read_text());functions=json.loads((P/'candidate-function-ledger.json').read_text());windows=json.loads((P/'original-windows.json').read_text());out=[]
 name_index=next(i for i,r in enumerate(functions) if any((('framework_codes9ErrorCode4name' if namespace=='owned' else 'anchor_lang5error9ErrorCode4name') in n) for n in r['names']))
 message_index=next(i for i,r in enumerate(functions) if any((('framework_codes..ErrorCode' if namespace=='owned' else 'anchor_lang..error..ErrorCode') in n) and 'core..fmt..Display' in n and '$GT$3fmt' in n for n in r['names']))
 for r in rows:
  item=dict(code=r['code'],name=r['name'],message=r['message'],selections={})
  for kind,oi,ci in [('name',296,name_index),('message',298,message_index)]:
   a=windows[oi];b=functions[ci];selections={}
   for label,e,w in [('original',original,a),('candidate',candidate,b)]:
    v=select(e,w['start'],w['bytes'],r['code'],kind);data=e.at(v['pointer'],v['length']);assert data.decode()==r[kind],(r['code'],label,kind,v,data)
    v['selected_bytes_sha256']=H(data);selections[label]=v
   assert [x-a['start'] for x in selections['original']['trace']]==[x-b['start'] for x in selections['candidate']['trace']]
   item['selections'][kind]=selections
  out.append(item)
 return out
if __name__=='__main__':
 result={n:derive(n) for n in ['owned','anchor']};(P/'selector-proof-both77.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(variants_per_implementation={n:len(v) for n,v in result.items()},full_names_and_messages_checked=True,whole_program_identity=False)))
