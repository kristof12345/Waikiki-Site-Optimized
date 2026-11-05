---
name: publish
description: >-
  Publishes and pushes local git commits and tags across all configured remotes (origin, prod, optimized, redesign). Use when synchronizing repository remotes or deploying published site updates.
---

# Multi-Remote Publish Skill

This skill provides the automated workflow, validation checks, and scripts for publishing and pushing local git commits and tags to all configured downstream remotes in the Sovereign Nation of Waikiki repository.

---

## When to Use This Skill

Activate this skill when:
- New features, content, layout updates, or bugfixes have been committed locally.
- The user requests to "publish", "push to all remotes", "sync remotes", or "push to prod and origin".
- Synchronizing the multi-remote ecosystem (`origin`, `prod`, `optimized`, `redesign`).
- Releasing a new site tag or milestone release across all mirrors.

---

## Workspace Remotes Architecture

The repository maintains multiple synchronized remotes:

| Remote Name | Target Repository | Purpose |
| :--- | :--- | :--- |
| **`origin`** | `https://github.com/WaikikiGovernment/Site.git` | Primary canonical government repository. |
| **`prod`** | `https://github.com/waikiki-gov/Site.git` | Production deployment mirror. |
| **`optimized`** | `https://github.com/kristof12345/Waikiki-Site-Optimized.git` | Optimized performance mirror. |
| **`redesign`** | `https://github.com/selena-chease/Waikiki.git` | Redesign & cultural public mirror. |

---

## Core Publish Commands

### 1. Automated Python Multi-Remote Publisher (Recommended)

```bash
# Push current branch to all configured remotes
python3 .agents/skills/publish/scripts/publish.py

# Dry-run check: verify remote reachability and see pending commits without pushing
python3 .agents/skills/publish/scripts/publish.py --dry-run

# Push branch commits and all tags (--follow-tags)
python3 .agents/skills/publish/scripts/publish.py --tags

# Allow publishing even if working tree has untracked / uncommitted edits
python3 .agents/skills/publish/scripts/publish.py --allow-dirty
```

### 2. Direct Shell Multi-Push

```bash
for remote in $(git remote); do
    git push "$remote" HEAD
done
```

---

## Step-by-Step Publishing Workflow

### Step 1: Pre-Flight Integrity Checks
Before publishing, ensure the site satisfies all quality standards:
1. Verify HTML formatting and 0 empty lines:
   ```bash
   python3 scripts/build_pages.py --format --all
   ```
2. Verify CSS is purged and clean:
   ```bash
   purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes
   ```
3. Verify copy quality and spell audit:
   ```bash
   python3 .agents/skills/spell-check/scripts/audit.py
   ```
4. Verify bilingual locale synchronization:
   ```bash
   python3 .agents/skills/locale-sync/scripts/sync_check.py
   ```

### Step 2: Commit All Changes
Stage and commit changes with a descriptive message:
```bash
git add .
git commit -m "Your descriptive commit message"
```

### Step 3: Publish to All Remotes
Run the publisher:
```bash
python3 .agents/skills/publish/scripts/publish.py
```

### Step 4: Verify Remote Status
Ensure the script reports:
```text
[SUCCESS] All remotes synchronized successfully!
```
Each remote (`origin`, `prod`, `optimized`, `redesign`) will confirm that `HEAD` points to the latest commit.
