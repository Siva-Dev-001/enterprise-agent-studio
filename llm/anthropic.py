import os
import anthropic

# ── Anthropic client ─────────────────────────────────────────────────────────
_anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))   # set this in your environment

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


def call_llm(prompt: str) -> str:
    """
    Call Claude via the Anthropic API.

    Args:
        prompt: The user prompt string.

    Returns:
        The model's response as a string.
    """
    message = _anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── Quick test ───────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     print(call_llm("Explain what a transformer model is in two sentences."))