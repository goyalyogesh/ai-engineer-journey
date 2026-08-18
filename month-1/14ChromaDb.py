# Chroma's built-in default embedding model (all-MiniLM-L6-v2), so no external
# API key is needed here — a separate local embedding space from the Pinecone
# script (which uses OpenAI's text-embedding-3-small).

import chromadb
from sentences_100 import SENTENCES, QUERIES

# 1. Initialize a persistent client (saves data locally to a folder)
client = chromadb.PersistentClient(path="./chroma_db_data")

# 2. Create or get a collection
collection = client.get_or_create_collection(name="sec_10k_sentences")

# 3. Add all 100 sentences (Chroma embeds them automatically)
collection.upsert(
    ids=[s["id"] for s in SENTENCES],
    documents=[s["text"] for s in SENTENCES],
    metadatas=[{"topic": s["topic"]} for s in SENTENCES],
)
print(f"Indexed {collection.count()} sentences in Chroma.\n")

# 4. Run each query and show the top 5 semantic matches
for query in QUERIES:
    print(f"Query: {query}")
    results = collection.query(query_texts=[query], n_results=5)
    for doc, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        print(f"  [{meta['topic']:<20}] (distance {distance:.4f}) {doc}")
    print()
