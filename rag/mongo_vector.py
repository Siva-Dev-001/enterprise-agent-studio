from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
# Database 
db = client["rag_db"] 
# Collection 
collection = db["documents"]

# ───────────────────────────────────────────────────────────── 
#  Insert Document into MongoDB 
# ─────────────────────────────────────────────────────────────
def insert_doc(doc):
    result = collection.insert_one(doc)
    return result
    # print(collection.count_documents({}))
    # print(collection.find_one())

# ───────────────────────────────────────────────────────────── 
# Vector Search 
# ─────────────────────────────────────────────────────────────

def search(query_vector):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "rag-search-index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": 5
            }
        }
        # {
        #     "$project": {
        #         "_id": 0,
        #         "text": 1,
        #         "score": {
        #             "$meta": "vectorSearchScore"
        #         }
        #     }
        # }
    ]
    results = collection.aggregate(pipeline)
    # try:
    #     doc = collection.find_one()
    #     print(doc.keys())
    #     print(len(doc["embedding"]))
    #     print(type(doc["embedding"]))
    # except Exception as e:
    #     print(e)
    results_new = list(collection.aggregate(pipeline))

    # print("VECTOR RESULTS:", results_new)
    return list(results)