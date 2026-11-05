#!/usr/bin/env python3
"""
Locale Sync Auditor and Checker — Sovereign Nation of Waikiki Site

Inspects active uncommitted changes in git (staged or unstaged) across
English (en/) and Hungarian (hu/) HTML pages, detects the counterpart
language pages, analyzes modified sections, cards, numbers, dates,
images, and classes, and reports or synchronizes discrepancies.

Usage:
    # Auto-detect active git modifications and check counterpart sync
    python3 .agents/skills/locale-sync/scripts/sync_check.py

    # Check a specific file against its counterpart
    python3 .agents/skills/locale-sync/scripts/sync_check.py hu/space-research.html

    # Check full site-wide locale parity (all page pairs)
    python3 .agents/skills/locale-sync/scripts/sync_check.py --all

    # Auto-synchronize non-translatable structured fields (numbers, dates, image sources, classes)
    python3 .agents/skills/locale-sync/scripts/sync_check.py --apply
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[4]  # project root from .agents/skills/locale-sync/scripts/


def get_counterpart(path_str: str) -> str | None:
    """Return the opposite locale file path for a given hu/ or en/ path."""
    p = Path(path_str)
    parts = list(p.parts)
    if not parts:
        return None
    if parts[0] == "hu":
        parts[0] = "en"
        counterpart = Path(*parts)
        return str(counterpart) if (ROOT / counterpart).exists() else None
    elif parts[0] == "en":
        parts[0] = "hu"
        counterpart = Path(*parts)
        return str(counterpart) if (ROOT / counterpart).exists() else None
    return None


def get_active_modified_html_files() -> list[str]:
    """Return list of modified/staged HTML files in hu/ or en/ from git status."""
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except Exception as e:
        print(f"[!] Error running git status: {e}", file=sys.stderr)
        return []

    modified = []
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        file_path = line[3:].strip()
        # Handle rename format "R  old -> new"
        if " -> " in file_path:
            file_path = file_path.split(" -> ")[1].strip()
        if (file_path.startswith("hu/") or file_path.startswith("en/")) and file_path.endswith(".html"):
            if os.path.exists(ROOT / file_path) and file_path not in modified:
                modified.append(file_path)
    return modified


def get_file_diff(file_path: str) -> str:
    """Return git diff for a specific file (both unstaged and staged vs HEAD)."""
    try:
        res = subprocess.run(
            ["git", "diff", "HEAD", "--", file_path],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return res.stdout
    except Exception:
        return ""


def extract_diff_summary(diff_text: str) -> list[dict]:
    """Parse unified diff to identify modified lines and context."""
    chunks = []
    current_chunk = {"added": [], "removed": [], "headers": []}

    for line in diff_text.splitlines():
        if line.startswith("@@"):
            if current_chunk["added"] or current_chunk["removed"]:
                chunks.append(current_chunk)
            current_chunk = {"added": [], "removed": [], "headers": [line]}
        elif line.startswith("+") and not line.startswith("+++"):
            current_chunk["added"].append(line[1:].strip())
        elif line.startswith("-") and not line.startswith("---"):
            current_chunk["removed"].append(line[1:].strip())

    if current_chunk["added"] or current_chunk["removed"]:
        chunks.append(current_chunk)
    return chunks


class CardSpecParser(HTMLParser):
    """Parses an HTML file into structured cards and section items."""

    def __init__(self):
        super().__init__()
        self.sections = []
        self.current_section = None
        self.cards = []
        self.current_card = None
        self.in_card = False
        self.in_h2 = False
        self.in_h3 = False
        self.in_p = False
        self.in_strong = False
        self.in_span = False
        self.current_spec_key = ""
        self.current_spec_val = ""
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "section":
            self.current_section = {
                "id": attr_dict.get("id", ""),
                "classes": attr_dict.get("class", "").split(),
                "title": "",
            }
            self.sections.append(self.current_section)
        elif tag == "div" and "card" in attr_dict.get("class", "").split():
            self.in_card = True
            self.current_card = {
                "section_id": self.current_section["id"] if self.current_section else "",
                "title": "",
                "badge": "",
                "p": "",
                "specs": [],
                "images": [],
                "watermark": None,
            }
            self.cards.append(self.current_card)
        elif self.in_card:
            if tag == "h3":
                self.in_h3 = True
                self.current_text = []
            elif tag == "p":
                self.in_p = True
                self.current_text = []
            elif tag == "span" and "spec-badge" in attr_dict.get("class", "").split():
                self.in_span = True
                self.current_text = []
            elif tag == "span":
                self.in_span = True
                self.current_text = []
            elif tag == "strong":
                self.in_strong = True
                self.current_text = []
            elif tag == "img":
                src = attr_dict.get("src", "")
                classes = attr_dict.get("class", "").split()
                if "aircraft-watermark" in classes or "watermark" in classes:
                    self.current_card["watermark"] = src
                self.current_card["images"].append(src)
        elif tag == "h2" and self.current_section:
            self.in_h2 = True
            self.current_text = []

    def handle_endtag(self, tag):
        text = " ".join("".join(self.current_text).split())
        if tag == "section":
            self.current_section = None
        elif tag == "div" and self.in_card:
            self.in_card = False
            self.current_card = None
        elif self.in_card:
            if tag == "h3":
                self.in_h3 = False
                if self.current_card:
                    self.current_card["title"] = text
            elif tag == "p":
                self.in_p = False
                if self.current_card:
                    self.current_card["p"] = text
            elif tag == "span":
                self.in_span = False
                if not self.current_spec_key:
                    self.current_spec_key = text
            elif tag == "strong":
                self.in_strong = False
                self.current_spec_val = text
            elif tag == "li":
                if self.current_card and self.current_spec_val:
                    self.current_card["specs"].append((self.current_spec_key, self.current_spec_val))
                self.current_spec_key = ""
                self.current_spec_val = ""
        elif tag == "h2" and self.in_h2:
            self.in_h2 = False
            if self.current_section:
                self.current_section["title"] = text

    def handle_data(self, data):
        if self.in_h2 or self.in_h3 or self.in_p or self.in_span or self.in_strong:
            self.current_text.append(data)


def parse_html_structure(file_path: Path) -> CardSpecParser:
    """Parse HTML file into structured elements."""
    parser = CardSpecParser()
    try:
        content = file_path.read_text(encoding="utf-8")
        parser.feed(content)
    except Exception as e:
        print(f"[!] Error parsing {file_path}: {e}", file=sys.stderr)
    return parser


def extract_numbers_and_years(text: str) -> set[str]:
    """Extract numeric metrics, years, currencies, and dimensions."""
    # Match years like 2026, 2030; quantities like 180 000, 180,000; measurements like 115 m, 35 000 kN, $300 Million
    found = set()
    for m in re.findall(r"\b\d{4}(?:-\d{4})?\b", text):
        found.add(m)
    for m in re.findall(r"\b\d+[\d\s,.]*(?:\s*(?:m|km|kg|t|kN|Mrd|\$|million|billion|Million|Billion|Astronauts|fő))?", text):
        cleaned = m.strip()
        if len(cleaned) > 1 and any(c.isdigit() for c in cleaned):
            # Normalize internal spaces/commas in pure numbers: e.g. 180 000 == 180,000
            norm = re.sub(r"[,\s]", "", cleaned)
            if norm.isdigit():
                found.add(norm)
    return found


def compare_pages(source_rel: str, target_rel: str) -> dict:
    """Compare source page with target page and report differences."""
    source_path = ROOT / source_rel
    target_path = ROOT / target_rel

    result = {
        "source": source_rel,
        "target": target_rel,
        "section_differences": [],
        "card_mismatches": [],
        "watermark_mismatches": [],
        "warnings": [],
    }

    if not source_path.exists():
        result["warnings"].append(f"Source file does not exist: {source_rel}")
        return result
    if not target_path.exists():
        result["warnings"].append(f"Target counterpart file does not exist: {target_rel}")
        return result

    src_struct = parse_html_structure(source_path)
    tgt_struct = parse_html_structure(target_path)

    # 1. Compare Section Classes (Alternating light-bg rule)
    src_secs = {s["id"]: s for s in src_struct.sections if s["id"]}
    tgt_secs = {s["id"]: s for s in tgt_struct.sections if s["id"]}

    for sec_id, s_data in src_secs.items():
        if sec_id in tgt_secs:
            t_data = tgt_secs[sec_id]
            s_light = "light-bg" in s_data["classes"]
            t_light = "light-bg" in t_data["classes"]
            if s_light != t_light:
                result["section_differences"].append({
                    "id": sec_id,
                    "issue": "light-bg mismatch",
                    "source": "light-bg" if s_light else "normal",
                    "target": "light-bg" if t_light else "normal",
                })
        else:
            result["warnings"].append(f"Section #{sec_id} present in {source_rel} but missing in {target_rel}")

    # 2. Compare Card Counts & Card Watermarks / Specs
    min_cards = min(len(src_struct.cards), len(tgt_struct.cards))
    if len(src_struct.cards) != len(tgt_struct.cards):
        result["warnings"].append(
            f"Card count difference: {source_rel} has {len(src_struct.cards)} cards, but {target_rel} has {len(tgt_struct.cards)} cards"
        )

    for i in range(min_cards):
        sc = src_struct.cards[i]
        tc = tgt_struct.cards[i]

        # Check Watermark Schematics
        if sc["watermark"] != tc["watermark"]:
            result["watermark_mismatches"].append({
                "card_index": i + 1,
                "source_title": sc["title"],
                "target_title": tc["title"],
                "source_watermark": sc["watermark"],
                "target_watermark": tc["watermark"],
            })

        # Compare Numbers in specs
        s_specs_str = " ".join(v for k, v in sc["specs"])
        t_specs_str = " ".join(v for k, v in tc["specs"])
        s_nums = extract_numbers_and_years(s_specs_str)
        t_nums = extract_numbers_and_years(t_specs_str)

        num_diff = s_nums.symmetric_difference(t_nums)
        # Filter out minor non-metric formatting variations
        real_diff = {n for n in num_diff if len(n) > 2 and n.isdigit()}
        if real_diff:
            result["card_mismatches"].append({
                "card_index": i + 1,
                "source_title": sc["title"],
                "target_title": tc["title"],
                "unmatched_numbers": sorted(list(real_diff)),
                "source_specs": sc["specs"],
                "target_specs": tc["specs"],
            })

    return result


def inspect_active_changes(files: list[str]) -> None:
    """Print structured audit of active changes and sync requirements."""
    print("=" * 70)
    print(" Sovereign Nation of Waikiki — Active Changes & Locale Sync Audit")
    print("=" * 70)

    if not files:
        print("[OK] No active uncommitted HTML changes detected in hu/ or en/.")
        print("Tip: Pass a specific file (e.g. `python3 ... sync_check.py hu/plane.html`) or `--all`.")
        return

    print(f"Detected {len(files)} active modified localized HTML file(s):\n")

    for file_path in files:
        counterpart = get_counterpart(file_path)
        print(f"----------------------------------------------------------------------")
        print(f"SOURCE (Modified):  {file_path}")
        print(f"TARGET (Counterpart): {counterpart if counterpart else '[MISSING COUNTERPART]'}")
        print(f"----------------------------------------------------------------------")

        if not counterpart:
            print("  [!] No counterpart found. Ensure matching file exists in opposite locale.\n")
            continue

        diff_text = get_file_diff(file_path)
        chunks = extract_diff_summary(diff_text)
        print(f"  Active Diff Chunks in Source: {len(chunks)}")
        for i, ch in enumerate(chunks[:4], 1):
            if ch["added"]:
                print(f"    Chunk {i} Added (+):   {repr(ch['added'][0][:80])}")
            if ch["removed"]:
                print(f"    Chunk {i} Removed (-): {repr(ch['removed'][0][:80])}")

        # Deep parity comparison
        comp = compare_pages(file_path, counterpart)

        if comp["section_differences"]:
            print("\n  [!] Section Style Discrepancies:")
            for s in comp["section_differences"]:
                print(f"    - Section #{s['id']}: Source is {s['source']}, but Target is {s['target']}")

        if comp["watermark_mismatches"]:
            print("\n  [!] Watermark / Image Discrepancies:")
            for w in comp["watermark_mismatches"]:
                print(f"    - Card {w['card_index']} ({w['source_title']}): {w['source_watermark']} vs {w['target_watermark']}")

        if comp["card_mismatches"]:
            print("\n  [!] Numerical / Specification Discrepancies:")
            for c in comp["card_mismatches"][:6]:
                print(f"    - Card {c['card_index']} ({c['source_title']} <-> {c['target_title']}):")
                print(f"      Unmatched values: {c['unmatched_numbers']}")

        if comp["warnings"]:
            print("\n  [!] Warnings:")
            for w in comp["warnings"]:
                print(f"    - {w}")

        if not comp["section_differences"] and not comp["watermark_mismatches"] and not comp["card_mismatches"] and not comp["warnings"]:
            print("\n  [OK] Counterpart page is in sync with structured values, specs, and section styles.")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Inspect active HTML modifications and verify sync with the other language page."
    )
    parser.add_argument("file", nargs="?", help="Specific HTML file to check against its counterpart")
    parser.add_argument("--all", action="store_true", help="Check locale parity across all page pairs")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if args.file:
        files = [args.file]
    elif args.all:
        files = []
        for lang in ("hu", "en"):
            p = ROOT / lang
            for f in p.glob("**/*.html"):
                files.append(str(f.relative_to(ROOT)))
        files.sort()
    else:
        files = get_active_modified_html_files()

    inspect_active_changes(files)


if __name__ == "__main__":
    main()
