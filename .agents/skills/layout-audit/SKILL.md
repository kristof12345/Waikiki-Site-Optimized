---
name: layout-audit
description: >-
  Audits and inspects site pages in the browser across multiple viewports (2560px, 1280px, mobile 430px) and color modes (light and dark) for layout defects: overlapping elements, text overflowing containers, horizontal scrollbar spills, and unreadable contrast.
---

# Browser Layout & Visual Contrast Audit Skill

This skill provides the automated inspection tools, multi-viewport browser testing workflows, and responsive guidelines for identifying visual defects across all site pages:
- **Horizontal Viewport Spills**: Content bleeding offscreen causing horizontal scroll on mobile or desktop.
- **Text & Container Clipping**: Text overflowing its containing card or truncated unintentionally.
- **Element Collisions**: Sibling cards, buttons, or headers colliding or overlapping.
- **WCAG Color Contrast**: Text with insufficient contrast ratio in either Light Mode or Dark Mode.
- **Broken Media**: Missing or unrendered images.

---

## When to Use This Skill

Activate this skill when:
- Creating new HTML pages, redesigning sections, or adding new card grids.
- Editing CSS styles, media queries, or theme variable tokens.
- Verifying responsive behavior across desktop (2560px, 1280px) and mobile (430px) viewports.
- Validating legibility in both Light Mode and Dark Mode (`.body-dark`).
- Performing a pre-release quality check before publishing.

---

## Canonical Viewport & Theme Matrix

Every page is systematically tested across 6 distinct conditions (3 viewports $\times$ 2 themes):

| Profile | Dimensions | Mode | Purpose |
| :--- | :--- | :--- | :--- |
| **Desktop Ultra-wide** | `2560 × 1440` | Light Mode | Canonical large desktop baseline (`--width-full`). |
| **Desktop Ultra-wide** | `2560 × 1440` | Dark Mode | High-resolution night theme legibility. |
| **Desktop Standard** | `1280 × 800` | Light Mode | Standard laptop / intermediate breakpoint. |
| **Desktop Standard** | `1280 × 800` | Dark Mode | Laptop night mode contrast and layout. |
| **Mobile Phone** | `430 × 932` | Light Mode | Modern smartphone single-column stack & touch targets. |
| **Mobile Phone** | `430 × 932` | Dark Mode | Modern smartphone OLED dark mode contrast & legibility. |

---

## Automated Layout Auditor

The workspace includes a dedicated Playwright & headless Google Chrome layout auditor script:

```bash
# 1. Audit a single page across all 3 viewports and both light/dark themes (uses Playwright automatically)
python3 .agents/skills/layout-audit/scripts/layout_audit.py hu/overview.html

# Direct Playwright runner via Node:
node .agents/skills/layout-audit/scripts/playwright_audit.js hu/overview.html

# 2. Audit specific viewports (e.g. 2560px and mobile 430px)
python3 .agents/skills/layout-audit/scripts/layout_audit.py --widths 2560,430 hu/space-research.html

# 3. Audit only Dark Mode or only Light Mode
python3 .agents/skills/layout-audit/scripts/layout_audit.py --modes dark hu/plane.html
python3 .agents/skills/layout-audit/scripts/layout_audit.py --modes light hu/plane.html

# 4. Audit all English and Hungarian pages across the entire website
python3 .agents/skills/layout-audit/scripts/layout_audit.py --all

# 5. Export structured JSON results
python3 .agents/skills/layout-audit/scripts/layout_audit.py --json hu/space-research.html
```

---

## What the Auditor Checks

1. **Horizontal Scrollbar Overflow (`scrollWidth > clientWidth`)**:
   - Detects if any element forces the document body wider than the viewport window width, which causes unwanted horizontal scrolling.
   - Flags the specific offending CSS selector and the exact pixel overflow amount.
2. **Text & Content Clipping**:
   - Identifies text elements (`p`, `h1`-`h4`, `.spec-badge`, `.btn`, `li`) where `scrollWidth > clientWidth` or `scrollHeight > clientHeight` when `overflow` is set to `hidden` or `clip`.
3. **Element Collisions & Overlaps**:
   - Bounding rect collision detection among sibling cards, grid items, and text blocks to catch layout overlaps.
4. **WCAG Color Contrast**:
   - Computes the effective background color (traversing up DOM layers to an opaque surface).
   - Calculates relative luminance and contrast ratio according to WCAG 2.1 AA specifications:
     - Normal text ($< 24$px regular, or $< 18.66$px bold): **$\ge 4.5:1$**
     - Large text ($\ge 24$px regular, or $\ge 18.66$px bold): **$\ge 3.0:1$**
5. **Broken Media**:
   - Checks if any `<img>` has natural width or height equal to 0.

---

## Step-by-Step Layout Audit Workflow

### Step 1: Run the Layout Auditor
Run the auditor against the modified page(s):
```bash
python3 .agents/skills/layout-audit/scripts/layout_audit.py hu/<page>.html
```
Examine output for any flagged `[FAIL: ...]` sections.

### Step 2: Diagnose & Fix Issues
- **If Horizontal Overflow is flagged**: Check elements listed under `offendingElements`. Add `max-width: 100%`, `overflow-wrap: break-word`, or `min-width: 0` on flex children.
- **If Text Clipping is flagged**: Remove fixed container heights, adjust line-height, or allow container auto-expansion.
- **If Low Contrast is flagged**: Check CSS custom properties in `.body-dark` or light theme. Adjust color tokens (`--heading`, `--text`, `--primary`, `--tertiary`) to achieve $\ge 4.5:1$ contrast.

### Step 3: Synchronize to Counterpart Page
If HTML or CSS was modified to resolve layout issues, verify that both language versions (`hu/` and `en/`) are updated:
```bash
python3 .agents/skills/locale-sync/scripts/sync_check.py hu/<page>.html
```

### Step 4: Verification
Re-run the layout auditor and verify:
```text
[SUCCESS] All tested viewports and color modes exhibit 100% clean layouts!
No horizontal spills, clipped elements, collisions, or contrast defects found.
```
