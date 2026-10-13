#!/usr/bin/env python3
"""Format document and remove all empty lines in document.

Usage:
    python3 scripts/format_document.py [files...]
    python3 scripts/format_document.py --all
    cat file.html | python3 scripts/format_document.py -
"""

import os
import re
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Embedded Node script for exact js-beautify HTML formatting
NODE_FORMAT_SCRIPT = """
const fs = require('fs');
const beautify = require('js-beautify').html;
const opts = {
    indent_size: 4,
    indent_char: ' ',
    max_preserve_newlines: 0,
    preserve_newlines: false,
    extra_liners: [],
    end_with_newline: true,
    wrap_line_length: 0,
    indent_inner_html: false
};
let input = fs.readFileSync(0, 'utf8');
let out = beautify(input, opts);
let lines = out.split(/\\r?\\n/).filter(l => l.trim().length > 0);
process.stdout.write(lines.join('\\n') + '\\n');
"""


def format_and_remove_empty_lines(html_content: str) -> str:
    """Format document with 4-space indent and remove all empty lines."""
    try:
        proc = subprocess.run(
            ["node", "-e", NODE_FORMAT_SCRIPT],
            input=html_content,
            text=True,
            capture_output=True,
            check=True,
            cwd=str(ROOT),
        )
        if proc.stdout.strip():
            return proc.stdout
    except Exception:
        pass

    # Fallback if node or js-beautify is unavailable
    lines = [line for line in html_content.splitlines() if line.strip()]
    return "\n".join(lines) + "\n"


def get_all_html_files(directory: Path) -> list[Path]:
    """Recursively collect all .html files excluding node_modules and .git."""
    results = []
    if not directory.exists():
        return results
    for item in directory.rglob("*.html"):
        parts = item.parts
        if "node_modules" in parts or ".git" in parts:
            continue
        results.append(item)
    return sorted(results)


def process_file(file_path: Path) -> bool:
    """Format and strip blank lines for a single file in-place."""
    try:
        original = file_path.read_text(encoding="utf-8")
        processed = format_and_remove_empty_lines(original)
        if original != processed:
            file_path.write_text(processed, encoding="utf-8")
            try:
                rel = file_path.relative_to(Path.cwd())
            except ValueError:
                rel = file_path
            print(f"Formatted and cleaned: {rel}")
            return True
    except Exception as err:
        print(f"Error processing {file_path}: {err}", file=sys.stderr)
    return False


def main():
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print("Usage:")
        print("  python3 scripts/format_document.py <file1.html> [file2.html ...]")
        print("  python3 scripts/format_document.py --all")
        print("  cat index.html | python3 scripts/format_document.py -")
        sys.exit(0)

    if args[0] == "-":
        stdin_content = sys.stdin.read()
        sys.stdout.write(format_and_remove_empty_lines(stdin_content))
        return

    files = []
    if "--all" in args:
        files += get_all_html_files(ROOT / "en")
        files += get_all_html_files(ROOT / "hu")
        root_index = ROOT / "index.html"
        if root_index.exists():
            files.append(root_index)
    else:
        for arg in args:
            files.append(Path(arg).resolve())

    changed = 0
    for file_path in files:
        if process_file(file_path):
            changed += 1

    print(f"Done. Processed {len(files)} file(s), updated {changed}.")


if __name__ == "__main__":
    main()
