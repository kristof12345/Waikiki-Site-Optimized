import os
import subprocess
import sys
import re
import urllib.parse
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(SCRIPT_DIR)
IMAGES_DIR = os.path.join(SITE_DIR, "images")

MAX_WIDTH = 2560
MAX_HEIGHT = 1440

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

def get_excluded_images(site_dir):
    """
    Finds all images used in hero sections or portrait containers across all HTML files.
    Returns a set of normalized absolute file paths and a set of filenames.
    """
    excluded_filenames = set()
    excluded_paths = set()
    
    html_files = []
    for root, dirs, files in os.walk(site_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    for html_path in html_files:
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {html_path}: {e}", file=sys.stderr)
            continue

        extracted_srcs = set()

        # 1. Match hero sections, hero-media, or [data-hero] blocks
        hero_patterns = [
            r'<section[^>]*class=[\'"][^\'\"]*\bhero\b[^\'\"]*[\'\"][^>]*>.*?</section>',
            r'<div[^>]*class=[\'"][^\'\"]*\bhero-media\b[^\'\"]*[\'\"][^>]*>.*?</div>',
            r'<[^>]*data-hero\b[^>]*>.*?</[^>]+>'
        ]
        for pattern in hero_patterns:
            for block in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                block_content = block.group(0)
                # Find img src
                for src in re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', block_content, re.IGNORECASE):
                    extracted_srcs.add(src)
                # Find source srcset
                for srcset in re.findall(r'srcset=[\'"]([^\'"]+)[\'"]', block_content, re.IGNORECASE):
                    for part in srcset.split(','):
                        clean_src = part.strip().split()[0]
                        extracted_srcs.add(clean_src)
                # Find inline background url(...)
                for bg in re.findall(r'url\([\'"]?([^\'\"\)\s]+)[\'"]?\)', block_content, re.IGNORECASE):
                    extracted_srcs.add(bg)

        # 2. Match preload tags in <head> (hero preloads)
        head_match = re.search(r'<head>(.*?)</head>', content, re.DOTALL | re.IGNORECASE)
        if head_match:
            for preload in re.findall(r'<link[^>]+rel=[\'"]preload[\'"][^>]+href=[\'"]([^\'"]+)[\'"]', head_match.group(1), re.IGNORECASE):
                extracted_srcs.add(preload)

        # 3. Match portrait containers and pedigree tree thumb cards
        portrait_patterns = [
            r'<[^>]*class=[\'"][^\'\"]*\bportrait\b[^\'\"]*[\'\"][^>]*>.*?</[^>]+>',
            r'<[^>]*class=[\'"][^\'\"]*\b(tree-node-thumb|founder-card|ancestor-card)\b[^\'\"]*[\'\"][^>]*>.*?</[^>]+>'
        ]
        for pattern in portrait_patterns:
            for block in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                block_content = block.group(0)
                for src in re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', block_content, re.IGNORECASE):
                    extracted_srcs.add(src)

        # Resolve paths
        html_dir = os.path.dirname(html_path)
        for raw_src in extracted_srcs:
            if raw_src.startswith('data:') or raw_src.startswith(('http://', 'https://')):
                continue
            clean_url = urllib.parse.unquote(raw_src)
            filename = os.path.basename(clean_url)
            excluded_filenames.add(filename)

            if clean_url.startswith('/'):
                abs_path = os.path.normpath(os.path.join(SITE_DIR, clean_url.lstrip('/')))
            else:
                abs_path = os.path.normpath(os.path.join(html_dir, clean_url))
            excluded_paths.add(abs_path)

    return excluded_filenames, excluded_paths

def get_image_dimensions(file_path):
    """Returns (width, height) of an image using 'identify', or (None, None) on error."""
    try:
        result = subprocess.run(
            ['identify', '-format', '%w %h', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        parts = result.stdout.strip().split()
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except Exception as e:
        print(f"Error identifying {file_path}: {e}", file=sys.stderr)
    return None, None

def resize_image(file_path, width, height, dry_run=False):
    """
    Resizes image to fit within max dimensions while preserving exact aspect ratio.
    Never upscales, never distorts, and never forcibly crops portrait photos.
    """
    if width >= height:
        target_spec = f"{MAX_WIDTH}x{MAX_HEIGHT}>"
    else:
        target_spec = f"{MAX_HEIGHT}x{MAX_WIDTH}>"

    if dry_run:
        return True

    try:
        subprocess.run(
            ['mogrify', '-resize', target_spec, file_path],
            check=True
        )
        return True
    except Exception as e:
        print(f"Error resizing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Resize large non-hero images preserving aspect ratio.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report without modifying any files.")
    parser.add_argument("--all-images", action="store_true", help="Process all images (not just UniversalUpscaler* files).")
    args = parser.parse_args()

    print(f"Project root directory: {SITE_DIR}")
    print(f"Images directory: {IMAGES_DIR}")
    if args.dry_run:
        print("[DRY RUN MODE ENABLED - No files will be modified]")
    
    excluded_filenames, excluded_paths = get_excluded_images(SITE_DIR)
    print(f"Found {len(excluded_filenames)} excluded unique images (heroes & portraits).")

    image_paths = []
    for root, dirs, files in os.walk(IMAGES_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if not args.all_images and not file.startswith('UniversalUpscaler'):
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                abs_path = os.path.join(root, file)
                if file not in excluded_filenames and abs_path not in excluded_paths:
                    image_paths.append(abs_path)

    print(f"Found {len(image_paths)} images eligible for processing (excluding heroes & portraits).")

    needs_resize_count = 0
    resized_count = 0

    for path in image_paths:
        rel_path = os.path.relpath(path, IMAGES_DIR)
        width, height = get_image_dimensions(path)
        if width is None or height is None:
            continue

        # Check if resizing is actually needed (downscale only)
        needs_resize = False
        if width >= height and (width > MAX_WIDTH or height > MAX_HEIGHT):
            needs_resize = True
        elif height > width and (width > MAX_HEIGHT or height > MAX_WIDTH):
            needs_resize = True

        if needs_resize:
            needs_resize_count += 1
            print(f"Needs resize: {rel_path} ({width}x{height}px)")
            if resize_image(path, width, height, dry_run=args.dry_run):
                if not args.dry_run:
                    new_w, new_h = get_image_dimensions(path)
                    print(f"  -> Resized to {new_w}x{new_h}px")
                else:
                    print(f"  -> [Dry Run] Would resize proportionally")
                resized_count += 1
            else:
                print("  -> Failed to resize")

    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Total excluded hero/portrait images: {len(excluded_filenames)}")
    print(f"  Total scanned eligible images:       {len(image_paths)}")
    print(f"  Images needing downscale:            {needs_resize_count}")
    print(f"  Successfully processed:              {resized_count}")
    print("=" * 50)

if __name__ == '__main__':
    main()
