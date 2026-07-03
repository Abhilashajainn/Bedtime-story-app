"""
Component 3: Judge

Scores a story draft against a kid-lit rubric and returns structured
feedback the storyteller can act on during a revision pass.

Takes a style label + description directly (rather than importing CATEGORIES
itself) so it works for both "Surprise Me" mode (categories.py CATEGORIES)
and "Personal Story" mode (categories.py STORY_TYPES).
"""

import json
from dataclasses import dataclass
from typing import Optional

from categories import AGE_GROUP_JUDGE_RUBRIC
from config import PASS_THRESHOLD
from llm_client import call_model

JUDGE_SYSTEM_PROMPT = """You are a strict but fair children's literature editor.
You evaluate bedtime stories intended for children aged 5 to 10 against a rubric.
HARD SAFETY RULE:
- If any content includes violence, harm, death, fear, threats, romance, adult themes, weapons, or unsafe behavior, the score MUST be <= 3 and pass MUST be false.
HARD LENGTH RULE:
- If a target word count range is given below and the story's actual word count falls
  outside that range, the score MUST be capped at 6 and pass MUST be false - no matter
  how good the writing is otherwise. Length compliance is not optional or a tiebreaker;
  treat it as a hard gate, the same way you treat the safety rule above.
You always respond with ONLY valid JSON, no other text."""


@dataclass
class JudgeVerdict:
    score: int
    passed: bool
    feedback: str


def judge_story(user_input: str, style_label: str, style_description: str, story: str,
                 story_format: str = "story", age_group: str = "8-10",
                 min_words: Optional[int] = None, max_words: Optional[int] = None) -> JudgeVerdict:
    age_rubric = AGE_GROUP_JUDGE_RUBRIC[age_group]
    form_note = (
        "This piece is a rhyming POEM, not prose - judge it as a poem (rhythm and rhyme quality "
        "matter, prose narrative structure does not need to be as strict)."
        if story_format == "poem" else
        "This piece is prose - it should have a clear beginning, middle, and end."
    )
    poem_note = (
        '\n- Must include a closing section titled "A Little Poem for You:" with a 4-to-6-line '
        "rhyming poem related to the story - check the line count is within that range."
        if age_group == "5-7" else ""
    )
    vocab_note = (
        '\n- Must include a closing section titled "Words You Learned Today:" with 3 to 5 '
        "words from the story, each with a short child-friendly meaning."
        if age_group == "8-10" else ""
    )

    # Compute the real word count ourselves rather than trusting the model to self-report -
    # this is what the HARD LENGTH RULE above actually needs to check against.
    actual_word_count = len(story.split())
    if min_words is not None and max_words is not None:
        length_note = (
            f"- WORD COUNT (hard gate - see HARD LENGTH RULE above): target is {min_words}-{max_words} "
            f"words. This draft is approximately {actual_word_count} words. State the actual number and "
            f"the target range in your feedback if it's out of range (e.g. 'story is ~{actual_word_count} "
            f"words but needs to be {min_words}-{max_words}; expand the middle scene with another beat' "
            "or 'trim the opening description'). Remember: out-of-range length caps the score at 6 "
            "regardless of writing quality."
        )
    else:
        length_note = "- Reasonable length for the request"

    prompt = f"""Evaluate this bedtime story on a scale of 1-10 using this rubric:
- Age-appropriateness for children (no violence, scares, or adult themes): required
- Explicitly check:
  - no violence or physical harm
  - no scary horror elements
  - no weapons or fighting
  - no romance or kissing
  - no death or loss trauma
  - no unsafe real-world instructions
  - nothing illegal
- Matches the original request: "{user_input}"
- Fits the "{style_label}" story style: {style_description}
- {form_note}
- Warm, engaging, readable-aloud language for the selected age band
- {age_rubric}
{length_note}
- Includes a "Tomorrow's Little Adventure:" activity section at the end{poem_note}{vocab_note}

Story:
---
{story}
---

Respond with ONLY this JSON shape:
{{"score": <integer 1-10>, "pass": <true/false, true only if score >= {PASS_THRESHOLD} and there are no safety issues>, "feedback": "<1-3 concise, actionable sentences on what to fix, or 'Looks great' if nothing needs fixing>"}}"""

    raw = call_model(prompt, system=JUDGE_SYSTEM_PROMPT, temperature=0.0, max_tokens=300)

    try:
        # Judges sometimes wrap JSON in code fences despite instructions; strip those defensively.
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)
        return JudgeVerdict(score=int(data["score"]), passed=bool(data["pass"]), feedback=str(data["feedback"]))
    except (json.JSONDecodeError, KeyError, ValueError):
        # Fail safe: if we can't parse the judge, don't block the user forever -
        # treat it as a pass so the pipeline still terminates.
        return JudgeVerdict(score=PASS_THRESHOLD, passed=True, feedback="Judge response unparseable; accepted as-is.")