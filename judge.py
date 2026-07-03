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

from categories import AGE_GROUP_JUDGE_RUBRIC
from config import PASS_THRESHOLD
from llm_client import call_model

JUDGE_SYSTEM_PROMPT = """You are a strict but fair children's literature editor.
You evaluate bedtime stories intended for children aged 5 to 10 against a rubric.
HARD SAFETY RULE:
- If any content includes violence, harm, death, fear, threats, romance, adult themes, weapons, or unsafe behavior, the score MUST be <= 3 and pass MUST be false.
You always respond with ONLY valid JSON, no other text."""


@dataclass
class JudgeVerdict:
    score: int
    passed: bool
    feedback: str


def judge_story(user_input: str, style_label: str, style_description: str, story: str,
                 story_format: str = "story", age_group: str = "8-10") -> JudgeVerdict:
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
    prompt = f"""Evaluate this bedtime story on a scale of 1-10 using this rubric:
- Age-appropriateness for children (no violence, scares, or adult themes): required
- Explicitly check:
  - no violence or physical harm
  - no scary horror elements
  - no weapons or fighting
  - no romance or kissing
  - no death or loss trauma
  - no unsafe real-world instructions
- Matches the original request: "{user_input}"
- Fits the "{style_label}" story style: {style_description}
- {form_note}
- Warm, engaging, readable-aloud language for the selected age band
- {age_rubric}
- Reasonable length for the request
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
