# from openai import AzureOpenAI
# import os

# client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_KEY"))

# def embed(text):
#     res = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return res.data[0].embedding

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed(text):
    return model.encode(text).tolist()