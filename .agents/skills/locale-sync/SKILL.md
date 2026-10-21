---
name: locale-sync
description: >-
  Detects active uncommitted changes across English (en/) and Hungarian (hu/) HTML pages, analyzes counterpart file parity, flags discrepancies in structure, specs, numbers, watermarks, and section styles, and guides exact synchronization between languages.
---

# Locale Synchronization Skill (HU <-> EN)

This skill provides the automated auditing tools, runbook, and editorial guidelines to detect active modifications in either Hungarian (`hu/`) or English (`en/`) pages and synchronize them accurately to their opposite-language counterpart.

---

## When to Use This Skill

Activate this skill when:
- The user modifies, adds, or deletes content in a Hungarian or English HTML page and asks to sync changes to the other language.
- The user asks to "sync active changes", "sync to EN", "sync to HU", or check language parity.
- Reviewing whether two language versions have matching section counts, cards, wireframes/watermarks, numbers, or alternating `light-bg` styles.
- Before committing changes that affect bilingual pages.

---

## Workspace Locale Architecture

Every content page in the Sovereign Nation of Waikiki portal is paired 1-to-1 between Hungarian and English:

| Hungarian File | English File | Counterpart Path Mapping |
| :--- | :--- | :--- |
| `hu/<page>.html` | `en/<page>.html` | Switch prefix `hu/` <-> `en/` |
| `hu/bio/<person>.html` | `en/bio/<person>.html` | Switch prefix `hu/` <-> `en/` |

Both files share identical semantic layout, section hierarchies, CSS classes, wireframe illustrations, card counts, and metrics, but use localized prose and typography.

---

## Automated Locale Sync Checker

The workspace includes a dedicated inspection and parity checker script:

```bash
# 1. Auto-detect all active uncommitted HTML changes in git and inspect counterpart parity
python3 .agents/skills/locale-sync/scripts/sync_check.py

# 2. Check a specific file against its counterpart
python3 .agents/skills/locale-sync/scripts/sync_check.py hu/space-research.html

# 3. Check all page pairs across the entire website for structural and metric parity
python3 .agents/skills/locale-sync/scripts/sync_check.py --all
```

### What `sync_check.py` Automatically Checks:
1. **Active Git Changes**: Identifies which chunks were added or removed in the active working tree.
2. **Section Style Parity**: Validates that corresponding sections have identical `light-bg` / `fade-in` classes (enforcing the alternating section rule).
3. **Card Count Parity**: Verifies that each section contains an equal number of cards across both locales.
4. **Watermark & Wireframe SVGs**: Checks that wireframe schematics (`aircraft-watermark`, `watermark`) match on both sides.
5. **Numerical & Specification Parity**: Flags unmatched numbers, years, thrust values, masses, dimensions, and costs between specs.

---

## Step-by-Step Sync Runbook

### Step 1: Detect Active Modifications
Run the sync checker to locate which file(s) have uncommitted changes:
```bash
python3 .agents/skills/locale-sync/scripts/sync_check.py
```
Review the reported diff chunks, modified cards, and any flagged discrepancies.

### Step 2: Synchronize Counterpart HTML Content
Open the counterpart file and apply the corresponding additions, updates, or removals:
- **Prose**: Translate naturally and faithfully while maintaining dignified, inspiring register fitting for a sovereign state.
- **Titles & Headings**:
  - Hungarian: Sentence case (e.g. *„Hold- és Mars-küldetések”*, *„Delta III B nehéz hordozórakéta”*).
  - English: Title Case (e.g. *“Lunar and Mars Exploration”*, *“Delta III B Heavy Lift Rocket”*).
- **Technical Specs**: Ensure all numerical metrics match (mass in kg, height in m, thrust in kN, cost in USD/Mrd Ft).
- **Watermark & Wireframe Schematics**: Ensure identical SVG image paths (e.g. `../images/wireframes/...`).
- **Section IDs & Classes**: Ensure matching `id` attributes and `class` attributes (`light-bg`, `fade-in`).

### Step 3: Enforce Editorial Policies
During synchronization, strictly adhere to site rules:
1. **No Ampersands**: Use "and" in English and "és" in Hungarian. Never use `&` in titles, card headers, labels, or copy (except established trademarks like `Walker Finance & Insurance Holding` or `R&D`).
2. **Alternating Section Styles**: Top-level page sections must alternate between normal and `light-bg`.
3. **Punctuation & Quotes**:
   - Hungarian: `„...”` (bottom-99 / top-99 quotes), standard hyphens `-` instead of en-dashes `–`.
   - English: `“...”` (curly quotes).

### Step 4: Format Document & Remove Blank Lines
After editing either HTML file, ALWAYS run the formatter to ensure 4-space indentation and 0 blank lines:
```bash
python3 scripts/build_pages.py --format <path/to/page.html>
```
Or format both pages:
```bash
python3 scripts/build_pages.py --format hu/<page>.html
python3 scripts/build_pages.py --format en/<page>.html
```

### Step 5: Verify Parity and Quality
1. Verify locale parity:
   ```bash
   python3 .agents/skills/locale-sync/scripts/sync_check.py <path/to/page.html>
   ```
   Ensure it outputs:
   `[OK] Counterpart page is in sync with structured values, specs, and section styles.`

2. Run copy quality and spell audit:
   ```bash
   python3 .agents/skills/spell-check/scripts/audit.py <path/to/source.html> <path/to/target.html>
   ```
   Ensure it outputs:
   `[SUCCESS] All checks passed! Site copy is 100% clean.`
