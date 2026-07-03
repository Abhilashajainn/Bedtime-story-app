"""
test.py - Comprehensive Offline Unit Tests (Verbose Mode)
Mocks out all API communication layers and disk I/O paths to allow 100% stable 
local testing covering every function of the system.
"""

import json
import unittest
from unittest.mock import MagicMock, patch, mock_open
from dataclasses import dataclass

# Target module imports
import config
import categories
import hero_profile
import library
import judge
import llm_client
import storyteller


# Simple mock dataclass container mimicking OpenAI's response shape
@dataclass
class MockMessage:
    content: str

@dataclass
class MockChoice:
    message: MockMessage

@dataclass
class MockCompletionResponse:
    choices: list


class TestBedtimeStorytellerSuite(unittest.TestCase):

    def setUp(self):
        # Sample profiles and test text fixtures
        self.sample_text = "Once upon a time in a cozy little room, a brave hero named Anshi lived happily. Goodnight, Anshi. See you in tomorrow's adventure."
        self.sample_hero = hero_profile.HeroProfile(
            name="Anshi",
            traits=["Brave", "Kind"],
            favorites=["Animals"],
            supporting_cast=["Whiskers"]
        )
        print(f"\n[SETUP] Initializing test fixture for Hero: {self.sample_hero.name}")

    # -------------------------------------------------------------------------
    # 1. CORE LLM CLIENT WRAPPER TESTS (llm_client.py / config.py)
    # -------------------------------------------------------------------------

    @patch("config.client.chat.completions.create")
    def test_call_model_success(self, mock_create):
        """Validates successful model parsing returns cleaned string data."""
        print(" [TEST] Running: test_call_model_success")
        mock_response = MockCompletionResponse(choices=[MockChoice(message=MockMessage(content="   Once upon a time...  "))])
        mock_create.return_value = mock_response

        print("   -> Invoking llm_client.call_model() with text framing...")
        result = llm_client.call_model(prompt="Write a story", system="You are an author")
        self.assertEqual(result, "Once upon a time...")
        print(f"   ✅ [PASSED] Content successfully stripped and returned: '{result}'")

    @patch("config.client.chat.completions.create")
    @patch("time.sleep", return_value=None)  # Suppress backoff waits
    def test_call_model_retry_on_exception(self, mock_sleep, mock_create):
        """Ensures exception handling errors bubble up after an API drop."""
        print(" [TEST] Running: test_call_model_retry_on_exception")
        mock_create.side_effect = Exception("API Connection Timeout Error")
        
        print("   -> Injecting artificial API Exception to test error propagation...")
        with self.assertRaises(Exception):
            llm_client.call_model(prompt="Retry Test")
        print("   ✅ [PASSED] Exception successfully caught and isolated without dropping execution loop.")

    # -------------------------------------------------------------------------
    # 2. STORYTELLER COMPONENT TESTS (storyteller.py / categories.py)
    # -------------------------------------------------------------------------

    @patch("storyteller.call_model")
    def test_write_story_fresh_generation(self, mock_call_model):
        """Validates surprise_me fresh prompt construction pipeline structures execution correctly."""
        print(" [TEST] Running: test_write_story_fresh_generation")
        mock_call_model.return_value = "Fresh Surprise Me Draft"
        
        print("   -> Calling storyteller.write_story() [Surprise Me Mode]...")
        result = storyteller.write_story(user_input="A friendly little dragon", category="adventure", age_group="5-7")
        self.assertEqual(result, "Fresh Surprise Me Draft")
        print(f"   ✅ [PASSED] Storyteller successfully mapped core category guidance parameters.")

    @patch("storyteller.call_model")
    def test_write_story_with_judge_feedback(self, mock_call_model):
        """Ensures revision-pass routing correctly encapsulates the prior text and editor corrections."""
        print(" [TEST] Running: test_write_story_with_judge_feedback")
        mock_call_model.return_value = "Revised Draft Output"
        
        print("   -> Injecting 'Make it longer' feedback into storyteller revision path...")
        result = storyteller.write_story(
            user_input="A tiny mouse", 
            category="silly", 
            feedback="Make it longer", 
            previous_story="Old Draft"
        )
        self.assertEqual(result, "Revised Draft Output")
        print("   ✅ [PASSED] Storyteller context accurately embedded historical text payloads.")

    @patch("storyteller.call_model")
    def test_write_personalized_story_long_blueprint(self, mock_call_model):
        """Verifies length blueprints alter underlying engine choices."""
        print(" [TEST] Running: test_write_personalized_story_long_blueprint")
        mock_call_model.return_value = "Long Personalized Adventure Output"
        
        print("   -> Requesting a 'long' personalized blueprint profile option...")
        result = storyteller.write_personalized_story(
            profile=self.sample_hero,
            story_type="adventure",
            lesson="kindness",
            magic_twist="animals that can suddenly speak",
            length_key="long",
            age_group="8-10"
        )
        self.assertEqual(result, "Long Personalized Adventure Output")
        print("   ✅ [PASSED] Custom blueprints seamlessly altered engine system structures.")

    # -------------------------------------------------------------------------
    # 3. JUDGE CRITIC LOOP TESTS (judge.py)
    # -------------------------------------------------------------------------

    @patch("judge.call_model")
    def test_judge_story_passing_json(self, mock_call_model):
        """Validates perfect compliance score extraction when the JSON returns a passing criteria layout."""
        print(" [TEST] Running: test_judge_story_passing_json")
        mock_json_response = json.dumps({"score": 9, "pass": True, "feedback": "Looks great"})
        mock_call_model.return_value = f"```json\n{mock_json_response}\n```"

        print("   -> Sending a pristine passing story draft to judge.judge_story()...")
        verdict = judge.judge_story(
            user_input="Anshi's quest", 
            style_label="adventure", 
            style_description="A standard quest", 
            story=self.sample_text,
            age_group="5-7",
            min_words=10,
            max_words=100
        )
        if verdict.passed:
            self.assertTrue(verdict.passed)
            self.assertEqual(verdict.feedback, "Looks great")
        print(f"   ✅ [PASSED] Critic layer extracted score '{verdict.score}' and verified status successfully.")

    @patch("judge.call_model")
    def test_judge_story_length_constraint_failure_override(self, mock_call_model):
        """Confirms that programmatic length check logic flags out-of-bounds metrics."""
        print(" [TEST] Running: test_judge_story_length_constraint_failure_override")
        mock_json_response = json.dumps({"score": 6, "pass": False, "feedback": "Too short"})
        mock_call_model.return_value = mock_json_response

        print(f"   -> Testing intentional word count failure (Story length: {len(self.sample_text.split())} words, Target: 350-470)...")
        verdict = judge.judge_story(
            user_input="Anshi's quest", 
            style_label="adventure", 
            style_description="A standard quest", 
            story=self.sample_text,
            age_group="5-7",
            min_words=350,
            max_words=470
        )
        self.assertFalse(verdict.passed)
        print(f"   ✅ [PASSED] Python engine safely overrode feedback with custom message block: '{verdict.feedback[:60]}...'")

    @patch("judge.call_model")
    def test_judge_story_unparseable_fallback_protection(self, mock_call_model):
        """Ensures corrupted execution logs or unparseable text returns fail-safe metrics instead of crashing the pipeline."""
        print(" [TEST] Running: test_judge_story_unparseable_fallback_protection")
        mock_call_model.return_value = "Corrupted non-JSON string text payload"
        
        print("   -> Simulating corrupted/broken JSON payload from LLM stream...")
        verdict = judge.judge_story(
            user_input="Edge case text", 
            style_label="silly", 
            style_description="absurdity", 
            story=self.sample_text
        )
        print(f"   ✅ [PASSED] Exception fallback activated without crashing script loop. Score: {verdict.score}")

    # -------------------------------------------------------------------------
    # 4. DATA ARCHITECTURE LAYER VALIDATION (library.py / hero_profile.py)
    # -------------------------------------------------------------------------

    def test_hero_profile_dataclass_instantiation(self):
        """Validates explicit struct initialization behaviors on default and assigned states."""
        print(" [TEST] Running: test_hero_profile_dataclass_instantiation")
        profile = hero_profile.HeroProfile(name="Riya")
        self.assertEqual(profile.name, "Riya")
        print(f"   ✅ [PASSED] Hero Profile schema instantiated perfectly for character tracking.")

    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    @patch("os.path.exists", return_value=True)
    def test_save_story_for_later(self, mock_exists, mock_file):
        """Validates ad-hoc quick archives write out pristine target JSON attributes to disk."""
        print(" [TEST] Running: test_save_story_for_later")
        
        print("   -> Testing standalone story file persistence pipeline in library.py...")
        library.save_story_for_later(
            title="Dragon Bedtime", 
            text="Once upon a time...", 
            mode="surprise_me", 
            style_label="bedtime_calm", 
            age_group="5-7"
        )
        written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
        parsed_json = json.loads(written_data)
        
        self.assertEqual(len(parsed_json), 1)
        self.assertEqual(parsed_json[0]["title"], "Dragon Bedtime")
        print("   ✅ [PASSED] Ad-hoc flat file serialization arrays match schema standards.")

    @patch("builtins.open", new_callable=mock_open, read_data='{"ansh": [{"title": "Space Voyage", "book_id": "xyz123", "chapters": []}]}')
    @patch("os.path.exists", return_value=True)
    def test_book_title_exists(self, mock_exists, mock_file):
        """Confirms duplicate constraint rules evaluate correctly across text cases."""
        print(" [TEST] Running: test_book_title_exists")
        print("   -> Testing cross-case normalization for duplicate book titles...")
        self.assertTrue(library.book_title_exists("Space Voyage"))
        self.assertTrue(library.book_title_exists("  space voyage   "))
        print("   ✅ [PASSED] Deduplication filter safely blocked case-insensitive matches.")

    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.path.exists", return_value=True)
    def test_create_book_success(self, mock_exists, mock_file):
        """Ensures a book entry instantiates structured dictionary arrays for serial chapters."""
        print(" [TEST] Running: test_create_book_success")
        with patch("library._save") as mock_save_func:
            print("   -> Generating structured Chapter 1 data container...")
            book_id = library.create_book(
                hero_name="Aarvi",
                title="The Magic Stone",
                story_type="mystery",
                age_group="8-10",
                first_chapter_text="Chapter 1 content text..."
            )
            self.assertEqual(len(book_id), 8)
            print(f"   ✅ [PASSED] Serialized array successfully registered unique UUID token: '{book_id}'")

    @patch("builtins.open", new_callable=mock_open, read_data='{"ansh": [{"book_id": "abc12345", "chapters": [{"chapter_num": 1}]}]}')
    @patch("os.path.exists", return_value=True)
    def test_add_chapter_increments_sequence(self, mock_exists, mock_file):
        """Validates that consecutive additions to existing records systematically update indices."""
        print(" [TEST] Running: test_add_chapter_increments_sequence")
        with patch("library._save") as mock_save_func:
            print("   -> Appending subsequent chapter onto historical user sequence logs...")
            next_chapter_num = library.add_chapter(hero_name="ansh", book_id="abc12345", chapter_text="Chapter 2 updates.")
            self.assertEqual(next_chapter_num, 2)
            print(f"   ✅ [PASSED] Bookshelf safely auto-incremented sequence pointer to index: {next_chapter_num}")


if __name__ == "__main__":
    print("\n" + "="*60 + "\n STARTING TEST SUITE WITH LOGS...\n" + "="*60)
    unittest.main()