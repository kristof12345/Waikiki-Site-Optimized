#!/usr/bin/env python3
"""
Multi-Remote Publisher — Sovereign Nation of Waikiki Site
Part of the 'publish' skill.

Pushes commits and tags to all configured git remotes:
    - Discovers all configured remotes (`git remote`)
    - Identifies current branch (`git branch --show-current`)
    - Checks for uncommitted working tree changes
    - Pushes sequentially to each remote with clear progress reporting
    - Summarizes push results across all remotes

Usage:
    python3 .agents/skills/publish/scripts/publish.py            # Push current branch to all remotes
    python3 .agents/skills/publish/scripts/publish.py --dry-run  # Dry-run test push without pushing
    python3 .agents/skills/publish/scripts/publish.py --tags     # Push branch and all tags
    python3 .agents/skills/publish/scripts/publish.py --force    # Force push (use with extreme caution)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def run_git(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=check,
    )


def get_remotes() -> list[tuple[str, str]]:
    """Return list of (remote_name, push_url)."""
    res = run_git(["remote", "-v"])
    remotes = {}
    for line in res.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[2] == "(push)":
            remotes[parts[0]] = parts[1]
    # Fallback to standard git remote if no push urls parsed
    if not remotes:
        res_names = run_git(["remote"])
        for name in res_names.stdout.splitlines():
            if name.strip():
                remotes[name.strip()] = ""
    return sorted(list(remotes.items()))


def get_current_branch() -> str:
    res = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    return res.stdout.strip()


def has_uncommitted_changes() -> bool:
    res = run_git(["status", "--porcelain"])
    return bool(res.stdout.strip())


def push_to_remote(remote: str, branch: str, dry_run: bool = False, push_tags: bool = False, force: bool = False) -> tuple[bool, str]:
    cmd = ["push"]
    if dry_run:
        cmd.append("--dry-run")
    if force:
        cmd.append("--force")
    if push_tags:
        cmd.append("--follow-tags")
    cmd.extend([remote, f"HEAD:{branch}"])

    try:
        res = subprocess.run(
            ["git"] + cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        output = (res.stdout + "\n" + res.stderr).strip()
        return (res.returncode == 0, output)
    except Exception as e:
        return (False, str(e))


def main():
    parser = argparse.ArgumentParser(description="Push local git commits and tags to all configured remotes")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Simulate push without modifying remotes")
    parser.add_argument("--tags", "-t", action="store_true", help="Include tags in push (--follow-tags)")
    parser.add_argument("--force", "-f", action="store_true", help="Force push (use with extreme caution)")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow publishing with uncommitted changes")
    args = parser.parse_args()

    print("=================================================================")
    print(" Sovereign Nation of Waikiki — Multi-Remote Publisher")
    print("=================================================================")

    # 1. Branch detection
    branch = get_current_branch()
    print(f"Current Branch: {branch}")

    # 2. Working tree check
    if has_uncommitted_changes() and not args.allow_dirty:
        print("\n[!] Working tree has uncommitted changes:")
        run_git(["status", "-s"], check=False)
        print("\nCommit or stash your changes before publishing, or use --allow-dirty.")
        sys.exit(1)

    # 3. Discover remotes
    remotes = get_remotes()
    if not remotes:
        print("[!] No git remotes found. Add a remote with `git remote add <name> <url>`.")
        sys.exit(1)

    mode_label = " [DRY-RUN]" if args.dry_run else ""
    print(f"Discovered {len(remotes)} remote(s) to publish{mode_label}:\n")
    for name, url in remotes:
        print(f"  • {name:<12} -> {url}")
    print()

    # 4. Push to each remote
    results = []
    has_failure = False

    for name, url in remotes:
        print(f"Publishing to '{name}'...", end=" ", flush=True)
        ok, out = push_to_remote(name, branch, dry_run=args.dry_run, push_tags=args.tags, force=args.force)

        # Classify output message
        status_line = "OK"
        if not ok:
            status_line = "FAILED"
            has_failure = True
        elif "Everything up-to-date" in out:
            status_line = "Up to date"
        elif "->" in out:
            # Extract branch update line e.g. "4e44cddf..c53d51d5  HEAD -> main"
            for l in out.splitlines():
                if "->" in l:
                    status_line = l.strip()
                    break

        print(f"[{status_line}]")
        if not ok or (args.dry_run and out):
            for line in out.splitlines():
                print(f"    {line}")
        results.append((name, url, ok, status_line))

    # 5. Summary
    print("\n-----------------------------------------------------------------")
    if has_failure:
        print("[!] Some remotes failed to receive updates. See details above.")
        print("-----------------------------------------------------------------")
        sys.exit(1)
    else:
        success_msg = "[SUCCESS] All remotes synchronized successfully!" if not args.dry_run else "[SUCCESS] Dry-run complete. All remotes reachable and ready."
        print(success_msg)
        print("-----------------------------------------------------------------")


if __name__ == "__main__":
    main()
