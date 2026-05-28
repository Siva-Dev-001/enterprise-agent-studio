from rag.mongo_vector import search
from llm.gemini import embed

def rag_agent(query):
    vec = embed(query)
    results = search(vec)
    # print("===== QUERY VECTOR SIZE:", len(vec)) ### Helped for mongodb vector search indexing
    contexts = []
    # print("\n=====Search Results: ", results)
    for r in results:
        if "text" in r:
            contexts.append(r["text"])
    # print("=== RAG Context: ", contexts)
    return contexts