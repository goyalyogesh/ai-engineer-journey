#Chroma's built-in default embedding model (all-MiniLM-L6-v2), so you do not need an external API key like OpenAI to get started.

import chromadb

# 1. Initialize a persistent client (saves data locally to a folder)
client = chromadb.PersistentClient(path="./chroma_db_data")

# 2. Create or get a collection
# Chroma automatically handles the embedding generation for text
collection = client.get_or_create_collection(name="my_documents")

# 3. Add text data to the collection
collection.add(
    documents=[
        "Chroma is a vector database designed for LLM apps.",
        "Python is a versatile programming language used for data science.",
        "Semantic search matches concepts, not just exact keyword strings.",
        "RAG stands for Retrieval-Augmented Generation."
    ],
    ids=["doc1", "doc2", "doc3", "doc4"]
)

# 4. Perform a semantic search query
# The engine will find the closest conceptual match, even without matching words
results = collection.query(
    query_texts=["How do you find meaning in text data?"],
    n_results=2
)

# 5. Print the top matches
for doc, score in zip(results['documents'][0], results['distances'][0]):
    print(f"Match: {doc} (Distance score: {score:.4f})")
