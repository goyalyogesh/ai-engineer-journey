# Pinecone side of the same exercise as 14ChromaDb.py, using the SAME 100
# sentences so the two tools can be compared. Pinecone itself doesn't embed
# text for you (unlike Chroma's default behavior) — embeddings are generated
# here with OpenAI's text-embedding-3-small, matching the index's 1536 dims.

import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from sentences_100 import SENTENCES, QUERIES

load_dotenv()

openai_client = OpenAI()
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("sec-10k-analyzer")

EMBED_MODEL = "text-embedding-3-small"


def embed(text: str) -> list[float]:
    return openai_client.embeddings.create(model=EMBED_MODEL, input=text).data[0].embedding


# 1. Embed all 100 sentences and upsert into Pinecone (id, vector, metadata)
vectors = [
    {"id": s["id"], "values": embed(s["text"]), "metadata": {"topic": s["topic"], "text": s["text"]}}
    for s in SENTENCES
]
index.upsert(vectors=vectors)
print(f"Indexed {len(vectors)} sentences in Pinecone.\n")

# 2. Run each query and show the top 5 semantic matches
for query in QUERIES:
    print(f"Query: {query}")
    query_vector = embed(query)
    results = index.query(vector=query_vector, top_k=5, include_metadata=True)
    for match in results["matches"]:
        topic = match["metadata"]["topic"]
        text = match["metadata"]["text"]
        print(f"  [{topic:<20}] (score {match['score']:.4f}) {text}")
    print()
