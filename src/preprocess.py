# File Action: Preprocesses the Cranfield collection by tokenizing, lowercasing, removing stopwords, and stemming.
# Running Example:
# Input text: "The aerodynamic properties of wings"
# 1. words: ["The", "aerodynamic", "properties", "of", "wings"]
# 2. lower: ["the", "aerodynamic", "properties", "of", "wings"]
# 3. stops: ["aerodynamic", "properties", "wings"]
# 4. stems: ["aerodynam", "properti", "wing"]
# Output saved with .I docid and .S for words.

import re
import sys
from pathlib import Path
from porter_stemmer import PorterStemmer

REGEX = re.compile(r"[A-Za-z0-9]+")
LOCAL = Path(__file__).resolve().parent
ROOT  = LOCAL.parent

def parse(path):
    docs = []
    docid = None
    sect = None
    title, abstr = [], []

    def flush():
        if docid is not None:
            docs.append((docid, " ".join(title), " ".join(abstr)))

    with open(path, "r", encoding="utf-8", errors="replace") as file:
        for rline in file:
            line = rline.rstrip("\n")
            
            if line.startswith(".I"):
                flush()
                docid = int(line.split()[1])
                sect = None
                title, abstr = [], []
                
            elif line.startswith(".T"):
                sect = "T"
            elif line.startswith(".A"):
                sect = "A"
            elif line.startswith(".B"):
                sect = "B"
            elif line.startswith(".W"):
                sect = "W"
            else:
                if sect == "T":
                    title.append(line)
                elif sect == "W":
                    abstr.append(line)
                    
        flush()
    return docs

def split(text):
    return REGEX.findall(text)

def lower(words):
    return [w.lower()   for w in words if w]

def clean(words, stops):
    return [w for w in words   if w not in stops]

def stem(words, stemr):
    return [stemr.stem(w) for w in words]

def loads(path):
    with open(path, "r", encoding="utf-8", errors="replace") as file:
        return {l.strip().lower() for l in file if l.strip()}

def apply(text, stops, stemr):
    words = split(text)
    words = lower(words)
    words = clean(words, stops)
    words = stem(words, stemr)
    return words

def start(cran, stops, ofile):
    stps = loads(stops)
    stemr = PorterStemmer()
    docs = parse(cran)

    with open(ofile, "w", encoding="utf-8") as out:
        for docid, title, abstr in docs:
            combo = title + " " + abstr
            words = apply(combo, stps, stemr)
            
            out.write(f".I {docid}\n")
            out.write(".S\n")
            out.write(" ".join(words) + "\n")

    return len(docs)

def main():
    cran = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cran.all.1400"
    stops = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "stopwords.txt"
    ofile = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "Normal_Group_processed.all"

    if not cran.exists():
        alt = ROOT / "cran.all"
        if alt.exists():
            cran = alt
        else:
            sys.exit(1)

    count = start(cran, stops, ofile)
    print(f"Done: {count}")

if __name__ == "__main__":
    main()
