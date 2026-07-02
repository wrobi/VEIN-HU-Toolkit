"""Search translate.csv by English or Hungarian text (case-insensitive).
Usage:  find.bat Bekapcsol      find.bat "Turn On"
Prints ns / key / EN / HU so you know which row to edit."""
import sys, tmem

def main():
    if len(sys.argv) < 2:
        tmem.w("usage: find.bat <text>\n"); return 1
    q=" ".join(sys.argv[1:]).lower(); n=0
    for ns,key,en,hu in tmem.load_rows():
        if q in en.lower() or q in hu.lower():
            tmem.w("[%s] %s\n    EN: %s\n    HU: %s\n"%(ns,key,en,hu)); n+=1
    tmem.w("\n%d match(es).\n"%n)
    return 0

if __name__=="__main__":
    sys.exit(main())
