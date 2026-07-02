"""UE localization 'locres' v2/v3 (Optimized_CityHash64) reader + writer.
Only the standard library is used."""
import struct

LOCRES_MAGIC = bytes([0x0E,0x14,0x74,0x75,0x67,0x4A,0x03,0xFC,0x4A,0x15,0x90,0x9D,0xC3,0x37,0x7F,0x1B])

class R:
    def __init__(s,d): s.d=d; s.p=0
    def seek(s,p): s.p=p
    def tell(s): return s.p
    def u8(s): v=s.d[s.p]; s.p+=1; return v
    def i32(s): v=struct.unpack_from('<i',s.d,s.p)[0]; s.p+=4; return v
    def u32(s): v=struct.unpack_from('<I',s.d,s.p)[0]; s.p+=4; return v
    def i64(s): v=struct.unpack_from('<q',s.d,s.p)[0]; s.p+=8; return v
    def fstr(s):
        n=s.i32()
        if n==0: return ""
        if n<0:
            cnt=-n; raw=s.d[s.p:s.p+cnt*2]; s.p+=cnt*2; r=raw.decode('utf-16-le')
        else:
            raw=s.d[s.p:s.p+n]; s.p+=n; r=raw.decode('utf-8','replace')
        return r[:-1] if r.endswith('\x00') else r

def parse_locres(path):
    """Returns (version, entries_count, namespaces, localized).
    namespaces: list of [ns_hash, ns_name, keys]; keys: list of [key_hash, key, src_hash, index]
    localized:  list of [string, refcount]  (the shared string table indexed by 'index')"""
    d=open(path,'rb').read(); r=R(d)
    assert d[:16]==LOCRES_MAGIC, "not a supported .locres file (bad magic)"
    r.seek(16); version=r.u8(); assert version>=2, "only locres v2/v3 supported"
    off=r.i64(); cur=r.tell(); r.seek(off)
    num=r.i32(); localized=[]
    for _ in range(num):
        st=r.fstr(); rc=r.i32(); localized.append([st,rc])
    r.seek(cur)
    entries_count=r.u32(); ns_count=r.u32(); namespaces=[]
    for _ in range(ns_count):
        nh=r.u32(); nm=r.fstr(); kc=r.u32(); keys=[]
        for _ in range(kc):
            kh=r.u32(); k=r.fstr(); sh=r.u32(); ix=r.i32(); keys.append([kh,k,sh,ix])
        namespaces.append([nh,nm,keys])
    return version,entries_count,namespaces,localized

def wfstr(s):
    if s=="": return struct.pack('<i',0)
    try:
        b=s.encode('ascii'); return struct.pack('<i',len(b)+1)+b+b'\x00'
    except UnicodeEncodeError:
        b=s.encode('utf-16-le'); units=len(b)//2+1
        return struct.pack('<i',-units)+b+b'\x00\x00'

def build_locres(version, entries_count, namespaces, lut_order, lut_counts):
    out=bytearray(); out+=LOCRES_MAGIC; out+=bytes([version])
    off_pos=len(out); out+=struct.pack('<q',0)
    out+=struct.pack('<I',entries_count); out+=struct.pack('<I',len(namespaces))
    for nh,nm,keys in namespaces:
        out+=struct.pack('<I',nh); out+=wfstr(nm); out+=struct.pack('<I',len(keys))
        for kh,k,sh,ix in keys:
            out+=struct.pack('<I',kh); out+=wfstr(k); out+=struct.pack('<I',sh); out+=struct.pack('<i',ix)
    off=len(out); out+=struct.pack('<i',len(lut_order))
    for st,rc in zip(lut_order,lut_counts):
        out+=wfstr(st); out+=struct.pack('<i',rc)
    out[off_pos:off_pos+8]=struct.pack('<q',off)
    return bytes(out)
