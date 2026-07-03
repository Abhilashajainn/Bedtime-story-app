"""
Bedtime Story Generator - CLI entry point.

Flow:
  1. Mode:
       - Surprise Me       - free-text idea; Categorizer picks the story type.
       - Personal Story    - pick-based hero profile + story type; one-off,
                             with an optional "save for later" at the end.
       - Continue a Series - a per-hero bookshelf of multi-chapter books;
                             continue an existing book's next chapter, or
                             start a brand-new book (chapter 1).
       - My Story Library  - browse and re-read saved stories and past
                             bookshelf chapters. No generation, no age
                             group needed.
  2. (Surprise Me / Personal Story / new series only) Age group (5-7 or
     8-10) - tunes vocabulary and activity difficulty. Continued series use
     the age group already saved with that book. Every story is prose; for
     age 5-7, a short 4-6 line rhyme related to the story is appended at
     the end.

The three generation modes share the same Storyteller -> Judge -> revision
loop (pipeline.py).
"""

from categories import AGE_GROUP_LABELS, AGE_GROUPS, LESSONS, MAGIC_TWIST_EXAMPLES, STORY_TYPES
from cli_helpers import pick_single
from hero_profile import collect_profile
from library import (
    TITLE_EXISTS_MESSAGE,
    DuplicateBookTitleError,
    add_chapter,
    book_title_exists,
    create_book,
    list_all_heroes,
    list_books_for_hero,
    list_saved_stories,
    save_story_for_later,
)
from pipeline import generate_personalized_story, generate_story
from storyteller import write_personalized_story, write_story

BACK_OPTION = "Back"


def print_story(result):
    print("\n" + "=" * 60)
    print(result.story)
    print("=" * 60)
    print(f"(category: {result.category} | judge score: {result.final_score}/10 | revisions: {result.revisions})")


def choose_age_group() -> str:
    label = pick_single("How old is tonight's listener?", [AGE_GROUP_LABELS[a] for a in AGE_GROUPS] + [BACK_OPTION])
    if label == BACK_OPTION:
        return BACK_OPTION
    return AGE_GROUPS[[AGE_GROUP_LABELS[a] for a in AGE_GROUPS].index(label)]


def offer_save(story_text: str, mode: str, style_label: str, age_group: str) -> bool:
    save = pick_single("Save this story for later?", ["Yes", "No", BACK_OPTION])
    if save == BACK_OPTION:
        return False
    if save == "Yes":
        title = story_text.strip().split("\n")[0][:60]
        story_id = save_story_for_later(title, story_text, mode, style_label, age_group)
        print(f"Saved! (id: {story_id})")
    return True


def book_label(book: dict) -> str:
    chapter_count = len(book["chapters"])
    chapter_word = "chapter" if chapter_count == 1 else "chapters"
    return f'{book["title"]} ({chapter_count} {chapter_word})'


def ask_new_book_title(default_title: str) -> str:
    while True:
        raw = input(
            "\nWhat should we call this new book? "
            "(or press Enter for a default title, or type Back) "
        ).strip()
        if raw.lower() == "back":
            return BACK_OPTION

        title = raw or default_title
        if book_title_exists(title):
            print(TITLE_EXISTS_MESSAGE)
            continue
        return title


def run_surprise_me(age_group: str, story_format: str):
    user_input = input("\nWhat kind of story do you want to hear? (or type Back) ").strip()
    if user_input.lower() == BACK_OPTION.lower():
        return False
    result = generate_story(user_input, age_group=age_group, story_format=story_format)
    print_story(result)

    story = result.story
    while True:
        again = input("\nWant any changes? (describe them, or press Enter to finish) ").strip()
        if not again:
            break
        story = write_story(user_input, result.category, age_group=age_group, story_format=story_format,
                             previous_story=story, user_feedback=again)
        print("\n" + "=" * 60)
        print(story)
        print("=" * 60)

    return offer_save(story, "surprise_me", result.category, age_group)


