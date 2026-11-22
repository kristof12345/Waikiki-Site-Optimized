#!/usr/bin/env python3
"""
replace_upscaled_images.py

Scans the images directory for upscaled/enhanced files ending with "-U.jpg"
or "-X.jpg", identifies their matching original or lower-priority references
in HTML files, and replaces those references with the highest-priority variant.
Any files ending with "-U-X.jpg" or "-X-U.jpg" are first renamed to "-X.jpg"
and treated as "-X" variants. The "-U" rule is stronger than "-X": if both
"-U" and "-X" exist for the same base image, "-U.jpg" is used (and any
"-X.jpg" reference is also upgraded to "-U.jpg").

Usage Examples:
  # Normal execution: scan and update references across all HTML files
  python3 scripts/replace_upscaled_images.py

  # Dry-run preview: see what will be updated without writing to disk
  python3 scripts/replace_upscaled_images.py --dry-run

  # Also delete the old superseded images from the images/ folder
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
        description="Find -U and -X images and replace their older references in HTML files (-U takes precedence over -X)."
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
        help="Delete the old superseded image files from disk if they exist",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose details for every scanned file",
    )
    return parser.parse_args()


def normalize_double_suffix_images(images_dir: str, dry_run: bool):
    """
    Finds any files ending with '-U-X.jpg' or '-X-U.jpg' in images_dir and
    renames them to '-X.jpg' so they are treated as plain '-X' variants.
    Returns: (x_bases_added, double_suffix_by_base)
    """
    x_bases_added = set()
    double_suffix_by_base = {}

    if not os.path.isdir(images_dir):
        return x_bases_added, double_suffix_by_base

    double_entries = []
    for entry in sorted(os.listdir(images_dir)):
        if entry.startswith("."):
            continue
        entry_path = os.path.join(images_dir, entry)
        if not os.path.isfile(entry_path):
            continue
        if entry.endswith("-U-X.jpg") or entry.endswith("-X-U.jpg"):
            double_entries.append(entry)

    if not double_entries:
        return x_bases_added, double_suffix_by_base

    print(f"Found {len(double_entries)} double-suffix ('-U-X' / '-X-U') image(s) to normalize:")
    claimed_targets = set()

    for entry in double_entries:
        base = entry[:-8]
        new_name = f"{base}-X.jpg"
        old_path = os.path.join(images_dir, entry)
        new_path = os.path.join(images_dir, new_name)

        double_suffix_by_base.setdefault(base, []).append(entry)
        x_bases_added.add(base)

        if os.path.exists(new_path) or new_name in claimed_targets:
            print(f"  [Skipped rename] {entry} -> {new_name} (target already exists)")
            continue

        claimed_targets.add(new_name)
        if dry_run:
            print(f"  [Would rename] {entry} -> {new_name}")
        else:
            try:
                os.rename(old_path, new_path)
                print(f"  [Renamed] {entry} -> {new_name}")
            except Exception as e:
                print(f"  Error renaming {entry} -> {new_name}: {e}", file=sys.stderr)

    print()
    return x_bases_added, double_suffix_by_base


def get_u_mapping(images_dir: str, extra_x_bases=None, double_suffix_by_base=None):
    """
    Finds all files ending with '-U.jpg' or '-X.jpg' in images_dir.
    '-U.jpg' takes precedence over '-X.jpg'.
    Returns a dict: { old_filename: target_filename }
    """
    if not os.path.isdir(images_dir):
        print(f"Error: Images directory not found: {images_dir}", file=sys.stderr)
        return {}

    u_bases = set()
    x_bases = set(extra_x_bases or ())

    for entry in sorted(os.listdir(images_dir)):
        if entry.startswith("."):
            continue
        entry_path = os.path.join(images_dir, entry)
        if not os.path.isfile(entry_path):
            continue

        if entry.endswith("-U-X.jpg") or entry.endswith("-X-U.jpg"):
            continue
        elif entry.endswith("-U.jpg"):
            u_bases.add(entry[:-6])
        elif entry.endswith("-X.jpg"):
            x_bases.add(entry[:-6])

    mapping = {}

    # -X rule (applied only when -U does not exist)
    for base in sorted(x_bases):
        if base not in u_bases:
            mapping[f"{base}.jpg"] = f"{base}-X.jpg"

    # -U rule is stronger: overrides base.jpg and also upgrades base-X.jpg -> base-U.jpg
    for base in sorted(u_bases):
        target = f"{base}-U.jpg"
        mapping[f"{base}.jpg"] = target
        mapping[f"{base}-X.jpg"] = target

    # Map any HTML references to old '-U-X.jpg' / '-X-U.jpg' names to the winning target
    if double_suffix_by_base:
        for base, old_names in sorted(double_suffix_by_base.items()):
            target = f"{base}-U.jpg" if base in u_bases else f"{base}-X.jpg"
            for old_name in old_names:
                mapping[old_name] = target

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

    extra_x_bases, double_suffix_by_base = normalize_double_suffix_images(
        images_dir, args.dry_run
    )

    mapping = get_u_mapping(images_dir, extra_x_bases, double_suffix_by_base)
    if not mapping:
        print("No '-U' or '-X' images found in the images folder.")
        return 0

    unique_targets = sorted(set(mapping.values()))
    print(f"Found {len(unique_targets)} '-U' / '-X' target image(s) ({len(mapping)} replacement rule(s)):")
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
    print(f"'-U'/'-X' target images:     {len(unique_targets)}")
    print(f"Replacement rules checked:   {len(mapping)}")
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
