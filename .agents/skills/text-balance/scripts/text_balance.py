#!/usr/bin/env python3
"""
Component Text Length & Line Count Balance Auditor — Sovereign Nation of Waikiki Site
Part of the 'text-balance' skill.

Analyzes text lengths and rendered line counts of sibling components (e.g. card descriptions
within section rows), detects vertical height imbalances, and provides target line count
recommendations to harmonize visual rhythm.

Usage:
    # Check text balance on a specific page (static estimation)
    python3 .agents/skills/text-balance/scripts/text_balance.py hu/space-research.html

    # Check with live browser rendering (via headless Chrome for exact pixel line counts)
    python3 .agents/skills/text-balance/scripts/text_balance.py --browser hu/space-research.html

    # Check text balance across all pages
    python3 .agents/skills/text-balance/scripts/text_balance.py --all

    # Show only imbalanced sections
    python3 .agents/skills/text-balance/scripts/text_balance.py --imbalanced hu/plane.html
"""

from __future__ import annotations

import argparse
import html.parser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class ComponentParser(html.parser.HTMLParser):
    """Parses HTML into sections and card components."""

    def __init__(self):
        super().__init__()
        self.sections = []
        self.current_sec = None
        self.in_card = False
        self.in_h3 = False
        self.in_p = False
        self.in_spec_list = False
        self.cur_title = []
        self.cur_p = []
        self.cur_specs_count = 0

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get("class", "").split()

        is_card = tag in ("div", "article", "li") and any(
            cls == "card" or cls.endswith("-card") or cls.startswith("card-") for cls in classes
        )

        if tag == "section":
            self.current_sec = {
                "id": attr_dict.get("id", attr_dict.get("class", "section").split()[0] if attr_dict.get("class") else "section"),
                "title": "",
                "cards": [],
            }
            self.sections.append(self.current_sec)
        elif is_card:
            self.in_card = True
            self.cur_card_tag = tag
            self.cur_title = []
            self.cur_p = []
            self.cur_specs_count = 0
        elif self.in_card:
            if tag in ("h2", "h3", "h4") or "title" in attr_dict.get("class", ""):
                self.in_h3 = True
            elif tag == "p":
                self.in_p = True
            elif tag in ("ul", "ol") and "spec-list" in classes:
                self.in_spec_list = True
            elif tag == "li" and self.in_spec_list:
                self.cur_specs_count += 1

    def handle_endtag(self, tag):
        if tag == "section":
            self.current_sec = None
        elif self.in_card and tag == getattr(self, "cur_card_tag", "div"):
            self.in_card = False
            if self.current_sec:
                title = " ".join("".join(self.cur_title).split())
                p_text = " ".join("".join(self.cur_p).split())
                if p_text:  # only track cards with descriptive prose
                    self.current_sec["cards"].append({
                        "title": title or "(Untitled Card)",
                        "text": p_text,
                        "char_count": len(p_text),
                        "word_count": len(p_text.split()) if p_text else 0,
                        "spec_count": self.cur_specs_count,
                    })
        elif tag in ("h2", "h3", "h4") and self.in_h3:
            self.in_h3 = False
        elif tag == "p" and self.in_p:
            self.in_p = False
        elif tag in ("ul", "ol") and self.in_spec_list:
            self.in_spec_list = False

    def handle_data(self, data):
        if self.in_h3:
            self.cur_title.append(data)
        elif self.in_p:
            self.cur_p.append(data)


def estimate_line_count(char_count: int, num_cards: int) -> int:
    """
    Estimates rendered lines in a responsive desktop grid.
    In standard Waikiki card grids:
      - 3+ cards in a section render in a 3-column grid (~50-54 chars per line).
      - 2 cards render in a 2-column grid (~75-85 chars per line).
      - 1 card renders full width (~110-120 chars per line).
    """
    if char_count == 0:
        return 0
    chars_per_line = 52 if num_cards >= 3 else (80 if num_cards == 2 else 115)
    return max(1, round(char_count / chars_per_line))


VIEWPORT_WIDTH = 2560
VIEWPORT_HEIGHT = 1440


