from pathlib import Path
import importlib.util,json,struct,hashlib
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('program_data_elf',P/'analyze.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
H=lambda b:hashlib.sha256(b).hexdigest();MASK=(1<<64)-1

def name_value(e,start,size,variant):
    # Bounded, call-free decoding of a single selector's normal allocation path.
    # Synthetic memory exists only in this read-only analysis; it is not a VM or
    # build input and is not evidence about allocation failure or other callers.
    regs=[0]*11;regs[1]=0x1000;regs[2]=variant;regs[3]=0x300006000;mem={}
    def store(addr,value,n):
        for i,b in enumerate((value & ((1<<(n*8))-1)).to_bytes(n,'little')):mem[addr+i]=b
    def load(addr,n):
        assert all(addr+i in mem for i in range(n)),(addr,n)
        return int.from_bytes(bytes(mem[addr+i] for i in range(n)),'little')
    store(0x300000000,regs[3],8);pc=start+32;trace=[]
    for _ in range(512):
        assert start<=pc<start+size;trace.append(pc)
        op,rs,off,imm=struct.unpack('<BBhi',e.at(pc,8));d=rs&15;src=rs>>4
        if op==0x18:
            b=e.at(pc,16);regs[d]=struct.unpack_from('<I',b,4)[0]+(struct.unpack_from('<I',b,12)[0]<<32);pc+=16
        elif op==0xbf:regs[d]=regs[src];pc+=8
        elif op==0xb7:regs[d]=imm & MASK;pc+=8
        elif op in (0x07,0x17,0x57):
            regs[d]=({0x07:lambda x:x+imm,0x17:lambda x:x-imm,0x57:lambda x:x&(imm&MASK)}[op](regs[d]))&MASK;pc+=8
        elif op==0x05:pc+=8+off*8
        elif op&7==5 and op!=0x95 and op!=0x85 and op!=0x8d:
            right=regs[src] if op&8 else imm&MASK;x=regs[d];kind=op&0xf0
            sx=x if x<(1<<63) else x-(1<<64);sy=right if right<(1<<63) else right-(1<<64)
            take={0x10:x==right,0x20:x>right,0x30:x>=right,0x50:x!=right,0x60:sx>sy,0x70:sx>=sy,0xa0:x<right,0xb0:x<=right}[kind]
            pc+=8+(off*8 if take else 0)
        elif op&7 in (2,3):
            n={0:4,8:2,16:1,24:8}[op&24];store((regs[d]+off)&MASK,regs[src] if op&7==3 else imm,n);pc+=8
        elif op&7==1:
            n={0:4,8:2,16:1,24:8}[op&24];regs[d]=load((regs[src]+off)&MASK,n);pc+=8
        elif op==0x95:
            cap=load(0x1000,8);ptr=load(0x1008,8);length=load(0x1010,8);assert cap==length
            data=bytes(mem[ptr+i] for i in range(length));return dict(bytes=data.decode(),length=length,trace=trace)
        else:raise AssertionError(('unexpected instruction or external call on bounded name path',pc,hex(op)))
    raise AssertionError('name selector failed to return')

def message_value(e,start,size,variant):
    regs=[0]*11;regs[2]=variant;pc=start+40;trace=[]
    for _ in range(256):
        assert start<=pc<start+size;trace.append(pc);op,rs,off,imm=struct.unpack('<BBhi',e.at(pc,8));d=rs&15
        if op==0x18:
            b=e.at(pc,16);regs[d]=struct.unpack_from('<I',b,4)[0]+(struct.unpack_from('<I',b,12)[0]<<32);pc+=16
        elif op==0xb7:regs[d]=imm;pc+=8
        elif op==0x05:pc+=8+off*8
        elif op in (0x15,0x65):pc+=8+(off*8 if (regs[d]==imm if op==0x15 else regs[d]>imm) else 0)
        elif op==0x8d:
            raw=e.at(regs[2],regs[3]);return dict(pointer=regs[2],length=regs[3],bytes=raw.decode(),sha256=H(raw),trace=trace)
        else:raise AssertionError((pc,hex(op)))
    raise AssertionError('message selector did not reach formatter')

def derive():
    o=a.Elf((P/'original.so').read_bytes());c=a.Elf((P/'unstripped.so').read_bytes());ws=json.loads((P/'original-windows.json').read_text());fs=json.loads((P/'candidate-function-ledger.json').read_text());rows=json.loads((P/'business-codes.json').read_text())
    ni=next(i for i,f in enumerate(fs) if any('business_error_codes9ErrorCode4name' in n for n in f['names']));mi=next(i for i,f in enumerate(fs) if any('business_error_codes..ErrorCode' in n and 'core..fmt..Display' in n for n in f['names']));out=[]
    for row in rows:
        item=dict(code=row['code'],variant=row['variant'],name=row['name'],message=row['message'],decoded={})
        for kind,oi,ci,fn in [('name',114,ni,name_value),('message',116,mi,message_value)]:
            pair={}
            for label,e,f in [('original',o,ws[oi]),('candidate',c,fs[ci])]:
                result=fn(e,f['start'],f['bytes'],row['variant']);assert result['bytes']==row[kind];pair[label]=result
            item['decoded'][kind]=pair
        out.append(item)
    return out
if __name__=='__main__':
    rows=derive();(P/'program-data-proof-all34.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(dict(variants=len(rows),complete_normal_resource_names=True,full_message_extents=True,allocation_failure_equivalence=False,whole_program_identity=False)))
