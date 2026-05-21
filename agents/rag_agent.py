from rag.mongo_vector import search
from llm.gemini import embed

def rag_agent(query):
    vec = embed(query)
    return search(vec)