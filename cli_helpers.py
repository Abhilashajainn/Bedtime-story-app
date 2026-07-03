"""
Small, reusable CLI helpers for numbered single-pick and multi-pick menus.
Used by profile.py to build the "Personal Story" onboarding flow without
making the reader type free text for every field.
"""

from typing import Sequence


def pick_single(question: str, options: Sequence[str], allow_skip: bool = False) -> str:
    """Prints a numbered menu and returns the chosen option string.
    If allow_skip is True, an empty Enter returns "" (used for optional fields)."""
    print(f"\n{question}")
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    if allow_skip:
        print("  (press Enter to skip)")

    while True:
        raw = input("> ").strip()
        if allow_skip and not raw:
            return ""
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"Please enter a number between 1 and {len(options)}.")


def pick_multi(question: str, options: Sequence[str], max_picks: int, allow_skip: bool = False) -> list:
    """Prints a numbered menu and returns up to max_picks chosen option strings,
    parsed from a comma-separated list like '1,3,5'."""
    print(f"\n{question} (pick up to {max_picks}, comma-separated, e.g. 1,3)")
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    if allow_skip:
        print("  (press Enter to skip)")

    while True:
        raw = input("> ").strip()
        if allow_skip and not raw:
            return []
        try:
            indices = [int(x.strip()) for x in raw.split(",") if x.strip()]
        except ValueError:
            print("Please enter numbers separated by commas, e.g. 1,3.")
            continue
        if not indices or any(i < 1 or i > len(options) for i in indices):
            print(f"Please enter numbers between 1 and {len(options)}.")
            continue
        picks = [options[i - 1] for i in dict.fromkeys(indices)]  # dedupe, keep order
        return picks[:max_picks]