"""
Component 2: Storyteller

Writes the initial draft and rewrites it, either in response to judge
feedback (a revision pass) or a reader's free-text change request.

Both write_story() (Surprise Me) and write_personalized_story() (Personal
Story / Continue a Series) now take age_group and story_format, so the
same two functions serve both age bands and both story/poem formats rather
than branching into separate copies.
"""

from dataclasses import dataclass
from typing import Optional

from categories import (
    ACTIVITY_SECTION_INSTRUCTION,
    AGE_GROUP_ACTIVITY,
    AGE_GROUP_VOCABULARY,
    CATEGORIES,
    CLOSING_POEM_AGE_GROUPS,
    CLOSING_POEM_INSTRUCTION,
    FORMAT_INSTRUCTION,
    LENGTH_OPTIONS,
    LESSONS,
    STORY_TYPES,
    VOCABULARY_SECTION_AGE_GROUPS,
    VOCABULARY_SECTION_INSTRUCTION,
)
from llm_client import call_model


def _age_and_format_rules(age_group: str, story_format: str, chapter_num: Optional[int] = None) -> str:
    vocab = AGE_GROUP_VOCABULARY[age_group]
    activity = ACTIVITY_SECTION_INSTRUCTION.format(activity_guidance=AGE_GROUP_ACTIVITY[age_group])
    fmt = FORMAT_INSTRUCTION.get(story_format, "")
    lines = [vocab, activity]
    if fmt:
        lines.append(fmt)
    if age_group in CLOSING_POEM_AGE_GROUPS:
        lines.append(CLOSING_POEM_INSTRUCTION)
    
    # Only add the vocabulary section/teaser rules if it is NOT the final chapter (Chapter 10)
    if age_group in VOCABULARY_SECTION_AGE_GROUPS and chapter_num != 10:
        lines.append(VOCABULARY_SECTION_INSTRUCTION)
        
    return "\n".join(f"- {line}" for line in lines)


@dataclass
class StoryDraft:
    text: str
    category: str


def write_story(user_input: str, category: str, age_group: str = "8-10", story_format: str = "story",
                 feedback: Optional[str] = None, previous_story: Optional[str] = None,
                 user_feedback: Optional[str] = None) -> str:
    """Generates (or revises) a Surprise Me story draft.

    - On the first pass, feedback/previous_story are None -> fresh draft.
    - On a judge-driven revision, we pass the judge's feedback + prior draft.
    - On a user-driven revision, we pass the user's free-text request + prior draft.
    """
    style_guidance = CATEGORIES[category]

    system = f"""You are a warm, imaginative children's author who writes
bedtime stories for children.

Hard rules, always:
- No violence, death, gore, romance, swearing, or anything scary/disturbing.
- Warm, gentle tone throughout, short-to-medium sentences.
- Include a character or two the reader can root for, and a satisfying ending.
- Always clearly establish the physical setting in the first 1–2 sentences (e.g. home, park, bedroom, school).
- Maintain spatial consistency throughout the story (do not teleport between scenes without transition).
- Every major scene change must include a transition phrase (e.g. "after a while", "as they finished playing", "later that evening").
- Never use phrases like "goodbye" or "waved goodbye" unless it is clear WHO is leaving, WHERE they are going, and WHY.
- Open every story with a calm establishing moment that describes:
  (1) where the characters are,
  (2) what the environment looks or feels like,
  (3) what they are doing normally BEFORE anything changes.
- Do NOT start immediately with dialogue, action, or a problem.
- The problem/magic event must come ONLY after the setting is grounded.
{_age_and_format_rules(age_group, story_format)}
- If age_group is "5-7", include simple daily life activities like brushing teeth, cleaning toys, helping with chores, eating meals, or getting ready for bed. Keep them very concrete and familiar.
- Output ONLY the story itself (a short title on the first line is welcome), no
  preamble, no notes, no "Here is your story:" framing."""

    if previous_story and feedback:
        prompt = f"""Original request: "{user_input}"
Story category: {category} - {style_guidance}

Here is a previous draft of the story:
---
{previous_story}
---

An editor reviewed it and gave this feedback:
"{feedback}"

Rewrite the story to address the feedback while keeping what already worked.
Follow all the style rules you were given."""
    elif previous_story and user_feedback:
        prompt = f"""Original request: "{user_input}"
Story category: {category} - {style_guidance}

Here is the current story:
---
{previous_story}
---

The reader (a parent/child) asked for this change:
"{user_feedback}"

If the story doesn't already reflect this, rewrite it to incorporate the
change, keeping the parts they didn't ask to change. If the story already
does what they asked, make that explicit some other way (e.g. reinforce it
more clearly in a line or two) rather than returning the text completely
unchanged, so it's obvious the request was heard. Follow all the style
rules you were given."""
    else:
        prompt = f"""Write a bedtime story for the following request:
"{user_input}"

Story category: {category} - {style_guidance}"""

    return call_model(prompt, system=system, temperature=0.9, max_tokens=1200)


