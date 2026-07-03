"""
Component 1: Categorizer

Classifies a free-text story request into one of the categories defined in
categories.py, so the storyteller can use a tailored prompt template.
"""

from categories import CATEGORIES, CATEGORY_LIST_STR
from llm_client import call_model


def categorize_request(user_input: str) -> str:
    prompt = f"""Classify the following bedtime story request into exactly one of
these categories: {", ".join(CATEGORIES.keys())}.

Category descriptions:
{CATEGORY_LIST_STR}

Request: "{user_input}"

Respond with ONLY the category key (e.g. "adventure"), nothing else."""

    result = call_model(prompt, temperature=0.0, max_tokens=10).strip().lower()
    # Guard against the model returning something slightly off-format.
    for key in CATEGORIES:
        if key in result:
            return key
    return "adventure"  # sensible default