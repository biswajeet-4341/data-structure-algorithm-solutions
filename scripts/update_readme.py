"""
Auto-updates README.md Problem Index and Progress Table
by scanning my-solutions/ and querying LeetCode's API.

- Run manually : python scripts/update_readme.py
- Run via CI   : triggered automatically by GitHub Actions on every push
"""

import os
import json
import re
import time
import requests
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.parent
SOLUTIONS    = ROOT / "my-solutions"
README       = ROOT / "README.md"
CACHE_FILE   = Path(__file__).parent / "leetcode_cache.json"

# ── Language detection (add more extensions if needed) ────────────────────────
LANG_MAP = {
    ".c"    : "C",
    ".js"   : "JavaScript",
    ".py"   : "Python",
    ".cpp"  : "C++",
    ".java" : "Java",
    ".ts"   : "TypeScript",
    ".go"   : "Go",
    ".rs"   : "Rust",
}

# ── LeetCode tag → display category ───────────────────────────────────────────
# First matching tag wins, so order matters.
TAG_CATEGORY = [
    (["Linked List"],                           "Linked Lists"),
    (["Tree", "Binary Tree", "Binary Search Tree"], "Trees"),
    (["Graph", "Topological Sort"],             "Graphs"),
    (["Dynamic Programming"],                   "Dynamic Programming"),
    (["Backtracking"],                          "Backtracking"),
    (["Sliding Window"],                        "Sliding Window"),
    (["Two Pointers"],                          "Two Pointers"),
    (["Binary Search"],                         "Binary Search"),
    (["Stack"],                                 "Stack & Queue"),
    (["Queue", "Monotonic Queue"],              "Stack & Queue"),
    (["Heap (Priority Queue)"],                 "Heap / Priority Queue"),
    (["Greedy"],                                "Greedy"),
    (["Bit Manipulation"],                      "Bit Manipulation"),
    (["Math", "Geometry", "Number Theory"],     "Math & Geometry"),
    (["Array", "String", "Hash Table", "Sorting", "Matrix"], "Arrays & Strings"),
]

DIFF_ICON = {"Easy": "🟩", "Medium": "🟨", "Hard": "🟥"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_problem(slug: str) -> dict | None:
    """Query LeetCode GraphQL for title, difficulty, and topic tags."""
    query = """
    query($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        title
        difficulty
        topicTags { name }
      }
    }
    """
    try:
        resp = requests.post(
            "https://leetcode.com/graphql",
            json={"query": query, "variables": {"titleSlug": slug}},
            headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
            timeout=12,
        )
        resp.raise_for_status()
        q = resp.json()["data"]["question"]
        return {
            "title":      q["title"],
            "difficulty": q["difficulty"],
            "tags":       [t["name"] for t in q["topicTags"]],
        }
    except Exception as exc:
        print(f"  ⚠  Could not fetch '{slug}': {exc}")
        return None


def get_problem_info(slug: str, cache: dict) -> dict | None:
    if slug not in cache:
        print(f"  → Fetching: {slug}")
        info = fetch_problem(slug)
        if info:
            cache[slug] = info
        time.sleep(0.4)          # be polite to LC servers
    return cache.get(slug)


def detect_languages(folder: Path) -> str:
    langs = []
    for f in folder.iterdir():
        lang = LANG_MAP.get(f.suffix.lower())
        if lang and lang not in langs:
            langs.append(lang)
    return ", ".join(langs) if langs else "Unknown"


def map_category(tags: list[str]) -> str:
    for keys, label in TAG_CATEGORY:
        if any(t in keys for t in tags):
            return label
    return "Other"


# ── Section generators ────────────────────────────────────────────────────────

def build_index(by_cat: dict) -> str:
    lines = []
    for cat in sorted(by_cat):
        lines.append(f"\n### {cat}\n")
        for p in sorted(by_cat[cat], key=lambda x: x["num"]):
            icon = DIFF_ICON.get(p["difficulty"], "⬜")
            lines.append(
                f"- [{p['num']:04d}. {p['title']}]({p['url']}) "
                f"*({p['lang']})* — {icon} {p['difficulty']}"
            )
    return "\n".join(lines)


def build_table(by_cat: dict) -> str:
    rows = [
        "\n| Topic | Solved | 🟩 Easy | 🟨 Medium | 🟥 Hard |",
          "| ----- | :----: | :-----: | :-------: | :-----: |",
    ]
    totals = [0, 0, 0, 0]
    for cat in sorted(by_cat):
        probs = by_cat[cat]
        e = sum(1 for p in probs if p["difficulty"] == "Easy")
        m = sum(1 for p in probs if p["difficulty"] == "Medium")
        h = sum(1 for p in probs if p["difficulty"] == "Hard")
        s = len(probs)
        rows.append(f"| {cat} | {s} | {e} | {m} | {h} |")
        for i, v in enumerate([s, e, m, h]):
            totals[i] += v
    rows.append(f"| **Total** | **{totals[0]}** | **{totals[1]}** | **{totals[2]}** | **{totals[3]}** |")
    return "\n".join(rows)


# ── README writer ─────────────────────────────────────────────────────────────

def inject_section(readme: str, marker: str, content: str) -> str:
    start = f"<!-- {marker}_START -->"
    end   = f"<!-- {marker}_END -->"
    pattern = rf"{re.escape(start)}.*?{re.escape(end)}"
    replacement = f"{start}{content}\n{end}"
    updated, n = re.subn(pattern, replacement, readme, flags=re.DOTALL)
    if n == 0:
        print(f"  ⚠  Marker '{marker}' not found in README — section skipped.")
    return updated


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("📂 Scanning my-solutions/ ...")
    cache    = load_cache()
    by_cat: dict = {}

    for folder in sorted(SOLUTIONS.iterdir()):
        if not folder.is_dir():
            continue
        m = re.match(r"^(\d+)-(.+)$", folder.name)
        if not m:
            continue

        num  = int(m.group(1))
        slug = m.group(2)
        lang = detect_languages(folder)
        info = get_problem_info(slug, cache)

        if not info:
            continue

        cat = map_category(info["tags"])
        by_cat.setdefault(cat, []).append({
            "num":        num,
            "title":      info["title"],
            "difficulty": info["difficulty"],
            "lang":       lang,
            "url":        f"./my-solutions/{folder.name}",
        })

    save_cache(cache)
    print(f"✅ {sum(len(v) for v in by_cat.values())} problems across {len(by_cat)} categories.")

    print("📝 Updating README.md ...")
    readme = README.read_text(encoding="utf-8")
    readme = inject_section(readme, "PROBLEM_INDEX", build_index(by_cat))
    readme = inject_section(readme, "PROGRESS_TABLE", build_table(by_cat))
    README.write_text(readme, encoding="utf-8")
    print("✅ Done!")


if __name__ == "__main__":
    main()
