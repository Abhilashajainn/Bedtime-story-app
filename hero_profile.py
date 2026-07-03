"""
Personal Story mode: collects a lightweight hero profile via numbered picks
instead of free typing (name is the only typed field).
"""

from dataclasses import dataclass, field
from typing import List

from categories import TRAITS, FAVORITES
from cli_helpers import pick_multi


@dataclass
class HeroProfile:
    name: str
    traits: List[str] = field(default_factory=list)
    favorites: List[str] = field(default_factory=list)
    supporting_cast: List[str] = field(default_factory=list)


def collect_profile(name: str = None, back_option: str = None):
    if name is None:
        prompt = "\nWho is the hero of tonight's story? (name"
        if back_option:
            prompt += ", or type Back"
        prompt += ") "
        name = input(prompt).strip()
        if back_option and name.lower() == back_option.lower():
            return back_option
        name = name or "the hero"
    else:
        print(f"\nLet's refresh a few details for {name}'s next chapter.")

    trait_options = TRAITS + ([back_option] if back_option else [])
    traits = pick_multi(f"What is {name} like?", trait_options, max_picks=3)
    if back_option and back_option in traits:
        return back_option

    favorite_options = FAVORITES + ([back_option] if back_option else [])
    favorites = pick_multi(f"What does {name} love?", favorite_options, max_picks=3)
    if back_option and back_option in favorites:
        return back_option

    cast_raw = input(
        "\nAdd any family or pets to the story? "
        "(comma-separated names, press Enter to skip, or type Back) "
    ).strip()
    if back_option and cast_raw.lower() == back_option.lower():
        return back_option
    supporting_cast = [c.strip() for c in cast_raw.split(",") if c.strip()] if cast_raw else []

    return HeroProfile(name=name, traits=traits, favorites=favorites, supporting_cast=supporting_cast)
