# Variables
TRAIN_DOCS = cran.all.1400
STOPWORDS = stopwords.txt
PROCESSED_DOCS = Normal_Group_processed.all
INDEX = Normal_Group_cran.index
QUERIES = sample_queries.txt
DETAILED_OUTPUT = output.txt
PYTHON = python3

# Default target runs when you just type 'make'
all: $(DETAILED_OUTPUT)

# Step 3: Run boolean search to generate detailed output
$(DETAILED_OUTPUT): $(QUERIES) src/boolean_search.py $(INDEX)
	$(PYTHON) src/boolean_search.py $(INDEX) --queries $(QUERIES) --output $(DETAILED_OUTPUT)

# Step 2: Build the inverted index from preprocessed documents
$(INDEX): $(PROCESSED_DOCS) src/build_index.py
	$(PYTHON) src/build_index.py $(PROCESSED_DOCS) $(INDEX)

# Step 1: Preprocess the training documents
$(PROCESSED_DOCS): $(TRAIN_DOCS) $(STOPWORDS) src/preprocess.py
	$(PYTHON) src/preprocess.py $(TRAIN_DOCS) $(STOPWORDS) $(PROCESSED_DOCS)

# Clean up generated files
clean:
	rm -f $(DETAILED_OUTPUT) $(PROCESSED_DOCS) $(INDEX)
