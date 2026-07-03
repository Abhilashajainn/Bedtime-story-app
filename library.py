"""
Local JSON-backed story library.

Two separate stores, because they serve different UX needs:
- saved_stories.json: ad-hoc "save this for later" - a flat list, any mode,
  no ongoing structure implied.
- bookshelf.json: multi-chapter book series per hero, used by the
  "Continue a Series" flow. Each hero can have multiple books; each book is
  an ordered list of chapters.
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional

SAVED_STORIES_FILE = os.path.join(os.path.dirname(__file__), "saved_stories.json")
BOOKSHELF_FILE = os.path.join(os.path.dirname(__file__), "bookshelf.json")
TITLE_EXISTS_MESSAGE = "This title already exists. Please choose a different book title."


class DuplicateBookTitleError(ValueError):
    pass


def _normalize_title(title: str) -> str:
    return " ".join(title.strip().lower().split())


def _load(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save(path: str, data) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _dedupe_books(books: List[dict]) -> tuple:
    merged = []
    by_title = {}
    changed = False

    for book in books:
        title_key = _normalize_title(book.get("title", ""))
        if not title_key:
            merged.append(book)
            continue

        if title_key not in by_title:
            by_title[title_key] = book
            merged.append(book)
            continue

        target = by_title[title_key]
        changed = True
        for chapter in book.get("chapters", []):
            copied = dict(chapter)
            copied["chapter_num"] = len(target.setdefault("chapters", [])) + 1
            target["chapters"].append(copied)

    return merged, changed


def _load_bookshelf(dedupe: bool = True):
    shelf = _load(BOOKSHELF_FILE, {})
    if not dedupe:
        return shelf

    changed = False
    for hero_key, books in list(shelf.items()):
        deduped_books, did_change = _dedupe_books(books)
        shelf[hero_key] = deduped_books
        changed = changed or did_change

    if changed:
        _save(BOOKSHELF_FILE, shelf)
    return shelf


# ---- Save-for-later (ad hoc, non-chaptered) --------------------------------

def save_story_for_later(title: str, text: str, mode: str, style_label: str, age_group: str) -> str:
    stories = _load(SAVED_STORIES_FILE, [])
    story_id = str(uuid.uuid4())[:8]
    stories.append({
        "id": story_id,
        "title": title,
        "mode": mode,  # "surprise_me" | "personal_story"
        "style_label": style_label,
        "age_group": age_group,
        "text": text,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    })
    _save(SAVED_STORIES_FILE, stories)
    return story_id


def list_saved_stories() -> List[dict]:
    return _load(SAVED_STORIES_FILE, [])


# ---- Bookshelf (chaptered series per hero) ---------------------------------

def list_all_heroes() -> List[str]:
    """Returns the hero display names that have at least one book, for
    browsing without already knowing a name."""
    shelf = _load_bookshelf()
    names = []
    for key, books in shelf.items():
        if books:
            names.append(books[0].get("hero_name", key.title()))
    return names


def list_books_for_hero(hero_name: str) -> List[dict]:
    shelf = _load_bookshelf()
    return shelf.get(hero_name.strip().lower(), [])


def book_title_exists(title: str) -> bool:
    normalized = _normalize_title(title)
    if not normalized:
        return False

    shelf = _load_bookshelf()
    for books in shelf.values():
        for book in books:
            if _normalize_title(book.get("title", "")) == normalized:
                return True
    return False


def create_book(hero_name: str, title: str, story_type: str, age_group: str, first_chapter_text: str) -> str:
    shelf = _load_bookshelf()
    if book_title_exists(title):
        raise DuplicateBookTitleError(TITLE_EXISTS_MESSAGE)

    key = hero_name.strip().lower()
    books = shelf.setdefault(key, [])
    book_id = str(uuid.uuid4())[:8]
    books.append({
        "book_id": book_id,
        "hero_name": hero_name.strip(),  # display-cased, e.g. "Mia" not "mia"
        "title": title,
        "story_type": story_type,
        "age_group": age_group,
        "chapters": [{
            "chapter_num": 1,
            "text": first_chapter_text,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }],
    })
    _save(BOOKSHELF_FILE, shelf)
    return book_id


def add_chapter(hero_name: str, book_id: str, chapter_text: str) -> int:
    shelf = _load_bookshelf()
    key = hero_name.strip().lower()
    books = shelf.get(key, [])
    for book in books:
        if book["book_id"] == book_id:
            next_num = len(book["chapters"]) + 1
            book["chapters"].append({
                "chapter_num": next_num,
                "text": chapter_text,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
            _save(BOOKSHELF_FILE, shelf)
            return next_num
    raise ValueError(f"Book {book_id} not found for {hero_name}")


def get_book(hero_name: str, book_id: str) -> Optional[dict]:
    for book in list_books_for_hero(hero_name):
        if book["book_id"] == book_id:
            return book
    return None