def run_personal_story(age_group: str, story_format: str):
    profile = collect_profile(back_option=BACK_OPTION)
    if profile == BACK_OPTION:
        return False

    story_type = pick_single("What kind of adventure tonight?", list(STORY_TYPES.keys()) + [BACK_OPTION])
    if story_type == BACK_OPTION:
        return False

    lesson_options = list(LESSONS.keys()) + ["no_lesson"]
    lesson_pick = pick_single("Want a hidden lesson tucked into the story?", lesson_options + [BACK_OPTION])
    if lesson_pick == BACK_OPTION:
        return False
    lesson = None if lesson_pick == "no_lesson" else lesson_pick

    twist_pick = pick_single("Include a magic twist?", ["on", "off", BACK_OPTION])
    if twist_pick == BACK_OPTION:
        return False
    twist_on = twist_pick == "on"
    magic_twist = MAGIC_TWIST_EXAMPLES[hash(profile.name) % len(MAGIC_TWIST_EXAMPLES)] if twist_on else None

    length_key = pick_single("How long should the story be?", ["short", "medium", "long", BACK_OPTION])
    if length_key == BACK_OPTION:
        return False

    result = generate_personalized_story(profile, story_type, lesson, magic_twist, length_key,
                                          age_group=age_group, story_format=story_format)
    print_story(result)

    story = result.story
    while True:
        again = input("\nWant any changes? (describe them, or press Enter to finish) ").strip()
        if not again:
            break
        story = write_personalized_story(profile, story_type, lesson, magic_twist, length_key,
                                          age_group=age_group, story_format=story_format,
                                          previous_story=story, user_feedback=again)
        print("\n" + "=" * 60)
        print(story)
        print("=" * 60)

    return offer_save(story, "personal_story", story_type, age_group)


def run_series(story_format: str):
    while True:
        heroes = list_all_heroes()
        action = "Start a brand-new series"
        if heroes:
            action = pick_single("Would you like to continue a saved book or create a new series?", [
                "Continue an existing book",
                "Start a brand-new series",
                BACK_OPTION,
            ])
            if action == BACK_OPTION:
                return False
        else:
            print("\nNo saved series found yet - let's start a brand-new one!")

        book = None
        if action == "Continue an existing book":
            hero_name = pick_single("Whose bookshelf should we open?", heroes + [BACK_OPTION])
            if hero_name == BACK_OPTION:
                continue

            existing_books = list_books_for_hero(hero_name)
            shelf_labels = [book_label(b) for b in existing_books]
            pick = pick_single(f"{hero_name}'s saved books:", shelf_labels + [BACK_OPTION])
            if pick == BACK_OPTION:
                continue

            book = existing_books[shelf_labels.index(pick)]
            # --- ADD MAX CHAPTER GUARDRAIL HERE ---
            current_chapters = len(book["chapters"])
            if current_chapters >= 10:
                print("\n🛑 This book is already complete! It has reached its maximum limit of 10 chapters.")
                print("Please start a brand-new series or read this book from your Story Library.")
                input("\nPress Enter to return to the menu...")
                continue # Bounces the user back to the series menu safely
            # --------------------------------------
            profile = collect_profile(book["hero_name"], back_option=BACK_OPTION)
            if profile == BACK_OPTION:
                continue
            age_group = book["age_group"]
            story_type = book["story_type"]
            print(f'\nContinuing "{book["title"]}" as chapter {len(book["chapters"]) + 1}.')
            break

        profile = collect_profile(back_option=BACK_OPTION)
        if profile == BACK_OPTION:
            continue
        age_group = choose_age_group()
        if age_group == BACK_OPTION:
            continue
        story_type = pick_single("What kind of adventure tonight?", list(STORY_TYPES.keys()) + [BACK_OPTION])
        if story_type == BACK_OPTION:
            continue
        break

    lesson_options = list(LESSONS.keys()) + ["no_lesson"]
    lesson_pick = pick_single("Want a hidden lesson tucked into the story?", lesson_options + [BACK_OPTION])
    if lesson_pick == BACK_OPTION:
        return run_series(story_format)
    lesson = None if lesson_pick == "no_lesson" else lesson_pick

    twist_pick = pick_single("Include a magic twist?", ["on", "off", BACK_OPTION])
    if twist_pick == BACK_OPTION:
        return run_series(story_format)
    twist_on = twist_pick == "on"
    magic_twist = MAGIC_TWIST_EXAMPLES[hash(profile.name) % len(MAGIC_TWIST_EXAMPLES)] if twist_on else None

    length_key = pick_single("How long should the chapter be?", ["short", "medium", "long", BACK_OPTION])
    if length_key == BACK_OPTION:
        return run_series(story_format)

    if book is None:
        title = ask_new_book_title(f"{profile.name}'s Adventures")
        if title == BACK_OPTION:
            return run_series(story_format)
        chapter_num = 1
        sequel_recap = None
    else:
        title = book["title"]
        chapter_num = len(book["chapters"]) + 1
        last_chapter_text = book["chapters"][-1]["text"]
        # Give the model the ending, not a recap, so the next chapter can move forward.
        sequel_recap = last_chapter_text[-1000:]

    result = generate_personalized_story(profile, story_type, lesson, magic_twist, length_key,
                                          age_group=age_group, story_format=story_format,
                                          chapter_num=chapter_num, sequel_recap=sequel_recap)
    print_story(result)

    story = result.story
    while True:
        again = input("\nWant any changes to this chapter? (describe them, or press Enter to finish) ").strip()
        if not again:
            break
        story = write_personalized_story(profile, story_type, lesson, magic_twist, length_key,
                                          age_group=age_group, story_format=story_format,
                                          chapter_num=chapter_num, sequel_recap=sequel_recap,
                                          previous_story=story, user_feedback=again)
        print("\n" + "=" * 60)
        print(story)
        print("=" * 60)

    if book is None:
        try:
            create_book(profile.name, title, story_type, age_group, story)
            print(f'\nStarted a new book: "{title}" (chapter 1 saved).')
        except DuplicateBookTitleError as exc:
            print(str(exc))
    else:
        add_chapter(profile.name, book["book_id"], story)
        print(f'\nAdded chapter {chapter_num} to "{title}".')
    return True


