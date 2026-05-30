"""
fix_folder_names.py
───────────────────
Renames folders in my-solutions/ so they always use the correct
LeetCode *frontend* problem number (the one shown on the website).

The LeetCode sync tool sometimes writes the internal backend ID instead,
e.g.  1580-shuffle-the-array  →  should be  1470-shuffle-the-array

Run once to fix existing folders:
    python scripts/fix_folder_names.py

Also called automatically in the GitHub Actions workflow after every
LeetCode sync, before update_readme.py runs.
"""

import json
import re
import time
import requests
from pathlib import Path

ROOT      = Path(__file__).parent.parent
SOLUTIONS = ROOT / "my-solutions"
CACHE     = Path(__file__).parent / "leetcode_cache.json"


# ── Cache helpers ─────────────────────────────────────────────────────────────
def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}

def save_cache(cache: dict):
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


# ── LeetCode API ──────────────────────────────────────────────────────────────
def fetch_frontend_id(slug: str) -> int | None:
    """Returns the correct frontend problem number for a given slug."""
    query = """
    query($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
      }
    }
    """
    try:
        resp = requests.post(
            "https://leetcode.com/graphql",
            json={"query": query, "variables": {"titleSlug": slug}},
            headers={"Content-Type": "application/json",
                     "Referer": "https://leetcode.com"},
            timeout=12,
        )
        resp.raise_for_status()
        fid = resp.json()["data"]["question"]["questionFrontendId"]
        return int(fid)
    except Exception as exc:
        print(f"  ⚠  Could not fetch frontend ID for '{slug}': {exc}")
        return None


def get_frontend_id(slug: str, cache: dict) -> int | None:
    key = f"fid:{slug}"
    if key not in cache:
        print(f"  → Fetching frontend ID: {slug}")
        fid = fetch_frontend_id(slug)
        if fid is not None:
            cache[key] = fid
            # Also store in the format update_readme.py expects
            if slug in cache and isinstance(cache[slug], dict):
                cache[slug]["num"] = fid
        time.sleep(0.4)
    return cache.get(key)


# ── Folder name parsing ───────────────────────────────────────────────────────
def parse_folder(name: str) -> tuple[int | None, str] | None:
    """
    Returns (current_num_or_None, slug), or None if not a solution folder.

    Handles:
      0001-two-sum           →  (1,    "two-sum")
      1580-shuffle-the-array →  (1580, "shuffle-the-array")   ← wrong number
      987654321_two-sum      →  (None, "two-sum")             ← submission ID
    """
    # Standard NNNN-slug format
    m = re.match(r"^(\d{1,5})-(.+)$", name)
    if m:
        return int(m.group(1)), m.group(2)

    # Submission-ID_slug format (6+ digits before underscore)
    m = re.match(r"^\d{6,}_(.+)$", name)
    if m:
        return None, m.group(1)

    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    cache   = load_cache()
    renamed = 0
    skipped = 0
    errors  = 0

    print("🔍 Checking folder names in my-solutions/ ...")

    for folder in sorted(SOLUTIONS.iterdir()):
        if not folder.is_dir():
            continue

        parsed = parse_folder(folder.name)
        if parsed is None:
            continue

        current_num, slug = parsed
        correct_num = get_frontend_id(slug, cache)

        if correct_num is None:
            print(f"  ✗ Could not determine correct number for: {folder.name}")
            errors += 1
            continue

        correct_name = f"{correct_num:04d}-{slug}"

        if folder.name == correct_name:
            skipped += 1
            continue

        new_path = SOLUTIONS / correct_name

        if new_path.exists():
            print(f"  ⚠  Target already exists, skipping: {correct_name}")
            errors += 1
            continue

        folder.rename(new_path)
        print(f"  ✅ Renamed: {folder.name}  →  {correct_name}")
        renamed += 1

    save_cache(cache)
    print(f"\nDone — {renamed} renamed, {skipped} already correct, {errors} errors.")


if __name__ == "__main__":
    main()
