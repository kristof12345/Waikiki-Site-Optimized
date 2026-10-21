---
name: clear-css
description: >-
  Purges unused CSS classes, selectors, keyframes, and properties across all site stylesheets using PurgeCSS. Use when cleaning up stylesheets, removing dead styles after HTML refactoring, or optimizing bundle sizes.
---

# Clear CSS Skill

This skill provides the automated workflow, commands, and validation steps for purging unused CSS rules, obsolete classes, unused keyframe animations, and redundant properties across all stylesheets in the Sovereign Nation of Waikiki portal.

---

## When to Use This Skill

Activate this skill when:
- HTML pages or components have been refactored, updated, or deleted (e.g., removing old sections, cards, or retired UI elements).
- New CSS styles or page-specific stylesheets have been introduced and need dead-code elimination.
- Verifying that no stylesheet accumulates unused classes or abandoned keyframes.
- Optimizing production asset weight and browser rendering performance.

---

## Core Purge Command

To purge unused CSS across all stylesheets in `css/` by scanning all HTML and JavaScript files:

```bash
purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes
```

### Scripted Runner with Savings Analytics

You can also run the bundled Python wrapper to view per-file byte reductions and savings analytics:

```bash
# Run PurgeCSS and display a summary of size reductions per stylesheet
python3 .agents/skills/clear-css/scripts/clean_css.py

# Dry-run check: reports whether stylesheets contain unpurged bloat without modifying them
python3 .agents/skills/clear-css/scripts/clean_css.py --check
```

---

## What PurgeCSS Scans & Cleans

1. **Input Stylesheets (`--css css/*.css`)**: Scans all top-level stylesheets (e.g., `common.css`, `plane.css`, `nature.css`, `space-research.css`, etc.).
2. **Content Scanning (`--content **/*.html **/*.js`)**:
   - Searches all `.html` pages (both `hu/` and `en/`, including subdirectories like `bio/`).
   - Searches all `.js` scripts in `js/` to preserve dynamically toggled classes (e.g., `is-active`, `is-open`, theme modifiers, and menu states).
3. **Keyframe Pruning (`--keyframes`)**: Removes unused `@keyframes` animation blocks whose animation names are not referenced by any surviving CSS rule.

---

## Step-by-Step CSS Cleaning Workflow

### Step 1: Run the Purge
Execute the purge command or Python runner from the workspace root:
```bash
purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes
```

### Step 2: Review Modified Stylesheets
Inspect the git diff to verify the removed selectors:
```bash
git diff --stat css/
git diff css/
```
Confirm that only obsolete or deleted components were stripped.

### Step 3: Verify Dynamic & Script States
Ensure that any classes applied solely via JavaScript (e.g., in event listeners or DOM manipulation) are present in `js/*.js` files or preserved by the content scanner.

### Step 4: Validate Site Integrity
After purging CSS, run the site-wide copy and locale sync checkers to confirm project consistency:
```bash
python3 .agents/skills/locale-sync/scripts/sync_check.py
python3 .agents/skills/spell-check/scripts/audit.py
```
