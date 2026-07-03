# Bedtime Storyteller

A CLI application that generates, judges, and saves bedtime stories for kids aged 5–10 using `gpt-3.5-turbo`. It features a built-in feedback loop between a Storyteller prompt and a Judge prompt to make sure stories fit the target age group and don't repeat themselves.

---

## How It Works

* **Storyteller Engine (`storyteller.py`):** Handles the creative prompts based on age and format rules.
* **Judge Agent (`judge.py`):** Acts as a critic. It reviews the draft, scores it 0–10, and outputs raw JSON with feedback. If the score is under 7, it auto-triggers a rewrite pass.
* **CLI & Router (`main.py`):** Handles user choices (Surprise Me, Personal Story, Series, Library).
* **Storage (`library.py`):** Saves everything to `saved_stories.json`, `bookshelf.json`
---

## Key Features

### Multiple Generation Modes

* **Surprise Me:** Quickly generates a fast, pre-configured story (like a friendly little dragon finding a nightlight) for an instant bedtime option.
* **Personal Story:** A highly customized mode where you can input specific story ideas, choose unique categories (Sci-Fi, Magic, Animals), select preferred format styles, and tailor the hero's profile.
* **Multi-Chapter Book Series:** A serialized book creation system. Instead of generating isolated, one-off stories, you can start a dedicated book and progressively add Chapter 1, Chapter 2, Chapter 3, etc. The system tracks the overall narrative arc across chapters without losing continuity.

### Literature & Age Progression

The vocabulary and sentence structures are explicitly tuned for different reading levels:

* **Ages 5–7:** Simple language, short sentences, and comforting themes. Includes a short, rhythmic poem at the end of the story that wraps up the core lesson in a fun way to help with engagement.
* **Ages 8–10:** More descriptive text with advanced vocabulary and richer world-building. Includes a cliffhanger teaser (`Tomorrow's Little Adventure:`) and a vocabulary/synonym list (`Words You Learned Today:`) featuring 3 to 5 challenging words from the text with simple definitions.

### Smart Series Continuity

To stop the AI from repeating the same setup over and over, continuing a book pulls the last 1,000 characters of the previous chapter. The prompt explicitly tells the model to skip the recaps, assume the reader knows what happened, and advance the plot immediately from the previous scene.

### Storage Layer Architecture

The application isolates its data layer into two explicit JSON-backed data stores to fulfill distinct user experience flows:

1. **`bookshelf.json` (Structured Chapter Series Store)**
* **Purpose:** Handles the **"Continue a Series"** and **"Continue Book"** flows. It organizes entries into a structured dictionary mapping distinct user-profile keys (such as `"taylor"` or `"riya"`) to arrays of books.
* **`book_id`**: An 8-character unique alphanumeric handle derived from a truncated UUID.
* **`hero_name`**: Preserves the original casing provided by the user for runtime rendering.
* **`story_type` & `age_group**`: Stores configuration attributes to ensure subsequent chapter updates remain style-invariant.
* **`chapters`**: An ordered array capturing incremental sequential progress (`chapter_num`), the core story payload text, and an ISO-8601 creation timestamp tracking second-level granularity.


2. **`saved_stories.json` (Ad-Hoc Flat Archive Store)**
* **Purpose:** Functions as an independent flat array archiving quick-saves or standalone, non-chaptered generation outputs.
* **Fields:** Entries utilize an 8-character string `id`, track the specific operational origin `mode` (`"surprise_me"` vs `"personal_story"`), and record the targeted `style_label` alongside the complete textual payload and `saved_at` timestamp.



> **Note on Dynamic Schema Divergence:** Based on demographic settings, text payloads are structurally altered before saving. The `5–7` cohort includes an appended **`A Little Poem for You:`** block, while the `8–10` cohort appends a rigorous **`Words You Learned Today:`** dictionary complete with context-specific definitions.

### Data & Navigation Guardrails

* **No Duplicates:** Prevents creating a new book if the title already exists (case-insensitive), printing: `"This title already exists. Please choose a different book title."`
* **Clean Library view:** Only displays `Title (X chapters)`.
* **Universal Back Button:** Type `Back` or select the `Back` option at any menu. If you choose `Back` on the final save screen, it loops you back to the editing prompt instead of kicking you out to the main menu.

