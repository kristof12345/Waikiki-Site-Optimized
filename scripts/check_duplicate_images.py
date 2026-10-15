#!/usr/bin/env python3
"""Check for duplicate JPG images across HTML files."""

import os
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html_files = sorted(ROOT.rglob("*.html"))

all_images = []
duplicates_across_site = Counter()

for html_file in html_files:
    # Exclude node_modules or .git if present
    if any(p in html_file.parts for p in ("node_modules", ".git")):
        continue

    try:
        content = html_file.read_text(encoding="utf-8")
    except Exception:
        continue

    # Find all image src attributes ending in .jpg or .jpeg
    raw_matches = re.findall(r'<img[^>]+src="([^"]+)"', content)
    matches = [src for src in raw_matches if src.lower().split("?")[0].endswith((".jpg", ".jpeg"))]

    # Check for duplicates within this specific file
    counts = Counter(matches)
    duplicates_in_file = {src: count for src, count in counts.items() if count > 1}

    if duplicates_in_file:
        print(f"Duplicates in {html_file.relative_to(ROOT)}:")
        for src, count in duplicates_in_file.items():
            print(f"  - {src} (used {count} times)")

    # Add to global counter
    duplicates_across_site.update(matches)

# Check global duplicates
global_dupes = {src: count for src, count in duplicates_across_site.items() if count > 1}
print(f"\nTotal JPG images used across all HTML files: {len(duplicates_across_site)}")
print(f"Total unique JPG images used more than once across the entire site: {len(global_dupes)}")
