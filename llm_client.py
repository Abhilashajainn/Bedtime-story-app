"""
Single wrapper around the Chat Completions call, used by the categorizer,
storyteller, and judge alike, so all of them share one place to change
retries/logging/model params in the future.
"""

from config import client, MODEL


def call_model(prompt: str, system: str = "", max_tokens: int = 1200, temperature: float = 0.8) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()