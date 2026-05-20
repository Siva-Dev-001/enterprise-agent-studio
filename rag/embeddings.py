# from openai import AzureOpenAI
# import os

# client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_KEY"))

# def embed(text):
#     res = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return res.data[0].embedding

### --------------------------------------------------------
# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("all-MiniLM-L6-v2")


# def embed(text):
#     return model.encode(text).tolist()

### --------------------------------------
from dotenv import load_dotenv
from openai import OpenAI
from typing import overload

import os

load_dotenv()   # ← must be called before OpenAI client is created

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
MAX_BATCH   = 2048


# ── Overloads tell the type checker exactly what to expect ───────────────────
@overload
def embed(text: str) -> list[float]: ...

@overload
def embed(text: list[str]) -> list[list[float]]: ...

def embed(text: str | list[str]) -> list[float] | list[list[float]]:
    """
    Generate embeddings for a single string or a batch of strings.
    - Pass a str  → returns list[float]
    - Pass a list → returns list[list[float]]
    """
    is_single = isinstance(text, str)
    inputs    = [text] if is_single else text

    if len(inputs) > MAX_BATCH:
        raise ValueError(f"Batch size {len(inputs)} exceeds limit of {MAX_BATCH}.")

    inputs = [t.replace("\n", " ").strip() for t in inputs]

    res     = client.embeddings.create(model=EMBED_MODEL, input=inputs)
    vectors = [item.embedding for item in sorted(res.data, key=lambda x: x.index)]

    return vectors[0] if is_single else vectors


def embed_in_batches(texts: list[str], batch_size: int = 512) -> list[list[float]]:
    """Embed a large list in safe batches, always returns list[list[float]]."""
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        result = embed(texts[i : i + batch_size])   # type checker knows → list[list[float]]
        all_vectors.extend(result)
    return all_vectors


# ── Quick test ───────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     single: list[float]        = embed("What is a transformer?")
#     batch:  list[list[float]]  = embed(["Hello", "World"])

#     print(f"Single dims : {len(single)}")
#     print(f"Batch count : {len(batch)}, dims each: {len(batch[0])}")