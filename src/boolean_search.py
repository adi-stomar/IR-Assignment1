# File Action: Performs Boolean search over the index using two terms and AND/OR operator.
# Running Example:
# Input query: "aerodynamic AND flow"
# 1. parse: "aerodynamic", "AND", "flow"
# 2. norm: "aerodynam", "flow"
# 3. get lists: list1=[1,10,11], list2=[10,12]
# 4. merge: [10]
# 5. Output: 10

import re
import sys
from pathlib import Path
from porter_stemmer import PorterStemmer

REGEX = re.compile(r"[A-Za-z0-9]+")
LOCAL = Path(__file__).resolve().parent
ROOT  = LOCAL.parent

def reads(path):
    index = {}
    with open(path, "r", encoding="utf-8", errors="replace") as file:
        head = file.readline().strip()
        vocab, maxid = (int(x.strip()) for x in head.split(","))
        for line in file:
            line = line.rstrip("\n")
            if not line: continue
            
            term, posts = line.split(" ", 1)
            index[term] = [int(x)  for x in posts.split(",") if x]
            
    return index, vocab, maxid

def norm(raw, stemr):
    words = REGEX.findall(raw)
    if not words:
        return ""
    word = words[0].lower()
    return stemr.stem(word)

def merge(list1, list2):
    found = []
    i = j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            found.append(list1[i])
            i += 1
            j += 1
            
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1
            
    return found

def union(list1, list2):
    found = []
    i = j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            found.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            found.append(list1[i])
            i += 1
        else:
            found.append(list2[j])
            j += 1
            
    found.extend(list1[i:])
    found.extend(list2[j:])
    return found

def parse(query):
    parts = query.strip().split()
    if len(parts) != 3:
        raise ValueError("Bad query")
    
    term1, oper, term2 = parts
    oper = oper.upper()
    if oper not in ("AND", "OR"):
        raise ValueError("Bad oper")
    return term1, oper, term2

def solve(query, index, stemr):
    raw1, oper, raw2 = parse(query)
    term1 = norm(raw1, stemr)
    term2 = norm(raw2, stemr)

    post1 = index.get(term1, [])
    post2 = index.get(term2, [])

    if oper == "AND":
        found = merge(post1, post2)
    else:
        found = union(post1, post2)

    return found

def chars(docs):
    return ",".join(str(d) for d in docs)

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    path = Path(sys.argv[1])
    stemr = PorterStemmer()
    index, vocab, maxid = reads(path)

    if "--queries" in sys.argv:
        q_idx = sys.argv.index("--queries")
        qfile = Path(sys.argv[q_idx + 1])
        ofile = None
        if "--output" in sys.argv:
            o_idx = sys.argv.index("--output")
            ofile = Path(sys.argv[o_idx + 1])

        items = []
        with open(qfile, "r", encoding="utf-8") as file:
            for line in file:
                query = line.strip()
                if not query:
                    continue
                try:
                    found = solve(query, index, stemr)
                    items.append(f"{query} : {chars(found)}")
                except ValueError as e:
                    items.append(f"{query} : ERR")

        text = "\n".join(items)
        if ofile:
            with open(ofile, "w", encoding="utf-8") as out:
                out.write(text + "\n")
            print(f"Wrote {len(items)} to {ofile}")
        else:
            print(text)
            
    else:
        query = " ".join(sys.argv[2:])
        found = solve(query, index, stemr)
        print(chars(found))

if __name__ == "__main__":
    main()
