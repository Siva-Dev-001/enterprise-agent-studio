from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))

collection = client.rag.documents

def insert_doc(doc):
    collection.insert_one(doc)


def search(query_vector):
    pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_vector,
            "numCandidates": 50,
            "limit": 5,
        }
    }
    ]

    results = collection.aggregate(pipeline)
    return list(results)