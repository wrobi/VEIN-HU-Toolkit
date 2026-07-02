"""Locate the game's pakchunk0-Windows.pak.
Order: config.txt (a pak file OR the game folder) -> Steam auto-detect."""
import os, re
try:
    import winreg
except ImportError:
    winreg=None

# from a Steam library root down to the pak
REL_PAK = os.path.join("steamapps","common","Vein","Vein","Content","Paks","pakchunk0-Windows.pak")
# from the game root down to the pak
GAME_REL = os.path.join("Vein","Content","Paks","pakchunk0-Windows.pak")

def _steam_roots():
    roots=[]
    if winreg:
        for hive,key,val in [
            (winreg.HKEY_CURRENT_USER,  r"Software\Valve\Steam",           "SteamPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam","InstallPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam",            "InstallPath"),
        ]:
            try:
                with winreg.OpenKey(hive,key) as k:
                    p,_=winreg.QueryValueEx(k,val)
                    if p and p not in roots: roots.append(p)
            except OSError:
                pass
    # common fallbacks
    for p in (r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"):
        if p not in roots: roots.append(p)
    return roots

def _library_roots(steam_root):
    libs=[steam_root]
    vdf=os.path.join(steam_root,"steamapps","libraryfolders.vdf")
    try:
        txt=open(vdf,encoding="utf-8",errors="replace").read()
        for m in re.finditer(r'"path"\s*"([^"]+)"', txt):
            libs.append(m.group(1).replace("\\\\","\\"))
    except OSError:
        pass
    return libs

def _from_config(config_path):
    if not (config_path and os.path.isfile(config_path)): return None
    for ln in open(config_path, encoding="utf-8-sig"):
        ln=ln.strip().strip('"')
        if not ln or ln.startswith("#"): continue
        if os.path.isfile(ln): return ln                       # pak file given
        c=os.path.join(ln, GAME_REL)                            # game folder given
        if os.path.isfile(c): return c
    return None

def find_pak(config_path=None):
    p=_from_config(config_path)
    if p: return p
    for root in _steam_roots():
        for lib in _library_roots(root):
            c=os.path.join(lib, REL_PAK)
            if os.path.isfile(c): return c
    return None
