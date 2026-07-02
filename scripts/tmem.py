"""Shared paths + translation-memory (translate.csv) helpers.
Every entry is one CSV row: columns  ns, key, en, hu.
Line breaks are stored as the literal text  \r \n \t  so one entry stays on one
physical line (Excel-safe). UTF-8 BOM so accented letters show correctly."""
import os, csv, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
def P(*a): return os.path.join(ROOT, *a)

CSV_PATH    = P("translate.csv")
LOCRES_PATH = P("Game.locres")
TODO_PATH   = P("to_translate.csv")
CONFIG_PATH = P("config.txt")
PAK_OUT     = P("VEIN_HUN.pak")
BS = chr(92)  # backslash

def w(s): sys.stdout.buffer.write(s.encode("utf-8"))

# ---- escape / unescape line breaks so a field never spans two CSV lines ----
def esc(s):
    return s.replace(BS, BS+BS).replace(chr(13), BS+"r").replace(chr(10), BS+"n").replace(chr(9), BS+"t")
def unesc(s):
    out=[]; i=0; n=len(s)
    while i < n:
        c=s[i]
        if c==BS and i+1<n:
            nx=s[i+1]; out.append({"r":chr(13),"n":chr(10),"t":chr(9),BS:BS}.get(nx,nx)); i+=2
        else:
            out.append(c); i+=1
    return "".join(out)

# ---- load / save ----
def load_rows():
    """Return list of (ns, key, en, hu), unescaped, in file order."""
    rows=[]
    if not os.path.exists(CSV_PATH): return rows
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rd=csv.reader(f); next(rd, None)
        for r in rd:
            if len(r) < 4: continue
            rows.append((unesc(r[0]), unesc(r[1]), unesc(r[2]), unesc(r[3])))
    return rows

def save_rows(rows):
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        wr=csv.writer(f); wr.writerow(["ns","key","en","hu"])
        for ns,key,en,hu in rows: wr.writerow([esc(ns),esc(key),esc(en),esc(hu)])

def save_todo(flagged):
    with open(TODO_PATH, "w", encoding="utf-8-sig", newline="") as f:
        wr=csv.writer(f); wr.writerow(["ns","key","en","hu","status"])
        for ns,key,en,hu,st in flagged: wr.writerow([esc(ns),esc(key),esc(en),esc(hu),st])

def hu_by_map():
    """(ns,key) -> hu, for the pak builder."""
    return {(ns,key): hu for ns,key,en,hu in load_rows()}