def measure_with_browser(file_path: Path, width: int = VIEWPORT_WIDTH, height: int = VIEWPORT_HEIGHT) -> dict[str, list[dict]] | None:
    """Uses headless Google Chrome to measure exact computed line heights and line counts at specified viewport width (default 2560px)."""
    if not os.path.exists(CHROME_PATH):
        return None

    content = file_path.read_text(encoding="utf-8", errors="ignore")

    # Layout probe script that computes exact rendered line count
    probe_script = f"""
    <script id="text-balance-probe">
    window.addEventListener('DOMContentLoaded', () => {{
        setTimeout(() => {{
            const results = {{}};
            document.querySelectorAll('section').forEach(sec => {{
                const secId = sec.id || 'sec';
                const cards = sec.querySelectorAll('.card, [class*="-card"], [class*="card-"]');
                if (cards.length > 1) {{
                    const cardList = [];
                    cards.forEach((c, idx) => {{
                        const h3 = c.querySelector('h2, h3, h4, [class*="title"]');
                        const p = c.querySelector('p');
                        if (p) {{
                            let lines = 0;
                            try {{
                                const range = document.createRange();
                                range.selectNodeContents(p);
                                const rects = range.getClientRects();
                                if (rects && rects.length > 0) lines = rects.length;
                            }} catch (e) {{}}
                            if (!lines || lines <= 1) {{
                                const cs = window.getComputedStyle(p);
                                const lh = parseFloat(cs.lineHeight) || 24;
                                lines = Math.round(p.offsetHeight / lh);
                            }}
                            cardList.push({{
                                index: idx + 1,
                                title: h3 ? h3.innerText.trim() : '',
                                lines: Math.max(1, lines),
                                height: p.offsetHeight,
                                chars: p.innerText.trim().length
                            }});
                        }}
                    }});
                    if (cardList.length > 1) results[secId] = cardList;
                }}
            }});
            const out = document.createElement('pre');
            out.id = 'text-balance-results';
            out.textContent = JSON.stringify(results);
            document.body.appendChild(out);
        }}, 500);
    }});
    </script>
    """

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False, dir=str(file_path.parent)) as tf:
        if "</body>" in content:
            temp_content = content.replace("</body>", probe_script + "</body>")
        else:
            temp_content = content + probe_script
        tf.write(temp_content)
        temp_file_path = tf.name

    try:
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            f"--window-size={width},{height}",
            "--virtual-time-budget=2000",
            "--dump-dom",
            f"file://{temp_file_path}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0 and "text-balance-results" in res.stdout:
            match = re.search(r'<pre id="text-balance-results">([\s\S]*?)</pre>', res.stdout)
            if match:
                return json.loads(match.group(1))
    except Exception:
        pass
    finally:
        try:
            os.remove(temp_file_path)
        except OSError:
            pass

    return None


