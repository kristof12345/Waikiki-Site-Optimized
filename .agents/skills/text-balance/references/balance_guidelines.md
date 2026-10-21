# Component Text Length & Line Balance Guidelines

This reference details the visual design principles, measurement techniques, and copyediting strategies for keeping component text lengths and line counts visually balanced across grid rows and sibling elements.

---

## 1. The Principle of Visual Balance

In modern responsive layouts, cards, grid teasers, and column blocks are displayed side-by-side in visual rows:
- **Equal-Height Harmony**: When cards in a row have approximately the same amount of text, their paragraphs, spec lists, and action areas align consistently, preventing ragged, staggered bottoms.
- **Rhythm Over Rigidity**: The goal is **not exact character matching**, but **visual line count parity** ($\pm 1$ line tolerance). For example, having cards in a 3-column row take 4, 4, and 5 lines looks harmonious, whereas 2 lines next to 6 lines looks visibly broken.
- **Bilingual Symmetry**: When balancing text on a page, always ensure the corresponding language counterpart (`hu/` <-> `en/`) maintains approximately the same line count balance.

---

## 2. Character-to-Line Reference on Desktop (1440px Viewport)

Standard Waikiki card grids render with the following approximate character capacities:

| Grid Type | Cards per Row | Average Chars per Line | 3-Line Target | 4-Line Target | 5-Line Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **3-Column Grid** (`.card`) | 3 cards / row | ~48 – 54 chars | ~140 – 165 chars | ~190 – 220 chars | ~240 – 275 chars |
| **2-Column Grid** (`.grid-2`) | 2 cards / row | ~75 – 85 chars | ~225 – 255 chars | ~300 – 340 chars | ~375 – 425 chars |
| **Full-Width Intro** | 1 element / row | ~110 – 125 chars | ~330 – 375 chars | ~440 – 500 chars | ~550 – 625 chars |

---

## 3. Techniques for Harmonizing Text Lengths

### A. Condensing Overly Long Text (+2 lines or more)
When a card is significantly taller than its neighbors:
1. **Eliminate Redundant Modifiers**: Remove duplicate adverbs and adjectives that do not add factual value.
2. **Shorten Compound Clauses**: Split or simplify multi-clause sentences; focus on the primary accomplishment, mission, or capability.
3. **Move Technical Data to Spec Lists**: If numerical specifications or partner agencies are embedded in narrative prose, move them to the structured `spec-list` below the paragraph.

### B. Expanding Overly Short Text (-2 lines or less)
When a card is too sparse and creates an empty gap:
1. **Add Purpose or Impact**: State why the project, vehicle, or institution matters (e.g., strategic impact, environmental benefit, historical significance).
2. **Mention Operational Context**: Include timeline milestones, collaborating agencies, or regional focus.
3. **Describe Key Features**: Provide one additional descriptive sentence highlighting a defining attribute.

---

## 4. Verification Workflow

1. Run the static and browser line balance audit:
   ```bash
   python3 .agents/skills/text-balance/scripts/text_balance.py <page.html>
   python3 .agents/skills/text-balance/scripts/text_balance.py --browser <page.html>
   ```
2. Edit flagged cards to bring line counts within the recommended target ($\pm 1$ line).
3. Synchronize adjustments with the counterpart language using `locale-sync`:
   ```bash
   python3 .agents/skills/locale-sync/scripts/sync_check.py <page.html>
   ```
4. Re-format the document:
   ```bash
   python3 scripts/build_pages.py --format <page.html>
   ```
