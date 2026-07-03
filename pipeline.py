"""
Orchestration: categorize -> write -> judge -> revise.

This is the only module that knows about all three components at once; it
wires them into the judge-driven revision loop described in README.md.
Both entry points (Surprise Me and Personal Story / bookshelf chapters)
share the same shape: write a draft, judge it, revise up to MAX_REVISIONS
times if needed.
"""

from dataclasses import dataclass, field
from typing import Optional

from categories import CATEGORIES, STORY_TYPES
from categorizer import categorize_request
from config import MAX_REVISIONS
from judge import judge_story
from storyteller import write_story, write_personalized_story


@dataclass
class PipelineResult:
    story: str
    category: str
    revisions: int
    final_score: int
    history: list = field(default_factory=list)  # list of (story, verdict) for transparency


def generate_story(user_input: str, age_group: str = "8-10", story_format: str = "story",
                    verbose: bool = True) -> PipelineResult:
    category = categorize_request(user_input)
    if verbose:
        print(f"\n[categorizer] -> {category}")

    story = write_story(user_input, category, age_group=age_group, story_format=story_format)
    verdict = judge_story(user_input, category, CATEGORIES[category], story, story_format=story_format, age_group=age_group)
    history = [(story, verdict)]

    if verbose:
        print(f"[judge] draft 1 score={verdict.score}/10 pass={verdict.passed}  feedback: {verdict.feedback}")

    revisions = 0
    while not verdict.passed and revisions < MAX_REVISIONS:
        revisions += 1
        story = write_story(user_input, category, age_group=age_group, story_format=story_format,
                             feedback=verdict.feedback, previous_story=story)
        verdict = judge_story(user_input, category, CATEGORIES[category], story, story_format=story_format, age_group=age_group)
        history.append((story, verdict))
        if verbose:
            print(f"[judge] revision {revisions} score={verdict.score}/10 pass={verdict.passed}  feedback: {verdict.feedback}")

    # If nothing ever passed the threshold, don't just show whatever came last -
    # a later revision can score worse than an earlier draft. Show the best one seen.
    best_story, best_verdict = max(history, key=lambda pair: pair[1].score)
    return PipelineResult(story=best_story, category=category, revisions=revisions,
                           final_score=best_verdict.score, history=history)


def generate_personalized_story(profile, story_type: str, lesson: Optional[str], magic_twist: Optional[str],
                                 length_key: str, age_group: str = "8-10", story_format: str = "story",
                                 chapter_num: Optional[int] = None, sequel_recap: Optional[str] = None,
                                 verbose: bool = True) -> PipelineResult:
    """Same categorize->write->judge->revise shape as generate_story(), but for
    Personal Story / Continue a Series mode, where the reader picked the story
    type explicitly instead of it being classified from free text."""
    user_input_label = f"personalized {story_type} story for {profile.name}"
    if chapter_num:
        user_input_label += f" (chapter {chapter_num})"

    story = write_personalized_story(profile, story_type, lesson, magic_twist, length_key,
                                      age_group=age_group, story_format=story_format,
                                      chapter_num=chapter_num, sequel_recap=sequel_recap)
    verdict = judge_story(user_input_label, story_type, STORY_TYPES[story_type], story, story_format=story_format, age_group=age_group)
    history = [(story, verdict)]

    if verbose:
        print(f"[judge] draft 1 score={verdict.score}/10 pass={verdict.passed}  feedback: {verdict.feedback}")

    revisions = 0
    while not verdict.passed and revisions < MAX_REVISIONS:
        revisions += 1
        story = write_personalized_story(profile, story_type, lesson, magic_twist, length_key,
                                          age_group=age_group, story_format=story_format,
                                          chapter_num=chapter_num, sequel_recap=sequel_recap,
                                          feedback=verdict.feedback, previous_story=story)
        verdict = judge_story(user_input_label, story_type, STORY_TYPES[story_type], story, story_format=story_format, age_group=age_group)
        history.append((story, verdict))
        if verbose:
            print(f"[judge] revision {revisions} score={verdict.score}/10 pass={verdict.passed}  feedback: {verdict.feedback}")

    # Same "best, not last" logic as generate_story() above.
    best_story, best_verdict = max(history, key=lambda pair: pair[1].score)
    return PipelineResult(story=best_story, category=story_type, revisions=revisions,
                           final_score=best_verdict.score, history=history)