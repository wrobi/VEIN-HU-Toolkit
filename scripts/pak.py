"""UE .pak: extract Game.locres from the game's pak (read, v11 index) and
build our small mod .pak (write, v3, uncompressed, unencrypted).
Standard library only."""
import struct, os, hashlib
from locres import LOCRES_MAGIC

PAK_MAGIC   = 0x5A6F12E1
PAK_VERSION = 3
MOUNT_POINT = "../../../Vein/Content/Localization/Game/en/"
INNER_NAME  = "Game.locres"

# ---------- read side: pull Game.locres out of the game's pak ----------
def _fstr(b,p):
    n=struct.unpack_from('<i',b,p)[0]; p+=4
    if n==0: return "",p
    if n<0:
        cnt=-n; raw=b[p:p+cnt*2]; p+=cnt*2; s=raw.decode('utf-16-le')
    else:
        raw=b[p:p+n]; p+=n; s=raw.decode('utf-8','replace')
    return (s[:-1] if s.endswith('\x00') else s), p

def _decode_entry(blob, pos):
    """Decode one bit-packed FPakEntry from the encoded-entries blob."""
    v=struct.unpack_from('<I',blob,pos)[0]; pos+=4
    if v & (1<<31): off=struct.unpack_from('<I',blob,pos)[0]; pos+=4
    else:           off=struct.unpack_from('<q',blob,pos)[0]; pos+=8
    if v & (1<<30): usize=struct.unpack_from('<I',blob,pos)[0]; pos+=4
    else:           usize=struct.unpack_from('<q',blob,pos)[0]; pos+=8
    cmi=(v>>23)&0x3f
    if cmi!=0:
        if v & (1<<29): size=struct.unpack_from('<I',blob,pos)[0]; pos+=4
        else:           size=struct.unpack_from('<q',blob,pos)[0]; pos+=8
    else:
        size=usize
    enc=(v>>22)&1
    return dict(offset=off, size=size, usize=usize, cmi=cmi, enc=enc)

def extract_locres(pak_path):
    """Return the bytes of Content/Localization/Game/en/Game.locres from the pak.
    Works with the shipped VEIN pak (v11, unencrypted index, uncompressed files)."""
    sz=os.path.getsize(pak_path)
    with open(pak_path,'rb') as f:
        f.seek(max(0, sz-300)); tail=f.read(300)
        i=tail.rfind(struct.pack('<I',PAK_MAGIC))
        if i<0: raise RuntimeError("pak footer magic not found (unexpected pak format)")
        ma=sz-len(tail)+i
        f.seek(ma-17); enc_guid=f.read(16); enc_index=f.read(1)[0]
        f.seek(ma+8); idx_off=struct.unpack('<q',f.read(8))[0]; idx_size=struct.unpack('<q',f.read(8))[0]
        if enc_index or enc_guid!=b'\0'*16:
            raise RuntimeError("pak index is encrypted; this simple extractor cannot read it.")
        # ---- primary index ----
        f.seek(idx_off); idx=f.read(idx_size); p=0
        _mount,p=_fstr(idx,p)
        p+=4                              # NumEntries
        p+=8                              # PathHashSeed
        if struct.unpack_from('<i',idx,p)[0]: p+=4+16+20   # has PathHashIndex (+off,+size,+hash)
        else: p+=4
        has_fd=struct.unpack_from('<i',idx,p)[0]; p+=4
        if not has_fd: raise RuntimeError("pak has no full directory index; cannot locate file.")
        fd_off,fd_size=struct.unpack_from('<qq',idx,p); p+=16; p+=20
        enc_size=struct.unpack_from('<i',idx,p)[0]; p+=4
        encoded=idx[p:p+enc_size]
        # ---- full directory index: find our file ----
        f.seek(fd_off); fd=f.read(fd_size); q=0
        ndir=struct.unpack_from('<i',fd,q)[0]; q+=4
        eoff=None
        for _ in range(ndir):
            d,q=_fstr(fd,q)
            nf=struct.unpack_from('<i',fd,q)[0]; q+=4
            for _ in range(nf):
                fn,q=_fstr(fd,q)
                e=struct.unpack_from('<i',fd,q)[0]; q+=4
                if fn=="Game.locres" and d.replace("\\","/").rstrip("/").endswith("Localization/Game/en"):
                    eoff=e
        if eoff is None:
            raise RuntimeError("Game.locres (en) not found in this pak.")
        ent=_decode_entry(encoded, eoff)
        if ent['enc']:  raise RuntimeError("target file is encrypted; cannot extract.")
        if ent['cmi']!=0:
            raise RuntimeError("target file is compressed; this extractor handles uncompressed only. "
                               "Unpack Game.locres manually (FModel/repak) and drop it in the folder.")
        # ---- read payload: skip the 53-byte inline FPakEntry header ----
        base=ent['offset']
        f.seek(base); head=f.read(128)
        for hlen in (53, 0):              # 53 = uncompressed/unencrypted inline header; 0 as fallback
            if head[hlen:hlen+16]==LOCRES_MAGIC:
                f.seek(base+hlen); return f.read(ent['usize'])
        m=head.find(LOCRES_MAGIC)          # last-resort scan
        if 0<=m<128:
            f.seek(base+m); return f.read(ent['usize'])
        raise RuntimeError("extracted data is not a locres (magic mismatch); pak layout changed.")

# ---------- write side: our mod pak (v3) ----------
def _wpstr(s):
    b=s.encode('ascii'); return struct.pack('<i',len(b)+1)+b+b'\x00'
def _pak_entry(offset,size,sha1):
    return (struct.pack('<q',offset)+struct.pack('<q',size)+struct.pack('<q',size)
            +struct.pack('<i',0)+sha1+struct.pack('<B',0)+struct.pack('<I',0))
def build_pak(data, outpath):
    sha1=hashlib.sha1(data).digest()
    body=_pak_entry(0,len(data),sha1)+data
    index_offset=len(body)
    index=_wpstr(MOUNT_POINT)+struct.pack('<I',1)+_wpstr(INNER_NAME)+_pak_entry(0,len(data),sha1)
    footer=(struct.pack('<I',PAK_MAGIC)+struct.pack('<I',PAK_VERSION)
            +struct.pack('<q',index_offset)+struct.pack('<q',len(index))+hashlib.sha1(index).digest())
    open(outpath,'wb').write(body+index+footer)
