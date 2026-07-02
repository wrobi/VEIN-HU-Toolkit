"""Step 1: pull the current English Game.locres out of the game's pak, then
create/refresh translate.csv reusing every existing Hungarian translation.

Reuse logic (resilient to hex-key moves between versions):
  * same (ns,key) AND same English   -> kept as-is
  * (ns,key) moved but English known -> Hungarian reused by source text
  * (ns,key) exists, English changed -> old Hungarian kept, FLAGGED (REVIEW)
  * brand-new string                 -> left English, FLAGGED (NEW)
Existing rows keep their position; genuinely new rows are appended at the end.
Flagged rows (REVIEW/NEW) are also written to to_translate.csv."""
import sys, collections
import tmem, steam
from pak import extract_locres
from locres import parse_locres
w=tmem.w

def main():
    pak=steam.find_pak(tmem.CONFIG_PATH)
    if not pak:
        w("ERROR: could not find pakchunk0-Windows.pak.\n")
        w("  Fix: open config.txt and put the path to the pak file, or to the VEIN game folder.\n")
        return 1
    w("using pak: %s\n"%pak)
    try:
        data=extract_locres(pak)
    except Exception as e:
        w("ERROR extracting Game.locres: %s\n"%e); return 1
    open(tmem.LOCRES_PATH,"wb").write(data)
    w("extracted Game.locres (%d bytes)\n"%len(data))

    _v,_ec,namespaces,localized=parse_locres(tmem.LOCRES_PATH)
    loc_order=[]; loc_en={}
    for _nh,nm,keys in namespaces:
        for _kh,k,_sh,ix in keys:
            en=localized[ix][0] if 0<=ix<len(localized) else ""
            loc_order.append((nm,k)); loc_en[(nm,k)]=en

    old=tmem.load_rows(); fresh=(len(old)==0)
    by_en=collections.defaultdict(collections.Counter)
    for ns,key,en,hu in old:
        if hu!=en: by_en[en][hu]+=1
    best_en={en:c.most_common(1)[0][0] for en,c in by_en.items()}

    out=[]; flagged=[]; seen=set()
    n_exact=n_src=n_review=n_new=0

    # keep existing rows in place
    for ns,key,en_old,hu_old in old:
        if (ns,key) not in loc_en: continue          # gone from the game -> drop
        en=loc_en[(ns,key)]; seen.add((ns,key))
        if en_old==en:
            hu=hu_old; n_exact+=1
        elif en in best_en:
            hu=best_en[en]; n_src+=1
        else:
            hu=hu_old; n_review+=1; flagged.append((ns,key,en,hu,"REVIEW-source-changed"))
        out.append((ns,key,en,hu))
    removed=0 if fresh else (len(old)-len(seen))

    # append new strings (in locres order)
    for (ns,key) in loc_order:
        if (ns,key) in seen: continue
        en=loc_en[(ns,key)]; seen.add((ns,key))
        if en in best_en:
            hu=best_en[en]; n_src+=1
        else:
            hu=en; n_new+=1; flagged.append((ns,key,en,hu,"NEW-untranslated"))
        out.append((ns,key,en,hu))

    tmem.save_rows(out); tmem.save_todo(flagged)

    if fresh:
        w("created translate.csv with %d entries (all untranslated).\n"%len(out))
    else:
        w("translate.csv refreshed: %d entries.\n"%len(out))
        w("  reused exact:            %d\n"%n_exact)
        w("  reused by source text:   %d\n"%n_src)
        w("  REVIEW (source changed): %d\n"%n_review)
        w("  NEW (untranslated):      %d\n"%n_new)
        w("  removed (gone from game):%d\n"%removed)
    w("  -> %d row(s) need work; see to_translate.csv\n"%len(flagged))
    if flagged:
        w("     Translate the 'hu' column of those rows in translate.csv, then run build.bat.\n")
    return 0

if __name__=="__main__":
    sys.exit(main())
