"""
Story category definitions.

Different kinds of stories benefit from different structures. A "bedtime
wind-down" story should be slow and soothing; an "adventure" story can be
more energetic. Rather than write one generic prompt for everything, we
classify the request first, then hand it to a category-specific template.
"""

CATEGORIES = {
    "adventure": (
        "An exciting quest or journey. Use a classic hero's-journey shape: "
        "a clear goal, a couple of small obstacles overcome through "
        "cleverness or kindness (never violence), and a triumphant, safe "
        "return home. Keep the stakes kid-sized (a lost toy, a hidden "
        "treasure, a puzzle to solve) - nothing genuinely frightening."
    ),
    "friendship": (
        "A story about two or more characters navigating a small "
        "disagreement or misunderstanding and resolving it through "
        "empathy, communication, or teamwork. Focus on feelings and "
        "gentle character growth rather than external action."
    ),
    "silly": (
        "A lighthearted, funny story full of playful language, silly "
        "mix-ups, and absurd-but-harmless situations. Favor wordplay, "
        "repetition, and gentle slapstick over any real conflict."
    ),
    "bedtime_calm": (
        "A slow, soothing wind-down story with soft imagery (stars, "
        "blankets, quiet forests, sleepy animals). Minimal conflict, a "
        "gently repetitive rhythm, and an ending that explicitly settles "
        "into rest or sleep."
    ),
    "moral_lesson": (
        "A short fable-like story where a character learns a clear, "
        "age-appropriate lesson (sharing, honesty, patience, trying new "
        "things) through their own experience, not through being told the "
        "lesson directly. End with the character reflecting briefly on "
        "what they learned, without a heavy-handed 'moral of the story' "
        "lecture."
    ),
}

CATEGORY_LIST_STR = "\n".join(f"- {k}: {v.split('.')[0]}." for k, v in CATEGORIES.items())


# ---------------------------------------------------------------------------
# Personal Story mode: menus used by profile.py / storyteller.write_personalized_story
# ---------------------------------------------------------------------------
# These are deliberately a *separate* set from CATEGORIES above. CATEGORIES
# backs "Surprise Me" mode, where the categorizer classifies free text.
# STORY_TYPES backs "Personal Story" mode, where the reader picks explicitly
# from a menu, so there's no need to auto-classify.

STORY_TYPES = {
    "adventure": (
        "A classic quest-style story with a clear goal and a couple of "
        "small obstacles solved through cleverness or kindness, ending in "
        "a safe, happy return."
    ),
    "mystery": (
        "A gentle detective story where the hero notices a small, "
        "clue-driven puzzle (a missing item, a secret door) and solves it "
        "step by step using observation and logic - nothing scary, no "
        "real danger."
    ),
    "funny_chaos": (
        "An absurd, playful story full of silly mix-ups (a talking pizza, "
        "flying socks, a day that runs backwards) with lots of wordplay "
        "and harmless slapstick."
    ),
    "magical_world": (
        "A story set in a softly magical world (talking animals, "
        "sparkling forests, floating islands) where the hero explores and "
        "discovers something delightful."
    ),
    "sleepy_wind_down": (
        "A slow, soothing story with soft, repetitive imagery and a "
        "gentle rhythm, designed to calm a child down rather than excite "
        "them."
    ),
}

LESSONS = {
    "kindness": "being kind to others",
    "sharing": "sharing with others",
    "courage": "being brave even when scared",
    "honesty": "telling the truth",
    "trying_again": "trying again after not succeeding the first time",
    "managing_fear": "managing fear or worry",
    "friendship": "being a good friend",
}

TRAITS = ["Brave", "Funny", "Curious", "Kind", "Adventurous", "Creative", "Calm"]

FAVORITES = ["Animals", "Space", "Dinosaurs", "Magic", "Sports", "Royalty",
             "Robots", "Ocean", "School adventures"]

MAGIC_TWIST_EXAMPLES = [
    "a talking object (like a pair of shoes, a backpack, or a spoon)",
    "a secret portal hidden somewhere ordinary",
    "a friendly, silly monster",
    "time slowing down for a few magical minutes",
    "animals that can suddenly speak",
    "a hidden treasure that appears out of nowhere",
]

# (min_words, max_words) targets for each length option.
LENGTH_OPTIONS = {
    "short": (250, 350),
    "medium": (450, 600),
    "long": (650, 850),
}


# ---------------------------------------------------------------------------
# Age group tuning: asked once, up front, before Surprise Me / Personal Story /
# Continue a Series. Affects vocabulary level, available format (poem vs
# story), and the difficulty of the closing activity suggestion.
# ---------------------------------------------------------------------------

AGE_GROUPS = ["5-7", "8-10"]

AGE_GROUP_LABELS = {
    "5-7": "Ages 5-7",
    "8-10": "Ages 8-10",
}

