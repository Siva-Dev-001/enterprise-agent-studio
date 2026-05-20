from rag.mongo_vector import search
from rag.embeddings import embed

def rag_agent(query):
    vec = embed(query)
    return search(vec)