import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in


# Define the schema for the index
schema = Schema(path=ID(stored=True), content=TEXT)

# Create or open the search index
if not os.path.exists("my_search_index"):
    os.mkdir("my_search_index")
ix = create_in("my_search_index", schema)

# Create an index writer
writer = ix.writer()

# Index text files
text_files_dir = "pdf_extracted_data"
for root, dirs, files in os.walk(text_files_dir):
    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(root, file), "r") as f:
                content = f.read()
            writer.add_document(path=os.path.join(root, file), content=content)

# Commit the changes
writer.commit()
