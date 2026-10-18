---
name: spell-check
description: >-
  Audits, verifies, and corrects copy quality, spelling, grammar, typography, and project-specific editorial rules across English and Hungarian HTML pages in the Waikiki site. Use this skill whenever checking spelling, auditing copy quality, validating ampersand or whitespace rules, or reviewing text on site pages.
---

# Spell Check & Copy Quality Audit Skill

This skill provides the standard runbook, editorial policies, and automated audit tools for ensuring 100% clean, error-free copy across all pages of the Sovereign Nation of Waikiki site in both English and Hungarian.

---

## When to Use This Skill

Activate this skill when:
- The user requests a spell check, copy audit, or proofreading on one or more pages.
- New HTML pages have been created or existing copy has been modified.
- Checking compliance with project editorial rules (ampersands, empty lines, formatting).
- Reviewing Hungarian orthography (compound hyphenation, en-dashes, accentuation, quotation marks).
- Checking English spelling and style (UK/US variants, macOS NSSpellChecker compliance).

---

## Editorial & Formatting Principles

Before making or reviewing edits, ensure familiarity with:
1. [Editorial & Copy Guidelines](./references/editorial_rules.md) — Ampersand policy, typography standards, Hungarian compound rules, quotation marks, and HTML formatting constraints.
2. [Domain Whitelist & Lore Dictionary](./references/domain_whitelist.md) — Canonical characters, titles, geography, institutions, and technologies.

### Key Rules at a Glance

| Rule | Requirement |
| :--- | :--- |
| **Ampersands** | Prefer **"and"** (English) and **"és"** (Hungarian) over `&` everywhere in headings and prose, except for established brand names (`Walker Finance & Insurance Holding`, `R&D`, `AT&T`). |
| **Whitespace & Typography** | No leading spaces before punctuation (`,`, `.`, `:`, `;`, `?`, `!`). No stray space after `<br>`. No accidental duplicate words. |
| **Quotes** | Hungarian: `„...”` (bottom-99 / top-99). English: `“...”` (curly quotes). Never use straight double quotes `"` in prose. |
| **Dashes** | En-dash (`–`, U+2013) for relational compounds (`Tesla–Waikiki`, `állami–privát`, `orosz–ukrán`) and year/number ranges. Hyphen (`-`) for standard compound words and foreign suffixes. |
| **Hungarian Compounds** | Compound words of 3+ words and >6 syllables require hyphenation at the main boundary (e.g. `infrastruktúra-fejlesztés`, `karate-világbajnokság`). |
| **HTML Formatting** | Exactly 4-space indentation and **0 empty lines** throughout the document. |

---

## Step-by-Step Audit Workflow

### Step 1: Run the Automated Quality Auditor

Execute the audit helper script to automatically scan for typography anomalies, duplicate words, ampersand policy violations, empty lines, Hungarian typos, and English spelling:

```bash
# Audit all pages across both languages
python3 .agents/skills/spell-check/scripts/audit.py

# Audit only Hungarian pages
python3 .agents/skills/spell-check/scripts/audit.py --lang hu

# Audit only English pages
python3 .agents/skills/spell-check/scripts/audit.py --lang en

# Audit specific page(s)
python3 .agents/skills/spell-check/scripts/audit.py hu/index.html hu/overview.html

# Automatically fix safe whitespace & punctuation spacing issues
python3 .agents/skills/spell-check/scripts/audit.py --fix
```

### Step 2: Contextual & Manual Review

Automated tools catch mechanics, but the agent must also evaluate:
- **Tone & Dignity**: Ensure dignified, inspiring, and consistent tone fitting for a sovereign royal state portal.
- **Headings Casing**: In Hungarian, headings and card titles follow sentence casing (e.g. *„Egy példaértékű partnerség”*, *„Közös célban gyökerező szerelem”*).
- **Titles in Prose**: Official titles in running sentences should remain lowercase (e.g. *„waikiki hercegnője”*, *„Waikiki diktátora”*).
- **Names & Suffixes**: Verify proper vowel lengthening (*Isla de la Estrellán*) and proper foreign suffixation (*Baileyvel*, *Taylorral*, *Universityn*).

### Step 3: Format & Clean Pages Post-Edit

Whenever an HTML file is edited:
1. Re-format the document with 4-space indentation and remove blank lines:
   ```bash
   python3 scripts/build_pages.py --format <path/to/page.html>
   ```
2. Or format all pages if multiple were edited:
   ```bash
   python3 scripts/build_pages.py --format --all
   ```

### Step 4: Verification

Re-run the audit script to verify that 0 issues remain:
```bash
python3 .agents/skills/spell-check/scripts/audit.py
```
Expected output:
```text
[SUCCESS] All checks passed! Site copy is 100% clean.
```
