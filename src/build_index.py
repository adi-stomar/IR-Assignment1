# File Action: Builds an inverted index from preprocessed files, mapping each term to sorted docids.
# Running Example:
# Read ".I 1\n.S\ntermA termB" -> docid=1, words=[termA, termB]
# index[termA].add(1), index[termB].add(1)
# Output line: termA 1

import sys
from pathlib import Path
from collections import defaultdict

LOCAL = Path(__file__).resolve().parent
ROOT  = LOCAL.parent

def reads(path):
    docid = None
    with open(path, "r", encoding="utf-8", errors="replace") as file:
        lines = file.readlines()
        
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if line.startswith(".I"):
            docid = int(line.split()[1])
            i += 1
            if i < len(lines) and lines[i].rstrip("\n").startswith(".S"):
                i += 1
            wline = lines[i].rstrip("\n") if i < len(lines) else ""
            words = wline.split()
            
            yield docid, words
            i += 1
        else:
            i += 1

def build(path):
    index = defaultdict(set)
    maxid = 0
    for docid, words in reads(path):
        maxid = max(maxid, docid)
        for w in words:
            index[w].add(docid)
            
    sortd = {w: sorted(d) for w, d in index.items()}
    return sortd, maxid

def write(index, maxid, ofile):
    vocab = len(index)
    with open(ofile, "w", encoding="utf-8") as out:
        out.write(f"{vocab}, {maxid}\n")
        
        for term in sorted(index.keys()):
            posts = ",".join(str(d)   for d in index[term])
            out.write(f"{term} {posts}\n")

def main():
    ifile = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Normal_Group_processed.all"
    ofile = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "Normal_Group_cran.index"

    if not ifile.exists():
        sys.exit(1)

    index, maxid = build(ifile)
    write(index, maxid, ofile)
    print(f"Vocab: {len(index)}, max: {maxid}")

if __name__ == "__main__":
    main()