AGE_GROUP_VOCABULARY = {
    "5-7": (
        "Vocabulary must be genuinely simple, not just 'simpler than usual': "
        "mostly 1-2 syllable words. Avoid abstract or fancy words - for example, "
        "prefer 'magic' over 'enchanted', 'place' over 'realm', 'sparkly' over "
        "'shimmering', 'big' over 'majestic'. Average sentence length under 10 "
        "words; no single sentence should run past about 14 words. One simple "
        "idea per sentence - avoid stacking multiple clauses with commas. Favor "
        "repetition and concrete, familiar images (home, family, animals, colors)."
    ),
    "8-10": (
        "Use slightly richer vocabulary and a bit more descriptive detail, "
        "appropriate for a confident 8-10 year old reader - sentences can run "
        "longer and use more varied words than for a 5-7 year old, while "
        "staying warm and easy to follow overall."
    ),
}

# Complexity of the closing "Tomorrow's Little Adventure" activity suggestion.
AGE_GROUP_ACTIVITY = {
    "5-7": (
        "one basic, very concrete activity a 5-7 year old can do with a "
        "little help from a grown-up (examples in spirit, don't copy "
        "verbatim: helping set the table, saying good morning to a family "
        "member, drawing their favorite animal from the story)"
    ),
    "8-10": (
        "one slightly more independent or challenging activity for an 8-10 "
        "year old (examples in spirit, don't copy verbatim: writing two "
        "sentences about their favorite part of today, trying a task by "
        "themselves three times, coming up with their own twist for "
        "tomorrow's story)"
    ),
}

ACTIVITY_SECTION_INSTRUCTION = (
    "After the story's final line, add a short new section on its own line "
    "titled exactly \"Tomorrow's Little Adventure:\" followed by {activity_guidance}, "
    "connected loosely to tonight's story theme where possible. Keep it to 1-2 sentences."
)

STORY_FORMATS = ["story", "poem"]

FORMAT_INSTRUCTION = {
    "story": "",  # default prose story, no extra instruction needed
    "poem": (
        "Instead of a prose story, write the whole piece as a simple, "
        "gentle rhyming poem (still following every rule above about safety, "
        "vocabulary, and pacing), with a short title on the first line."
    ),
}

# For 5-7, always append a short closing poem after the story (and after the
# "Tomorrow's Little Adventure" activity section), regardless of whether the
# main piece itself is prose or already a poem.
CLOSING_POEM_AGE_GROUPS = {"5-7"}

CLOSING_POEM_INSTRUCTION = (
    'After the "Tomorrow\'s Little Adventure:" section, add one more section '
    'on its own line titled exactly "A Little Poem for You:" followed by a '
    "short, gentle, rhyming poem that is 4 to 6 lines long and relates to "
    "tonight's story (its hero, setting, or theme). Simple words, easy rhymes."
)


# ---------------------------------------------------------------------------
# Judge rubric, per age group. judge.py imports this directly to build its
# scoring prompt, so it can check age-appropriate vocabulary/pacing rules
# without duplicating the AGE_GROUP_VOCABULARY text above.
# ---------------------------------------------------------------------------

AGE_GROUP_JUDGE_RUBRIC = {
    "5-7": (
        "For age 5-7, check concretely: is average sentence length under 10 words, "
        "are there any fancy/abstract words (e.g. 'enchanted', 'realm', 'shimmering', "
        "'majestic') that should be simpler, and does any single sentence exceed "
        "about 14 words? If something is off, quote 1-2 exact words or phrases from "
        "the story that should change, rather than giving a generic note like "
        "'simplify the vocabulary'."
    ),
    "8-10": (
        "For age 8-10, check that vocabulary and sentence length are a bit richer "
        "than a 5-7 year old's story would be, while still staying warm, clear, and "
        "easy to follow when read aloud - flag anything that feels babyish/too "
        "simple as well as anything too advanced."
    ),
}


# ---------------------------------------------------------------------------
# "Words You Learned Today" vocabulary section, 8-10 only. Matches the
# "Words You Learned Today:" check in judge.py's rubric for age_group=="8-10".
# ---------------------------------------------------------------------------

VOCABULARY_SECTION_AGE_GROUPS = {"8-10"}

VOCABULARY_SECTION_INSTRUCTION = (
    'After the "Tomorrow\'s Little Adventure:" section, add one more section on '
    'its own line titled exactly "Words You Learned Today:" followed by a '
    "numbered list of 3 to 5 words actually used in the story, each with a short, "
    "child-friendly one-line meaning (e.g. \"1. Hurdles - obstacles to jump over "
    'during a race."). Pick words that are a genuine but gentle stretch for an '
    "8-10 year old, not everyday words they already know."
)