def audit_file(file_path: Path, use_browser: bool = False, only_imbalanced: bool = False, width: int = VIEWPORT_WIDTH) -> int:
    parser = ComponentParser()
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        parser.feed(content)
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}", file=sys.stderr)
        return 0

    browser_data = measure_with_browser(file_path, width=width) if use_browser else None

    imbalanced_sections = 0
    total_sections_checked = 0

    print(f"\nAnalyzing: {file_path.name}")
    print("=" * 70)

    for sec in parser.sections:
        cards = sec["cards"]
        if len(cards) <= 1:
            continue

        total_sections_checked += 1
        sec_id = sec["id"]

        # Check if browser data is available for this section
        b_cards = browser_data.get(sec_id) if browser_data else None

        items = []
        for idx, c in enumerate(cards):
            title = c["title"]
            chars = c["char_count"]
            words = c["word_count"]

            if b_cards and idx < len(b_cards):
                lines = b_cards[idx]["lines"]
            else:
                lines = estimate_line_count(chars, len(cards))

            items.append({
                "index": idx + 1,
                "title": title,
                "text": c["text"],
                "chars": chars,
                "words": words,
                "lines": lines,
            })

        if not items:
            continue

        line_counts = [item["lines"] for item in items]
        min_lines = min(line_counts)
        max_lines = max(line_counts)
        avg_lines = sum(line_counts) / len(line_counts)
        line_variance = max_lines - min_lines

        # Criteria: variance >= 2 lines is considered imbalanced for peer cards
        is_imbalanced = line_variance >= 2

        if is_imbalanced:
            imbalanced_sections += 1

        if only_imbalanced and not is_imbalanced:
            continue

        status_tag = "[IMBALANCED]" if is_imbalanced else "[BALANCED]"
        mode_tag = "(Live Browser Render)" if b_cards else "(Estimated Desktop Lines)"
        print(f"\nSection #{sec_id} {status_tag} — {len(cards)} Cards {mode_tag}")
        print(f"Spread: {min_lines} to {max_lines} lines (Variance: {line_variance} line{'s' if line_variance != 1 else ''}, Avg: {avg_lines:.1f} lines)")
        print("-" * 70)

        target_lines = round(avg_lines)
        target_chars_min = max(50, (target_lines - 1) * 52)
        target_chars_max = (target_lines + 1) * 52

        for it in items:
            diff = it["lines"] - target_lines
            if diff > 0:
                diff_str = f"(+{diff} lines, trim text)"
            elif diff < 0:
                diff_str = f"({diff} lines, expand text)"
            else:
                diff_str = "(balanced target)"

            print(f"  Card {it['index']:>2}: {it['lines']:>2} lines | {it['chars']:>3} chars | {it['words']:>2} words  {diff_str:<24}  {it['title'][:32]}")

        if is_imbalanced:
            print(f"\n  * Harmonization Target: Unify cards in #{sec_id} to approximately ~{target_lines} lines (~{target_chars_min}-{target_chars_max} characters).")

    print("\n" + "=" * 70)
    print(f"Summary for {file_path.name}: {imbalanced_sections} imbalanced section(s) found across {total_sections_checked} multi-card section(s).")
    return imbalanced_sections


def main():
    parser = argparse.ArgumentParser(description="Audit and unify component text lengths and line counts on a page (always 2560px desktop width by default)")
    parser.add_argument("file", nargs="?", help="HTML file to audit (e.g. hu/space-research.html)")
    parser.add_argument("--browser", "-b", action="store_true", help="Use headless Google Chrome for exact rendered line counts (at 2560px)")
    parser.add_argument("--width", "-w", type=int, default=VIEWPORT_WIDTH, help=f"Viewport width for browser test (default: {VIEWPORT_WIDTH}px)")
    parser.add_argument("--all", "-a", action="store_true", help="Audit all English and Hungarian content pages")
    parser.add_argument("--imbalanced", "-i", action="store_true", help="Only display sections with imbalanced line counts (variance >= 2 lines)")
    args = parser.parse_args()

    print("=================================================================")
    print(f" Sovereign Nation of Waikiki — Component Text Balance Auditor ({args.width}px)")
    print("=================================================================")

    if args.file:
        target_files = [Path(args.file).resolve()]
    elif args.all:
        target_files = []
        for lang in ("hu", "en"):
            p = ROOT / lang
            target_files.extend(p.glob("*.html"))
        target_files.sort()
    else:
        # Default to space-research or active file if not specified
        default_file = ROOT / "hu" / "space-research.html"
        target_files = [default_file] if default_file.exists() else []

    if not target_files:
        print("[!] No HTML files found to inspect. Pass a file path (e.g. `hu/overview.html`).", file=sys.stderr)
        sys.exit(1)

    total_imbalanced = 0
    for f in target_files:
        total_imbalanced += audit_file(f, use_browser=args.browser, only_imbalanced=args.imbalanced, width=args.width)

    if total_imbalanced > 0:
        print(f"\n[ATTENTION] Found {total_imbalanced} imbalanced component row(s). Review suggestions above to unify line counts.")
    else:
        print("\n[SUCCESS] All component rows and cards exhibit unified visual line balance!")


if __name__ == "__main__":
    main()
