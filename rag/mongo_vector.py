from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))

collection = client.rag.documents

def insert_doc(doc):
    collection.insert_one(doc)


def search(query_vector):
    return list(collection.find({
        "$vectorSearch": {
            "queryVector": query_vector,
            "path": "embedding",
            "numCandidates": 100,
            "limit": 5,
            "index": "vector_index"
        }
    }))