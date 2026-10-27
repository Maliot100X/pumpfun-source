#!/usr/bin/env python3
"""Disassemble a function section of a relocatable object (compact; masks nothing). usage: objdis.py OBJ NAME_SUBSTR"""
import sys, struct
sys.path.insert(0, __import__('os').path.dirname(__file__))
import objfn
JMP = {0x00:'ja',0x10:'jeq',0x20:'jgt',0x30:'jge',0x40:'jset',0x50:'jne',0x60:'jsgt',0x70:'jsge',0x80:'call',0x90:'exit',0xa0:'jlt',0xb0:'jle',0xc0:'jslt',0xd0:'jsle'}
b = open(sys.argv[1], 'rb').read(); h = objfn.find(b, sys.argv[2])[0][0]; code = b[h['off']:h['off'] + h['size']]
p = 0
while p < len(code):
    op = code[p]; regs = code[p + 1]; off = struct.unpack_from('<h', code, p + 2)[0]; imm = struct.unpack_from('<i', code, p + 4)[0]
    w = 16 if op == 0x18 else 8
    cls = op & 7
    if cls in (5, 6) and (op & 0xf0) not in (0x80, 0x90):
        print(p, JMP.get(op & 0xf0, hex(op)), f'r{regs & 15}', (f'r{regs >> 4}' if op & 8 else imm), '->', p + 8 + off * 8)
    elif op == 0x85:
        print(p, 'call', imm)
    p += w
