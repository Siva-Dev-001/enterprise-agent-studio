from llm.gemini import embed
from rag.mongo_vector import insert_doc

def ingest_text(text):

    vector = embed(text)

    doc = {
        "text": text,
        "embedding": vector
    }

    res = insert_doc(doc)

    print(f"Document inserted successfully: {res.inserted_id}")