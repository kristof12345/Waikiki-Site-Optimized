#!/usr/bin/env python3
"""
copy_x_images.py

Copies all "-X" images from the site's images/ folder to the configured
destination directory (default:
"/Users/kristof/Library/Mobile Documents/com~apple~CloudDocs/Generated/generated/new").

Usage Examples:
  # Copy all "-X" images to the default destination (skips existing files)
  python3 scripts/copy_x_images.py

  # Preview which files would be copied without writing anything
  python3 scripts/copy_x_images.py --dry-run

  # Overwrite files that already exist in the destination directory
  python3 scripts/copy_x_images.py --overwrite
"""

import argparse
import os
import shutil
import sys


DEFAULT_DEST_DIR = (
    "/Users/kristof/Library/Mobile Documents/com~apple~CloudDocs/Generated/generated/new"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Copy all "-X" images from images/ to the destination directory.'
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
        "--dest-dir",
        default=DEFAULT_DEST_DIR,
        help="Destination directory to copy '-X' images into (default: %(default)s)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Preview files to copy without modifying the filesystem",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite files that already exist in the destination directory (default: skip existing)",
    )
    return parser.parse_args()


def find_x_images(images_dir: str):
    """Return sorted list of filenames in images_dir whose stem ends with '-X'."""
    if not os.path.isdir(images_dir):
        print(f"Error: Images directory not found: {images_dir}", file=sys.stderr)
        return []

    matches = []
    for entry in sorted(os.listdir(images_dir)):
        if entry.startswith("."):
            continue
        entry_path = os.path.join(images_dir, entry)
        if not os.path.isfile(entry_path):
            continue
        stem, _ = os.path.splitext(entry)
        if stem.endswith("-X"):
            matches.append(entry)

    return matches


def main():
    args = parse_args()
    site_dir = os.path.abspath(args.site_dir)
    images_dir = (
        os.path.abspath(args.images_dir)
        if args.images_dir
        else os.path.join(site_dir, "images")
    )
    dest_dir = os.path.abspath(args.dest_dir)

    print(f"Images directory:      {images_dir}")
    print(f"Destination directory: {dest_dir}")
    print(f"Mode:                  {'DRY-RUN' if args.dry_run else 'LIVE'}\n")

    x_images = find_x_images(images_dir)
    if not x_images:
        print("No '-X' images found in the images folder.")
        return 0

    print(f"Found {len(x_images)} '-X' image(s).\n")

    if not args.dry_run:
        os.makedirs(dest_dir, exist_ok=True)

    copied = 0
    skipped = 0
    errors = 0

    for filename in x_images:
        src_path = os.path.join(images_dir, filename)
        dst_path = os.path.join(dest_dir, filename)

        if not args.overwrite and os.path.exists(dst_path):
            print(f"  [Skipped] {filename} (already exists)")
            skipped += 1
            continue

        if args.dry_run:
            print(f"  [Would copy] {filename}")
            copied += 1
        else:
            try:
                shutil.copy2(src_path, dst_path)
                print(f"  [Copied] {filename}")
                copied += 1
            except Exception as e:
                print(f"  [Error] {filename}: {e}", file=sys.stderr)
                errors += 1

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"'-X' images found: {len(x_images)}")
    print(f"{'Would copy' if args.dry_run else 'Copied'}:           {copied}")
    print(f"Skipped:          {skipped}")
    if errors:
        print(f"Errors:           {errors}")
    print("\nDone.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
