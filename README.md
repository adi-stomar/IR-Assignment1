# IR Assignment 1 — Boolean Retrieval over the Cranfield Collection

Group name used for output file naming: **Normal_Group**

## Files

- `cran.all.1400` — input collection (1400 documents).
- `stopwords.txt` — English stop word list.
- `src/porter_stemmer.py` — pure-Python Porter (1980) stemmer, `PorterStemmer.stem(word)`.
- `src/preprocess.py` — tokenization, normalization, stop word removal, stemming.
- `src/build_index.py` — builds the inverted index.
- `src/boolean_search.py` — Boolean AND/OR query engine.
- `Normal_Group_processed.all` — generated preprocessed collection.
- `Normal_Group_cran.index` — generated inverted index.

## How it works

### 1. Preprocessing (`src/preprocess.py`)

Only the `.T` (title) and `.W` (abstract) fields of each document are used;
`.A` and `.B` are ignored, per the assignment.

Four separate functions implement the four required steps:

- `tokenize(text)` — regex split into alphanumeric token strings.
- `normalize(tokens)` — case-folds tokens to lower case.
- `remove_stopwords(tokens, stopword_set)` — drops tokens found in `stopwords.txt`.
- `stem_tokens(tokens, stemmer)` — applies the Porter stemmer.

They are run in the order `tokenize -> normalize -> remove_stopwords -> stem`,
because `stopwords.txt` contains ordinary (unstemmed) English words, so
stop words must be matched before stemming changes their shape.

Output format, one block per document:
```
.I <docid>
.S
<space-separated final tokens>
```

Run:
```bash
python src/preprocess.py
```
(defaults to `cran.all.1400`, `stopwords.txt`, and writes `Normal_Group_processed.all`
in the parent folder; all three paths can be overridden as CLI args.)

### 2. Indexing (`src/build_index.py`)

Reads the processed file and builds `term -> sorted [docids]`. Output:
```
<vocab_size>, <max_docid>
<term1> <docid,docid,...>
<term2> <docid,docid,...>
...
```
terms sorted lexicographically, postings sorted ascending.

Run:
```bash
python src/build_index.py
```

### 3. Boolean search (`src/boolean_search.py`)

Query terms are put through the same normalize+stem pipeline as document
tokens before lookup. Because postings lists are already sorted, AND/OR
are answered with a linear two-pointer merge (`merge_and` / `merge_or`,
O(len1 + len2)) instead of building Python sets — the standard efficient
algorithm for sorted postings.

Single query:
```bash
python src/boolean_search.py Normal_Group_cran.index "aerodynamics AND slipstream"
```
prints the matching docids as a comma-separated list.

Batch mode (one query per line):
```bash
python src/boolean_search.py Normal_Group_cran.index --queries queries.txt --output results.txt
```
writes `<query> : <docid,docid,...>` per line to `results.txt`.

## Regenerating everything

```bash
cd src
python preprocess.py
python build_index.py
```
