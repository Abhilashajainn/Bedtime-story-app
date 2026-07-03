from dataclasses import dataclass
from pipeline import generate_personalized_story


# ----------------------------
# Hero profile class
# ----------------------------
@dataclass
class HeroProfile:
    name: str
    traits: list
    favorites: list
    supporting_cast: list


TEST_CASES = [
    {
        "name": "5-7 Adventure (Ocean)",
        "profile": HeroProfile("Aarvi", ["Brave", "Creative"], ["Ocean"], ["Mom"]),
        "story_type": "adventure",
        "lesson": "kindness",
        "magic": None,
        "length": "short",
        "age": "5-7"
    },
    {
        "name": "5-7 Magical World",
        "profile": HeroProfile("Emma", ["Curious"], ["Magic", "Animals"], []),
        "story_type": "magical_world",
        "lesson": "courage",
        "magic": "A glowing unicorn appears",
        "length": "short",
        "age": "5-7"
    },
    {
        "name": "8-10 Space Adventure",
        "profile": HeroProfile("Sophia", ["Brave", "Curious"], ["Space", "Robots"], ["Robot Buddy"]),
        "story_type": "adventure",
        "lesson": "friendship",
        "magic": None,
        "length": "medium",
        "age": "8-10"
    }
]


def run_tests():
    print("\n" + "=" * 60)
    print("🚀 BEDTIME STORY TEST RUNNER 🚀")
    print("=" * 60)

    total = len(TEST_CASES)
    passed = 0

    for i, t in enumerate(TEST_CASES, 1):
        print(f"\n🧪 TEST {i}/{total}: {t['name']}")
        print("-" * 60)

        result = generate_personalized_story(
            profile=t["profile"],
            story_type=t["story_type"],
            lesson=t["lesson"],
            magic_twist=t["magic"],
            length_key=t["length"],
            age_group=t["age"],
        )

        # simple pass logic (you can change threshold if needed)
        is_pass = result.final_score >= 8

        if is_pass:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"{status}")
        print(f"📂 Category   : {t['story_type']}")
        print(f"🔁 Revisions   : {result.revisions}")
        print(f"📊 Final Score : {result.final_score}/10")

        print("\n📖 Story Preview:")
        print("-" * 60)
        print(result.story[:500])
        print("-" * 60)

    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {total - passed}")
    print(f"Success Rate: {round((passed/total)*100, 1)}%")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()