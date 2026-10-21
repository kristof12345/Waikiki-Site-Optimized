# General Locale Synchronization Guidelines

This document outlines the core principles, structural invariants, and localization methodologies for keeping Hungarian (`hu/`) and English (`en/`) counterpart pages synchronized.

---

## 1. Principles of Semantic Localization

Instead of literal, word-for-word translation:
- **Contextual Translation**: Translate ideas, intent, and domain-appropriate terminology naturally in the target language. Preserve nuance, dignity, and register rather than forcing syntactic symmetry.
- **Domain-Appropriate Idioms**: Use standard industry and domain conventions in the target language (e.g., aerospace, marine, constitutional, economic, or alpine terminology).
- **Tone Consistency**: Maintain a formal, authoritative, and statesmanlike register across both languages.
- **Heading Casing Conventions**:
  - **Hungarian**: Use sentence case for section titles, card headers, and subtitles (capitalize only the first word and proper nouns).
  - **English**: Use Title Case for section titles, card headers, and navigation items.

---

## 2. Quantitative & Numerical Localization

When synchronizing technical metrics, dimensions, costs, and dates:
- **Metric Integrity**: Ensure physical measurements (mass, dimensions, speed, thrust, capacity) represent identical values across both versions.
- **Number Formatting**:
  - **Hungarian**: Use non-breaking space as thousands separator (`180 000`) and comma for decimals (`2,5`). Place currency or unit after the value (`300 millió $`, `120 Mrd Ft`).
  - **English**: Use commas as thousands separator (`180,000`) or consistent space matching template, and period for decimals (`2.5`). Place currency symbols standardly (`$300 Million`, `$2.5 Billion`).
- **Dates & Intervals**:
  - **Hungarian**: Format date ranges with standard hyphen (`2026-2030`).
  - **English**: Format date ranges consistently (`2026-2030` or `2026–2030` matching page style).

---

## 3. Structural & Semantic DOM Invariants

Counterpart pages must preserve 1-to-1 structural parity:
1. **Section Structure**: Top-level `<section>` elements must have matching `id` attributes and must alternate strictly between normal and `light-bg` styles.
2. **Card Grid Symmetry**: Every grid should contain an equal number of cards in both languages, with matching visual components (icons, badges, headings, body text, spec lists).
3. **Asset & Media Parity**: Schematics, SVG wireframes, watermarks, photos, and illustrative diagrams must reference identical asset paths across both locales.
4. **Metadata & Headings**: Page titles should use the standardized national suffix (` — Waikiki Szuverén Állam` in Hungarian, ` — Sovereign Nation of Waikiki` in English).

---

## 4. Post-Synchronization Verification Checklist

Whenever changes are synchronized:
1. Format document with 4-space indentation and strip empty lines:
   ```bash
   python3 scripts/build_pages.py --format <file.html>
   ```
2. Verify structural and numerical parity:
   ```bash
   python3 .agents/skills/locale-sync/scripts/sync_check.py <file.html>
   ```
3. Audit copy quality, punctuation, and ampersands:
   ```bash
   python3 .agents/skills/spell-check/scripts/audit.py <file.html>
   ```
