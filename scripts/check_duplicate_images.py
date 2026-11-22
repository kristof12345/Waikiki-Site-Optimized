#!/usr/bin/env python3
"""Check for duplicate JPG images within and across HTML files in hu/."""

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = ROOT / "hu"
html_files = sorted(TARGET_DIR.rglob("*.html"))


def normalize_src(html_file: Path, src: str) -> str:
    """Resolve relative image paths to a repo-relative path for accurate cross-page matching."""
    clean = src.split("?")[0].split("#")[0]
    if clean.startswith(("http://", "https://", "data:", "/")):
        return clean
    try:
        resolved = (html_file.parent / clean).resolve()
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return clean


# image_usage[normalized_img][rel_html_path] = count
image_usage: dict[str, dict[str, int]] = defaultdict(dict)
duplicates_across_hu = Counter()

for html_file in html_files:
    try:
        content = html_file.read_text(encoding="utf-8")
    except Exception:
        continue

    rel_file = html_file.relative_to(ROOT).as_posix()

    # Skip next-media containers
    filtered_content = re.sub(r'<div[^>]+class="[^"]*\bnext-media\b[^"]*"[^>]*>.*?</div>', "", content, flags=re.S)

    # Find all image src attributes ending in .jpg or .jpeg
    raw_matches = re.findall(r'<img[^>]+src="([^"]+)"', filtered_content)
    matches = [
        normalize_src(html_file, src)
        for src in raw_matches
        if src.lower().split("?")[0].endswith((".jpg", ".jpeg"))
    ]

    # Check for duplicates within this specific file
    counts = Counter(matches)
    duplicates_in_file = {src: count for src, count in counts.items() if count > 1}

    if duplicates_in_file:
        print(f"Duplicates in {rel_file}:")
        for src, count in duplicates_in_file.items():
            print(f"  - {src} (used {count} times)")

    # Record usage across hu/
    for src, count in counts.items():
        image_usage[src][rel_file] = count
    duplicates_across_hu.update(matches)

# Check cross-page duplicates in hu/
cross_page = {
    src: pages
    for src, pages in sorted(image_usage.items())
    if len(pages) > 1
}
print(f"\nCross-page duplicates in 'hu/' ({len(cross_page)} images):")
if not cross_page:
    print("  (none)")
else:
    for src, pages in cross_page.items():
        total_uses = sum(pages.values())
        print(f"  - {src} (used {total_uses} times)")
        for p, c in sorted(pages.items()):
            suffix = f" ({c} times)" if c > 1 else ""
            print(f"      - {p}{suffix}")

# Summary
global_dupes = {src: count for src, count in duplicates_across_hu.items() if count > 1}
print(f"\nTotal unique JPG images used in hu/: {len(duplicates_across_hu)}")
print(f"Total unique JPG images used more than once in hu/: {len(global_dupes)}")