# ---------------------------------------------------------------------------
# Personal Story mode (also used by the bookshelf / Continue a Series flow)
# ---------------------------------------------------------------------------

def write_personalized_story(profile, story_type: str, lesson: Optional[str], magic_twist: Optional[str],
                              length_key: str, age_group: str = "8-10", story_format: str = "story",
                              chapter_num: Optional[int] = None, sequel_recap: Optional[str] = None,
                              feedback: Optional[str] = None, previous_story: Optional[str] = None,
                              user_feedback: Optional[str] = None) -> str:
    """Generates (or revises) a Personal Story mode draft, optionally as one
    chapter of an ongoing book.

    profile: HeroProfile (name, traits, favorites, supporting_cast)
    story_type: key into categories.STORY_TYPES
    lesson: key into categories.LESSONS, or None for "no lesson"
    magic_twist: one string picked from categories.MAGIC_TWIST_EXAMPLES, or None if the toggle is off
    length_key: "short" | "medium" | "long" -> categories.LENGTH_OPTIONS
    chapter_num: if this story is part of a bookshelf book, its chapter number (1, 2, 3...)
    sequel_recap: context about what happened previously (prior chapter text or a recap), or None
    feedback: judge-driven revision feedback (internal quality loop)
    user_feedback: reader's free-text change request (post-story "want any changes?" loop)
    """
    style_guidance = STORY_TYPES[story_type]
    min_words, max_words = LENGTH_OPTIONS[length_key]

    system = f"""You are a warm, imaginative children's author who writes
personalized bedtime stories starring the named hero.

Hard rules, always:
- No violence, death, gore, romance, swearing, or anything scary/disturbing.
- The hero's name and traits should shape what they do and how they solve the story's
  problem (e.g. a "curious" hero notices a clue others miss; a "kind" hero helps a
  stranger). Don't just insert the name - make the personalization feel earned.
  - Always clearly establish the physical setting in the first 1–2 sentences (e.g. home, park, bedroom, school).
- Maintain spatial consistency throughout the story (do not teleport between scenes without transition).
- Every major scene change must include a transition phrase (e.g. "after a while", "as they finished playing", "later that evening").
- Never use phrases like "goodbye" or "waved goodbye" unless it is clear WHO is leaving, WHERE they are going, and WHY.
- Open every story with a calm establishing moment:
  (1) location
  (2) mood
  (3) normal activity BEFORE disruption
- Inciting event must never be in sentence 1.
- The final ~20% of the story must slow down: shorter, slower sentences, gentle
  repetitive/calming imagery (wind, stars, quiet), settling toward sleep.
- The very last line of the story itself must be exactly: "Goodnight, {profile.name}. And they lived happily ever after." if chapter_num == 10 else f'The very last line of the story itself must be exactly: "Goodnight, {profile.name}. See you in tomorrow\'s adventure."'{_age_and_format_rules(age_group, story_format, chapter_num)}
- For age_group "5-7", naturally weave in 1–2 simple daily-life routines (like brushing teeth, cleaning toys, eating meals, or getting ready for bed) ONLY if they fit the scene. Keep them short, concrete, and part of the flow — not a checklist.- Output ONLY the story itself, no preamble, no notes, no "Here is your story:" framing."""

    traits_str = ", ".join(profile.traits) if profile.traits else "curious and kind"
    favorites_str = ", ".join(profile.favorites) if profile.favorites else "everyday adventures"
    cast_str = f"Supporting characters to include: {', '.join(profile.supporting_cast)}. " \
        if profile.supporting_cast else ""
    lesson_str = f"Weave in a soft, unspoken lesson about {LESSONS[lesson]} - show it through what " \
        f"the hero does, never state it as a moral. " if lesson else ""
    twist_str = f"Include exactly one magic twist: {magic_twist}. " if magic_twist else ""

    # Setup the Chapter Title and detect if it's the final chapter
    if chapter_num and chapter_num > 1:
        if chapter_num == 10:
            title_instruction = (
                f'This is Chapter 10, the FINAL chapter of the entire book series about {profile.name}. '
                f'Start the output with a line reading exactly "Chapter 10: <short evocative subtitle>" '
                f'in place of a generic title.'
            )
        else:
            title_instruction = (
                f'This is Chapter {chapter_num} of an ongoing book about {profile.name}. Start the '
                f'output with a line reading exactly "Chapter {chapter_num}: <short evocative subtitle>" '
                f'in place of a generic title.'
            )
    elif chapter_num == 1:
        title_instruction = (
            f'This is Chapter 1, the start of a brand-new book about {profile.name}. Start the '
            f'output with a line reading exactly "Chapter 1: <short evocative subtitle>" in place '
            f'of a generic title.'
        )
    else:
        title_instruction = ""

    # Continuity context instructions
    sequel_str = f"""This is a serialized story.
The reader has just finished the previous chapter, whose final scene was:
---
{sequel_recap}
---
Continue immediately from that final scene. Do NOT recap, summarize, or
repeat events that already occurred. Do NOT rediscover locations, portals,
magic objects, or characters that were already introduced. Advance the plot
from the exact point where the previous chapter ended. Each chapter should
contain mostly new events while still feeling connected to the previous
chapter. """ if sequel_recap else ""

    # Force the Finale if it hits Chapter 10
    final_chapter_instruction = ""
    if chapter_num == 10:
        final_chapter_instruction = f"""
=== ABSOLUTE FINALE RULES ===
This is Chapter 10, the last chapter of the book. You MUST wrap up all open narrative threads, 
conclude the adventure permanently, and ensure the characters achieve a complete, satisfying, 
and joyful "happily ever after" resolution. No new cliffhangers or teasers are allowed.
"""

    base_prompt = f"""Write a personalized bedtime story starring {profile.name}, a hero who is {traits_str}
and loves {favorites_str}. {cast_str}{lesson_str}{twist_str}{sequel_str}{title_instruction}{final_chapter_instruction}

Story type: {story_type.replace('_', ' ')} - {style_guidance}

Target length: {min_words}-{max_words} words."""

    if previous_story and feedback:
        prompt = f"""{base_prompt}

Here is a previous draft:
---
{previous_story}
---

An editor gave this feedback: "{feedback}"
Rewrite the story to address it while keeping what already worked."""
    elif previous_story and user_feedback:
        prompt = f"""{base_prompt}

Here is the current story:
---
{previous_story}
---

The reader (a parent/child) asked for this change: "{user_feedback}"

If the story doesn't already reflect this, rewrite it to incorporate the
change, keeping the parts they didn't ask to change. If the story already
does what they asked (e.g. it already uses the requested pronoun/detail),
make that explicit some other way - for example, reinforce it more clearly
in a line or two - rather than returning the text completely unchanged, so
it's obvious the request was heard. Keep the required closing line exactly
as specified."""
    else:
        prompt = base_prompt

    return call_model(prompt, system=system, temperature=0.9, max_tokens=1400)