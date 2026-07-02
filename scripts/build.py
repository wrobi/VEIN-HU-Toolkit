"""Step 2: translate.csv + Game.locres -> VEIN_HUN.pak
Builds the Hungarian locres (overwriting the game's 'en' slot) and wraps it in a
small v3 mod pak. Any (ns,key) missing from translate.csv keeps its English text."""
import os, sys
import tmem
from locres import parse_locres, build_locres
from pak import build_pak
w=tmem.w

def main():
    if not os.path.exists(tmem.LOCRES_PATH):
        w("ERROR: Game.locres is missing. Run getlocres.bat first.\n"); return 1
    if not os.path.exists(tmem.CSV_PATH):
        w("ERROR: translate.csv is missing. Run getlocres.bat first.\n"); return 1

    hu_by=tmem.hu_by_map()
    version,ec,namespaces,localized=parse_locres(tmem.LOCRES_PATH)

    lut_index={}; lut_order=[]; lut_counts=[]; missing=0
    for _nh,_nm,keys in namespaces:
        for kentry in keys:
            nm=_nm
            t=hu_by.get((nm,kentry[1]))
            if t is None:
                t=localized[kentry[3]][0] if 0<=kentry[3]<len(localized) else ""; missing+=1
            if t not in lut_index:
                lut_index[t]=len(lut_order); lut_order.append(t); lut_counts.append(0)
            kentry[3]=lut_index[t]; lut_counts[lut_index[t]]+=1

    loc=build_locres(version,ec,namespaces,lut_order,lut_counts)
    open(tmem.P("Game_hu.locres"),"wb").write(loc)
    build_pak(loc, tmem.PAK_OUT)

    total=sum(len(k[2]) for k in namespaces)
    w("OK. entries=%d, not-in-csv (kept English)=%d\n"%(total,missing))
    w("wrote VEIN_HUN.pak (%d bytes locres)\n"%len(loc))
    w("Copy VEIN_HUN.pak into: ...\\Vein\\Content\\Paks\\  (rename to VEIN_HUN_P.pak if it doesn't apply)\n")
    return 0

if __name__=="__main__":
    sys.exit(main())