---

## Field Testing & Observations

I put the application to the test with my two 4-year-old cousins during a quiet afternoon, and the results were highly telling:

* **The Power of Crossovers:** They both absolutely loved the **Personal Story** mode. Seeing themselves written directly into the adventure alongside their favorite cartoon characters, Peppa Pig and George, kept them completely locked in.
* **The Nap Effect:** Immediately after narrating just two personalized stories, the older of the two became incredibly drowsy and lazy, drifting right off into an unexpected afternoon nap. It turns out the app's calming imagery design patterns works exactly as intended on a child's active imagination.

---

## Future Roadmap: Scale, Budget & Scope Expansion

Given more development time, a larger project scope, and an allocation budget, the following components would be integrated next:

### 1. Front-End UI Transformation

Moving away from the terminal execution line to build a dedicated, reactive web or mobile application interface using Frameworks like React Native or Flutter. This includes high-contrast, child-friendly theme configurations, micro-animations, and seamless asset deployment.

### 2. Picture Book Genre

Implementing a secondary modality layer using text-to-image synthesis models (e.g., DALL-E or Midjourney API). The generation engine would split the text into explicit panels, auto-generating matching widescreen illustrations with visual scene-to-scene stylistic consistency.

### 3. Audio & Sound FX Integration

Integrating a multi-sensory text-to-speech rendering backend using ElevenLabs. The reader could select character voices, and the app would parse on-omatopoetic sound text to inject live ambient sound assets directly into the narration sequence (e.g., actual barking, animal moos, or rustling leaves).

### 4. Interactive "Choose Your Own Adventure" Genre

Building an branching-path architecture designed specifically to keep older readers (ages 8–10) deeply engaged. Instead of reading a continuous script passive listeners, the storyteller splits chapters or pages into structural decision nodes, prompting the child to interactively dictate the immediate path of the plot.

> **Example Workflow:**
> * *Story Text:* "...Aarvi stands before two shimmering portals inside the Cosmic Carnival. The blue portal hums with the sound of ocean waves, while the gold portal crackles with ancient lightning energy."
> * *Interactive Prompt:*
> 1. Step through the blue portal to explore the underwater sky.
> 2. Leap into the gold portal to discover the lightning castle.
> 
> 
> * *Action:* The child inputs their choice, and the LLM engine instantly generates the targeted consequences of that specific path, tracking a state tree to ensure the structural "Happily Ever After" finale rule is still honored at Chapter 10 regardless of the route taken.
> 
> 
### 5. Parent Feedback & Learning Over Time

Right now the Judge is the only one deciding if a story is good. In the
future, parents could rate each story too — a quick thumbs up/down, or a
1-5 star rating, right after the story ends. Maybe a short optional note
like "too long" or "kid loved it."

Over time, those ratings would pile up into real data: which story types,
lengths, and vocabulary levels actually work best for real kids, not just
what the Judge thinks looks good on paper. Two ways that data could help:

* **Short term:** use the ratings to spot patterns — like if
  `sleepy_wind_down` stories keep getting low ratings, that's a sign the
  prompt needs fixing, even if the Judge kept scoring it a 9.
* **Long term:** use the highest-rated stories as training examples to
  fine-tune a custom model. Instead of hand-tuning prompts forever, the
  app would slowly get better on its own as more parents use it and rate
  stories — the more it's used, the smarter it gets.

This turns story quality into something that improves automatically over
time, instead of only improving when a developer manually tweaks a prompt.

---

## Files

* `main.py` - Main CLI menu loop and routing logic.
* `storyteller.py` - Handles OpenAI payloads and prompt structure.
* `judge.py` - Evaluates the stories and returns JSON ratings.
* `categories.py` - Vocabulary lists, prompts, and age-group rule definitions.
* `hero_profile.py` - Profile creation and character multi-select options.
* `library.py` - JSON file read/write operations and deduplication logic.

---

## Setup

1. Install dependencies:

```bash
pip install openai

```

2. Set your environment variable:

```bash
export OPENAI_API_KEY="your-api-key"

```

3. Run the app:

```bash
python3 main.py

```

4. Run tests:

```bash
python3 test.py

```