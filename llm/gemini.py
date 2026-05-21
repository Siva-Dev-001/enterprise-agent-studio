# gemini.py
import os
from typing import overload, Any
from google import genai
from google.genai import types
import PIL.Image
from dotenv import load_dotenv
load_dotenv()
# ── Client setup ──────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY is not set.\n"
        "  → Get your key at: https://aistudio.google.com/app/apikey\n"
        "  → Then run: export GEMINI_API_KEY='...'"
    )

# genai.Client(api_key=api_key)
# It automatically picks up the GEMINI_API_KEY environment variable
client = genai.Client()
# ── Model config ──────────────────────────────────────────────────────────────
LLM_MODEL   = os.getenv("GEMINI_LLM_MODEL",   "gemini-2.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL",  "gemini-embedding-001")
MAX_TOKENS  = int(os.getenv("GEMINI_MAX_TOKENS", "1024"))

# ── LLM call ──────────────────────────────────────────────────────────────────
def call_llm(
    prompt:      str,
    system:      str  = "",
    temperature: float = 0.7,
    max_tokens:  int   = MAX_TOKENS,
) -> str:
    """
    Send a prompt to Gemini and return the text response.
    """
    # System instructions and configurations are passed into GenerateContentConfig
    config = types.GenerateContentConfig(
        system_instruction=system if system else None,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=config
    )
    return response.text


# ── Chat (multi-turn) ─────────────────────────────────────────────────────────
class GeminiChat:
    """
    Stateful multi-turn chat session with Gemini using the new GenAI SDK.
    """
    def __init__(self, system: str = "", temperature: float = 0.7):
        self.model_name = LLM_MODEL
        self.config = types.GenerateContentConfig(
            system_instruction=system if system else None,
            temperature=temperature,
            max_output_tokens=MAX_TOKENS,
        )
        # In the new SDK, client.chats.create sets up the stateful session
        self._session = client.chats.create(
            model=self.model_name,
            config=self.config
        )

    def send(self, message: str) -> str:
        """Send a message and return the assistant reply."""
        response = self._session.send_message(message)
        return response.text

    def history(self) -> list[dict]:
        """Return chat history as a list of {role, text} dicts."""
        # Note: Depending on the turn type, you might extract text via msg.parts[0].text
        return [
            {"role": msg.role, "text": msg.parts[0].text}
            for msg in self._session.get_history()
        ]

    def reset(self):
        """Clear chat history by re-creating the session."""
        self._session = client.chats.create(
            model=self.model_name,
            config=self.config
        )


# ── Embeddings ────────────────────────────────────────────────────────────────
@overload
def embed(text: str)       -> list[float]: ...
@overload
def embed(text: list[str]) -> list[list[float]]: ...

def embed(text: str | list[str]) -> list[float] | list[list[float]]:
    """
    Generate embeddings using Gemini.
    """
    is_single = isinstance(text, str)
    inputs = [text] if is_single else text
    inputs = [t.replace("\n", " ").strip() for t in inputs]

    # Task type and options are bundled inside EmbedContentConfig
    config = types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT"
    )

    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=inputs,
        config=config,
    )

    # The modern SDK returns an array of embedding objects where the vector is in .values
    if is_single:
        return result.embeddings[0].values
    else:
        return [e.values for e in result.embeddings]


def embed_in_batches(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """
    Embed a large list in safe batches.
    """
    all_vectors = []
    config = types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=[t.replace("\n", " ").strip() for t in batch],
            config=config,
        )
        all_vectors.extend([e.values for e in result.embeddings])
        
    return all_vectors


# ── Vision (image input) ──────────────────────────────────────────────────────
def call_vision(prompt: str, image_path: str) -> str:
    """
    Send a prompt + image to Gemini Vision.
    """
    image = PIL.Image.open(image_path)
    
    # Text and images are passed fluidly in a flat list to contents
    response = client.models.generate_content(
        model=LLM_MODEL, 
        contents=[prompt, image]
    )
    return response.text


# ── Quick test ────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     # LLM
#     print("── LLM ──────────────────────────────")
#     print(call_llm("Explain transformers in 2 sentences."))

#     # LLM with system prompt
#     print("\n── LLM with system prompt ───────────")
#     print(call_llm("What is 2+2?", system="You are a sarcastic math tutor."))

#     # Chat
#     print("\n── Chat ─────────────────────────────")
#     chat = GeminiChat(system="You are a helpful assistant.")
#     print(chat.send("My name is Alex."))
#     print(chat.send("What is my name?"))

#     # Embeddings
#     print("\n── Embeddings ───────────────────────")
#     single = embed("What is a transformer?")
#     print(f"Single vector dims : {len(single)}")

#     batch = embed(["Hello world", "How are you?"])
#     print(f"Batch count        : {len(batch)}, dims: {len(batch[0])}")