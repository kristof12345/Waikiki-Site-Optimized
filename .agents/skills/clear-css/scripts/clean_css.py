#!/usr/bin/env python3
"""
Clean CSS Runner & Optimizer — Sovereign Nation of Waikiki Site
Part of the 'clear-css' skill.

Runs PurgeCSS to remove unused classes, selectors, keyframes, and properties:
    purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes

Tracks file sizes before and after, reports byte savings, and summarizes changes.

Usage:
    python3 .agents/skills/clear-css/scripts/clean_css.py
    python3 .agents/skills/clear-css/scripts/clean_css.py --check   # Check if CSS has unpurged bloat
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CSS_DIR = ROOT / "css"


def get_css_sizes() -> dict[str, int]:
    sizes = {}
    for p in CSS_DIR.glob("*.css"):
        if p.is_file():
            sizes[p.name] = p.stat().st_size
    return sizes


def run_purgecss() -> int:
    # purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes
    css_files = [str(p.relative_to(ROOT)) for p in sorted(CSS_DIR.glob("*.css"))]
    if not css_files:
        print("[!] No CSS files found in css/", file=sys.stderr)
        return 1

    cmd = [
        "purgecss",
        "--css", *css_files,
        "--output", "css/",
        "--content", "**/*.html", "**/*.js",
        "--keyframes",
    ]

    try:
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[!] PurgeCSS exited with code {res.returncode}:\n{res.stderr}", file=sys.stderr)
            return res.returncode
        return 0
    except FileNotFoundError:
        print("[!] 'purgecss' command not found in PATH. Install via: npm install -g purgecss", file=sys.stderr)
        return 127


def main():
    parser = argparse.ArgumentParser(description="Purge unused CSS classes, selectors, and keyframes")
    parser.add_argument("--check", action="store_true", help="Dry run check for unpurged CSS")
    args = parser.parse_args()

    print("=================================================================")
    print(" Sovereign Nation of Waikiki — Clean CSS Optimizer")
    print("=================================================================")

    before_sizes = get_css_sizes()

    if args.check:
        # Backup css files to temporary dir
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            for name, _ in before_sizes.items():
                shutil.copy2(CSS_DIR / name, tmp_path / name)

            ret = run_purgecss()
            if ret != 0:
                sys.exit(ret)

            after_sizes = get_css_sizes()
            diff_files = []
            for name, b_sz in before_sizes.items():
                a_sz = after_sizes.get(name, b_sz)
                if a_sz < b_sz:
                    diff_files.append((name, b_sz, a_sz, b_sz - a_sz))

            # Restore original files
            for name in before_sizes:
                shutil.copy2(tmp_path / name, CSS_DIR / name)

            if diff_files:
                print(f"[!] Found {len(diff_files)} stylesheet(s) with unpurged rules:")
                for name, b, a, saved in diff_files:
                    print(f"    - {name}: {b:,} B -> {a:,} B (save {saved:,} B, -{saved / b * 100:.1f}%)")
                sys.exit(1)
            else:
                print("[OK] All stylesheets are already 100% clean and purged.")
                sys.exit(0)

    # Actual purge
    ret = run_purgecss()
    if ret != 0:
        sys.exit(ret)

    after_sizes = get_css_sizes()

    reduced = []
    total_before = sum(before_sizes.values())
    total_after = sum(after_sizes.values())

    for name, b_sz in before_sizes.items():
        a_sz = after_sizes.get(name, b_sz)
        if a_sz != b_sz:
            diff = b_sz - a_sz
            reduced.append((name, b_sz, a_sz, diff))

    if reduced:
        print(f"\n[SUCCESS] Purged unused CSS across {len(reduced)} file(s):")
        for name, b, a, diff in reduced:
            pct = (diff / b * 100) if b else 0
            if diff > 0:
                print(f"    - {name:<24} {b:>7,} B -> {a:>7,} B  (-{diff:,} B, -{pct:.1f}%)")
            else:
                print(f"    - {name:<24} {b:>7,} B -> {a:>7,} B  (+{-diff:,} B)")
        saved_total = total_before - total_after
        print(f"\nTotal size: {total_before:,} B -> {total_after:,} B (Saved {saved_total:,} B, -{saved_total / total_before * 100:.1f}%)")
    else:
        print(f"\n[OK] All {len(before_sizes)} stylesheets are already clean. No unused CSS was found.")

    print("-----------------------------------------------------------------")


if __name__ == "__main__":
    main()
