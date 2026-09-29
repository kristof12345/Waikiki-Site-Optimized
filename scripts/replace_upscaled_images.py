#!/usr/bin/env python3
"""
replace_upscaled_images.py

Scans the images directory for upscaled files ending with "-U.jpg",
identifies their matching original references in HTML files (the same
filename without the "-U" part), and replaces those references with
the "-U.jpg" variant.

Usage Examples:
  # Normal execution: scan and update references across all HTML files
  python3 scripts/replace_upscaled_images.py

  # Dry-run preview: see what will be updated without writing to disk
  python3 scripts/replace_upscaled_images.py --dry-run

  # Also delete the old un-upscaled images from the images/ folder
  python3 scripts/replace_upscaled_images.py --delete-old
"""

import argparse
import os
import re
import sys
import urllib.parse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find -U upscaled images and replace their non-U references in HTML files."
    )
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate_root = os.path.abspath(os.path.join(script_dir, ".."))
    if os.path.isdir(os.path.join(candidate_root, "images")):
        default_site_dir = candidate_root
    else:
        default_site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"

    parser.add_argument(
        "--site-dir",
        default=default_site_dir,
        help="Root directory of the website (default: %(default)s)",
    )
    parser.add_argument(
        "--images-dir",
        default=None,
        help="Path to the images directory (default: <site-dir>/images)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying any files",
    )
    parser.add_argument(
        "--delete-old",
        action="store_true",
        help="Delete the old non-U image files from disk if they exist",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose details for every scanned file",
    )
    return parser.parse_args()


def get_u_mapping(images_dir: str):
    """
    Finds all files ending strictly with '-U.jpg' in images_dir.
    Returns a dict: { original_filename: u_filename }
    """
    if not os.path.isdir(images_dir):
        print(f"Error: Images directory not found: {images_dir}", file=sys.stderr)
        return {}

    mapping = {}

    for entry in sorted(os.listdir(images_dir)):
        if entry.startswith("."):
            continue
        entry_path = os.path.join(images_dir, entry)
        if not os.path.isfile(entry_path):
            continue

        if entry.endswith("-U.jpg"):
            orig_name = entry[:-6] + ".jpg"
            mapping[orig_name] = entry

    return mapping


def find_html_files(site_dir: str):
    """Find all .html files in site_dir, excluding hidden directories."""
    html_files = []
    for root, dirs, files in os.walk(site_dir):
        # Exclude hidden directories like .git
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".html") and not f.startswith("."):
                html_files.append(os.path.join(root, f))
    html_files.sort()
    return html_files


def replace_references_in_text(content: str, mapping: dict):
    """
    Replaces references to orig_name with u_name in content.
    Returns: (new_content, list of replacements details)
    """
    replacements_done = []
    new_content = content

    for orig_name, u_name in mapping.items():
        # Candidate search targets: literal original name and URL-quoted name
        targets = [orig_name]
        encoded_name = urllib.parse.quote(orig_name)
        if encoded_name != orig_name:
            targets.append(encoded_name)

        for target in targets:
            encoded_u = urllib.parse.quote(u_name) if target == encoded_name else u_name
            # Regex lookbehind and lookahead to match boundaries around URL/path segments
            pattern = re.compile(
                r'(?<=[\/"\'\(=\s])' + re.escape(target) + r'(?=["\'#?\)\s,;>]|$)'
            )

            matches = list(pattern.finditer(new_content))
            if matches:
                replacements_done.append((orig_name, u_name, len(matches)))
                new_content = pattern.sub(encoded_u, new_content)

    return new_content, replacements_done


def main():
    args = parse_args()
    site_dir = os.path.abspath(args.site_dir)
    images_dir = (
        os.path.abspath(args.images_dir)
        if args.images_dir
        else os.path.join(site_dir, "images")
    )

    print(f"Site directory:   {site_dir}")
    print(f"Images directory: {images_dir}")
    if args.dry_run:
        print("Mode:             DRY-RUN (no files will be modified)\n")
    else:
        print("Mode:             LIVE (files will be updated)\n")

    mapping = get_u_mapping(images_dir)
    if not mapping:
        print("No '-U' images found in the images folder.")
        return 0

    print(f"Found {len(mapping)} upscaled '-U' image(s) in images folder:")
    for orig_name, u_name in mapping.items():
        orig_exists = os.path.exists(os.path.join(images_dir, orig_name))
        status = "(original exists on disk)" if orig_exists else "(original not on disk)"
        print(f"  • {u_name}  -->  looking for '{orig_name}' {status}")
    print()

    html_files = find_html_files(site_dir)
    print(f"Scanning {len(html_files)} HTML files for references...\n")

    total_replacements = 0
    updated_files_count = 0

    for html_file in html_files:
        rel_path = os.path.relpath(html_file, site_dir)
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {rel_path}: {e}", file=sys.stderr)
            continue

        new_content, file_replacements = replace_references_in_text(content, mapping)

        if file_replacements:
            updated_files_count += 1
            file_total = sum(count for _, _, count in file_replacements)
            total_replacements += file_total

            action = "Would update" if args.dry_run else "Updated"
            print(f"[{action}] {rel_path} ({file_total} occurrence(s)):")
            for orig, u_variant, count in file_replacements:
                print(f"    - '{orig}' -> '{u_variant}' ({count}x)")

            if not args.dry_run:
                try:
                    with open(html_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                except Exception as e:
                    print(f"Error writing {rel_path}: {e}", file=sys.stderr)

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"'-U' images checked:         {len(mapping)}")
    print(f"HTML files scanned:          {len(html_files)}")
    print(f"HTML files with references:  {updated_files_count}")
    print(f"Total references replaced:   {total_replacements}")

    # Handle --delete-old if requested
    if args.delete_old:
        print("\nChecking original files for deletion (--delete-old)...")
        deleted_count = 0
        for orig_name in mapping.keys():
            orig_path = os.path.join(images_dir, orig_name)
            if os.path.exists(orig_path):
                if args.dry_run:
                    print(f"  [Would delete] {orig_name}")
                    deleted_count += 1
                else:
                    try:
                        os.remove(orig_path)
                        print(f"  [Deleted] {orig_name}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  Error deleting {orig_name}: {e}", file=sys.stderr)
            else:
                print(f"  [Skipped] {orig_name} (does not exist on disk)")
        action = "Would delete" if args.dry_run else "Deleted"
        print(f"{action} {deleted_count} old image file(s).")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