def run_library():
    saved = list_saved_stories()
    heroes = list_all_heroes()

    if not saved and not heroes:
        print("\nNothing saved yet - stories you save, or bookshelf chapters "
              "you write, will show up here.")
        return False

    options = []
    if saved:
        options.append("Saved stories")
    if heroes:
        options.append("Bookshelf books")
    pick = pick_single("What would you like to look at?", options + [BACK_OPTION])
    if pick == BACK_OPTION:
        return False

    if pick == "Saved stories":
        labels = [f'{s["title"]}  ({s["mode"]}, saved {s["saved_at"][:10]})' for s in saved]
        chosen = pick_single("Saved stories:", labels + [BACK_OPTION])
        if chosen == BACK_OPTION:
            return run_library()
        print("\n" + "=" * 60)
        print(saved[labels.index(chosen)]["text"])
        print("=" * 60)
        return True

    hero_name = pick_single("Whose bookshelf?", heroes + [BACK_OPTION])
    if hero_name == BACK_OPTION:
        return run_library()

    books = list_books_for_hero(hero_name)
    book_labels = [book_label(b) for b in books]
    chosen_book = pick_single(f"{hero_name}'s books:", book_labels + [BACK_OPTION])
    if chosen_book == BACK_OPTION:
        return run_library()
    book = books[book_labels.index(chosen_book)]

    chapter_labels = [f'Chapter {c["chapter_num"]}' for c in book["chapters"]]
    chosen_chapter = pick_single(f'"{book["title"]}" - which chapter?', chapter_labels + [BACK_OPTION])
    if chosen_chapter == BACK_OPTION:
        return run_library()
    chapter = book["chapters"][chapter_labels.index(chosen_chapter)]
    print("\n" + "=" * 60)
    print(chapter["text"])
    print("=" * 60)
    return True


def main():
    while True:
        mode = pick_single("Let's make tonight's bedtime adventure!", [
            "Surprise Me",
            "Personal Story",
            "Continue a Series",
            "My Story Library (read saved stories & past chapters)",
            BACK_OPTION,
        ])

        if mode == BACK_OPTION:
            return

        if mode == "My Story Library (read saved stories & past chapters)":
            completed = run_library()
            if completed:
                return
            continue

        story_format = "story"  # prose only; 5-7 gets a closing rhyme appended, not a full-poem format

        if mode == "Surprise Me":
            age_group = choose_age_group()
            if age_group == BACK_OPTION:
                continue
            completed = run_surprise_me(age_group, story_format)
            if completed:
                return
            continue
        if mode == "Personal Story":
            age_group = choose_age_group()
            if age_group == BACK_OPTION:
                continue
            completed = run_personal_story(age_group, story_format)
            if completed:
                return
            continue

        completed = run_series(story_format)
        if completed:
            return


if __name__ == "__main__":
    main()
