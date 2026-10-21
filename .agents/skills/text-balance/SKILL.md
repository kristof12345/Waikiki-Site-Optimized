---
name: text-balance
description: >-
  Audits and unifies component text lengths and browser preview line counts across card rows, grid sections, and peer elements on a page to ensure balanced visual rhythm and consistent component heights.
---

# Component Text Balance Skill

This skill provides the automated inspection tools, visual typography principles, and copyediting techniques for auditing and unifying component text lengths (such as card descriptions within a section row) so that sibling elements maintain approximately equal rendered line counts and balanced visual heights.

---

## When to Use This Skill

Activate this skill when:
- Creating new cards, teaser items, or grid components on an HTML page.
- Reviewing pages where card heights look ragged, uneven, or vertically misaligned in browser preview.
- Editing existing copy in a section row where one card has significantly fewer or more lines than its peers (e.g., 2 lines next to 6 lines).
- Ensuring bilingual symmetry so that both Hungarian and English versions exhibit balanced component rows.

---

## Core Visual Balancing Principles

1. **Visual Parity Over Exact Counts**:
   - The goal is **not exact character matching**, but **visual line count harmony** ($\pm 1$ line tolerance).
   - If a row of 3 cards has descriptions of 4, 4, and 5 lines, they look cohesive and balanced.
   - If a card has 2 lines while its neighbors have 6 lines, the layout looks uneven and empty.
2. **Peer Group Context**:
   - Sibling cards within the same `<section>` or `.cards` container share a visual row on desktop screens and must be harmonized together.
3. **Bilingual Coordination**:
   - After balancing a section in one language, synchronize the corresponding adjustments to the counterpart page using `locale-sync`.

---

## Automated Text Balance Auditor

The workspace includes a dedicated inspection script supporting both static analysis and live headless Chrome browser rendering (which **always evaluates at 2560px width**):

```bash
# 1. Audit text balance on a specific page (static line estimation based on 2560px desktop grid width)
python3 .agents/skills/text-balance/scripts/text_balance.py hu/space-research.html

# 2. Audit with live headless Chrome for exact pixel-rendered line counts at 2560px width
python3 .agents/skills/text-balance/scripts/text_balance.py --browser hu/space-research.html

# 3. Only display sections with imbalanced rows (variance >= 2 lines)
python3 .agents/skills/text-balance/scripts/text_balance.py --imbalanced hu/space-research.html

# 4. Audit all pages across the website
python3 .agents/skills/text-balance/scripts/text_balance.py --all
```

### What the Auditor Reports:
- **Rendered Line Count**: Calculated live via browser DOM `Range.getClientRects()` at the canonical 2560px desktop width, or calibrated desktop column character estimation (~52 chars/line for 3-column cards).
- **Line Variance**: Difference between the shortest and longest card in each section. Sections with variance $\ge 2$ lines are flagged as `[IMBALANCED]`.
- **Target Line Count**: Recommended unified line count (average of the row) and specific suggestions for each card (`+1 lines, trim text` or `-2 lines, expand text`).

---

## Step-by-Step Text Harmonization Workflow

### Step 1: Run the Text Balance Auditor
Run the script on the target page:
```bash
python3 .agents/skills/text-balance/scripts/text_balance.py hu/<page>.html
```
Identify any sections flagged with `[IMBALANCED]`.

### Step 2: Note the Harmonization Target
Review the reported target line count and character range for the imbalanced section.
Example output:
```text
Section #fleet [IMBALANCED] — 12 Cards (Live Browser Render)
Spread: 7 to 10 lines (Variance: 3 lines, Avg: 7.8 lines)
  Card  1: 10 lines | 384 chars | (+2 lines, trim text)     Delta III A
  Card  2:  8 lines | 302 chars | (balanced target)         Space Shuttle
  Card  6:  7 lines | 285 chars | (-1 lines, expand text)   Delta III B
  * Harmonization Target: Unify cards in #fleet to approximately ~8 lines (~360-420 chars).
```

### Step 3: Edit and Harmonize Copy
- **To Trim (+2 lines)**: Remove filler words, condense compound sentences, or move secondary technical details into the card's `spec-list`.
- **To Expand (-2 lines)**: Add one sentence describing the operational significance, technological distinction, or strategic role.

### Step 4: Synchronize to Counterpart Language
Apply symmetrical adjustments to the opposite language page (`hu/` $\leftrightarrow$ `en/`), and verify parity:
```bash
python3 .agents/skills/locale-sync/scripts/sync_check.py hu/<page>.html
```

### Step 5: Format Document & Final Verification
Format the HTML files (4-space indentation, 0 empty lines) and re-run the balance check:
```bash
python3 scripts/build_pages.py --format hu/<page>.html en/<page>.html
python3 .agents/skills/text-balance/scripts/text_balance.py hu/<page>.html
python3 .agents/skills/spell-check/scripts/audit.py hu/<page>.html en/<page>.html
```
Expected output:
```text
[SUCCESS] All component rows and cards exhibit unified visual line balance!
```
