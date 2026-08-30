# Methodology

## 1. Overview

We implement a simple Boolean retrieval system over the Cranfield collection.

Our implementation has three main stages:

1. Preprocessing the documents
2. Building an inverted index
3. Processing Boolean queries using the index

The input collection contains 1400 documents. For each document, only the title (`.T`) and abstract (`.W`) are used. The author-related fields (`.A` and `.B`) are ignored.

The overall flow is:

```text
cran.all.1400
    |
    v
Preprocessing
    |
    v
Normal_Group_processed.all
    |
    v
Inverted Index
    |
    v
Normal_Group_cran.index
    |
    v
Boolean Search
```

## 2. Preprocessing

The preprocessing is implemented in `src/preprocess.py`.

For every document, the text from the title and abstract is passed through four steps.

### 2.1 Tokenization

The document text is converted into individual tokens.

The implementation extracts alphanumeric strings from the text, so punctuation and other separators do not become part of the tokens.

For example:

```text
"The study of air-flow."
```

becomes roughly:

```text
The
study
of
air
flow
```

### 2.2 Normalization

The tokens are converted to lower case.

For example:

```text
Aerodynamics
AERODYNAMICS
aerodynamics
```

are all normalized to:

```text
aerodynamics
```

This prevents differences in capitalization from creating separate terms in the index.

### 2.3 Stop Word Removal

Common English stop words are removed using the supplied `stopwords.txt` file.

Examples include words such as:

```text
the
of
and
is
```

The stop-word check is done after converting the tokens to lower case.

### 2.4 Stemming

The remaining tokens are stemmed using the Porter stemming algorithm.

We have a Python implementation of the Porter stemmer in `src/porter_stemmer.py`.

For example, different forms of a word can be mapped to the same stem, which helps the retrieval system match related word forms.

### 2.5 Preprocessed File

The final tokens for each document are written to `Normal_Group_processed.all`.

Each document is stored using the `.I` and `.S` tags:

```text
.I <docid>
.S
<space-separated final tokens>
```

## 3. Inverted Index

The indexing stage is implemented in `src/build_index.py`.

The purpose of the inverted index is to store, for every term, the list of documents in which that term occurs.

The basic structure is:

```text
term -> document IDs
```

For example:

```text
aerodynamic -> 1, 10, 11
slipstream   -> 1, 532
```

### 3.1 Building the Index

The processed collection is read document by document.

For every token in a document, the document ID is added to the postings list for that token.

A set is used while constructing the index so that a document ID is not added multiple times for repeated occurrences of the same word in that document.

### 3.2 Sorting

After construction:

- Terms are sorted in lexicographical order.
- Document IDs in each postings list are sorted in ascending order.

The first line of the index stores the vocabulary size and the maximum document ID.

The generated index starts with:

```text
4620, 1400
```

which corresponds to 4620 indexed terms and a maximum document ID of 1400.

The remaining lines have the form:

```text
<term> <docid,docid,...>
```

and are written in lexicographical order.

## 4. Boolean Search

The Boolean search implementation is in `src/boolean_search.py`.

The assignment requires queries containing two words and either `AND` or `OR`.

Examples:

```text
aerodynamics AND slipstream
```

and:

```text
experimental OR theory
```

### 4.1 Query Preprocessing

The query terms are normalized and stemmed before being looked up in the index.

This is important because the same preprocessing applied to the documents must also be applied to the query.

### 4.2 AND

For an `AND` query, a document must occur in both postings lists.

For example:

```text
aerodynamics -> [1, 2, 5]
slipstream   -> [1, 5, 9]
```

gives:

```text
aerodynamics AND slipstream -> [1, 5]
```

The two sorted postings lists are traversed using two pointers.

If the current document IDs are equal, that document is added to the result. Otherwise, the pointer pointing to the smaller ID is advanced.

### 4.3 OR

For an `OR` query, a document occurring in either postings list should be returned.

For example:

```text
aerodynamics -> [1, 2, 5]
slipstream   -> [1, 5, 9]
```

gives:

```text
aerodynamics OR slipstream -> [1, 2, 5, 9]
```

This is also performed using two pointers over the sorted postings lists.

## 5. Program Execution

The main programs in the repository are:

```text
src/preprocess.py
src/build_index.py
src/boolean_search.py
src/porter_stemmer.py
```

The preprocessing stage is run first to generate the processed collection.

The index builder then uses the processed collection to generate:

```text
Normal_Group_cran.index
```

Finally, the Boolean search program uses the index to answer queries.

A typical workflow is:

```bash
python src/preprocess.py
python src/build_index.py
python src/boolean_search.py Normal_Group_cran.index "aerodynamics AND slipstream"
```

## 6. Testing

The repository also contains sample Boolean queries and their results.

Some of the test queries are:

```text
aerodynamics AND slipstream
experimental OR theory
boundary AND layer
supersonic OR hypersonic
flow AND calculation
```

These are used to check that the preprocessing, indexing and Boolean search stages work together correctly.

## 7. Summary

The implementation follows this retrieval pipeline:

```text
Raw documents
    -> tokenization
    -> normalization
    -> stop word removal
    -> stemming
    -> inverted index
    -> Boolean query processing
```

The main idea is that instead of scanning all 1400 documents for every query, the inverted index directly gives the documents associated with each term. Boolean `AND` and `OR` can then be answered by combining the corresponding sorted postings lists.
