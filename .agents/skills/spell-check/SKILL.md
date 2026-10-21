---
name: spell-check
description: >-
  Audits, verifies, and corrects copy quality, spelling, grammar, typography, domain conventions, and project-specific editorial rules across English and Hungarian HTML pages in the Sovereign Nation of Waikiki site. Use this skill whenever checking spelling, auditing copy quality, validating ampersand or whitespace rules, or reviewing text and language style on site pages.
---

# Spell Check, Copy Quality & Editorial Style Skill

This skill provides the comprehensive runbook, linguistic conventions, editorial policies, and automated audit tools for ensuring 100% clean, error-free, and dignified copy across all pages of the Sovereign Nation of Waikiki site in both English and Hungarian.

---

## When to Use This Skill

Activate this skill when:
- The user requests a spell check, copy audit, proofreading, or language style review on one or more pages.
- New HTML pages have been created or existing copy has been modified.
- Checking compliance with project editorial rules (ampersands, 0 empty lines, 4-space formatting, alternating `light-bg` section classes).
- Reviewing Hungarian orthography (compound hyphenation, en-dashes vs. hyphens, vowel lengthening, proper noun suffixation, quotation marks).
- Checking English spelling and style (UK/US variants, Title Case headings, curly quotes, native macOS NSSpellChecker compliance).
- Validating canonical lore, geography, botanical/ecological biomes, alpine engineering, or aerospace terminology.

---

## Editorial & Formatting Principles

Before making or reviewing edits, consult the canonical references:
1. [Editorial, Style & Orthography Guidelines](./references/editorial_rules.md) — Tone and register, bilingual editorial symmetry, Hungarian orthography, English conventions, ampersand policy, and HTML layout constraints.
2. [Domain Whitelist & Lore Dictionary](./references/domain_whitelist.md) — Canonical characters, royal family, government officials, geography, ecological biomes, botanical and zoological species, space exploration vehicles, alpine technology, and financial institutions.
3. [Companion Skill: Locale Sync](../locale-sync/SKILL.md) — For detecting active changes and synchronizing content and specs between Hungarian and English counterpart pages.

---

### Key Linguistic & Editorial Rules at a Glance

| Rule | Requirement |
| :--- | :--- |
| **Tone & Register** | Formal, dignified, inspiring, and objective state publication register. Avoid colloquialisms, sensationalism, and conversational fillers. |
| **Ampersands** | Always write out **"and"** (English) and **"és"** (Hungarian) instead of `&` in titles, section headings, card headers, labels, and running copy. (Exceptions: `Walker Finance & Insurance Holding`, `R&D`, `AT&T`, HTML entities). |
| **Alternating Section Styles** | Top-level `<section>` elements must alternate strictly between normal and `light-bg` styles. |
| **Headings Casing** | **Hungarian**: Sentence case (capitalize only the first word and proper nouns).<br>**English**: Title Case (capitalize principal words). |
| **Quotes** | **Hungarian**: `„...”` (bottom-99 / top-99). Never use straight double quotes `"` or English `“...”`.<br>**English**: `“...”` (curly quotes). Never use straight `"`. |
| **Dashes & Hyphens** | Use regular hyphen (`-`, U+002D) everywhere. Never use en-dash (`–`, U+2013). Disallow double hyphens in non-date compound words (e.g., `Covid-19 világjárvány` instead of `Covid-19-világjárvány`). Double hyphens permitted for year intervals (e.g., `2002-2004-es`). |
| **Specific Terms** | `Pacifikus háború` $\rightarrow$ `Csendes-óceáni háború`. `COVID-19` $\rightarrow$ `Covid-19`. `zárt körű` $\rightarrow$ `zártkörű`. `infrastruktúrafejlesztés` $\rightarrow$ `infrastruktúra-fejlesztés`. `waikiki-i` $\rightarrow$ `Waikiki-i` (prefer noun phrasing: `Waikiki polgárai`). `Nova Aurélia` $\rightarrow$ `Nova Aurelia` (adjective: `Nova Auréliai`). |
| **A „szuverén” szó** | The word `szuverén` is reserved for the official state name (`Waikiki Szuverén Állam`) and the footer; avoid gratuitous use in body prose (use *önálló*, *független*, *saját*). |
| **Hungarian Suffixation** | Apply vowel lengthening (*Raimondóval*, *Selenával*, *Isla de la Estrellán*) and proper foreign suffix assimilation (*Chease-zel*, *Lautnerrel*, *Baileyvel*). Titles in running prose remain lowercase (*„waikiki hercegnője”*, *„a diktátor rendelete”*). |
| **HTML Formatting** | Exactly 4-space indentation and **0 empty lines** throughout the document. |
| **TODO Markers** | Never alter or remove `TODO` placeholders during copy or spelling audits. |

---

## Step-by-Step Audit Workflow

### Step 1: Run the Automated Quality Auditor

Execute the audit helper script to automatically scan for typography anomalies, duplicate words, ampersand violations, empty lines, Hungarian typos, and English spelling:

```bash
# Audit all pages across both languages
python3 .agents/skills/spell-check/scripts/audit.py

# Audit only Hungarian pages
python3 .agents/skills/spell-check/scripts/audit.py --lang hu

# Audit only English pages
python3 .agents/skills/spell-check/scripts/audit.py --lang en

# Audit specific page(s)
python3 .agents/skills/spell-check/scripts/audit.py hu/space-research.html en/space-research.html

# Automatically fix safe whitespace & punctuation spacing issues
python3 .agents/skills/spell-check/scripts/audit.py --fix
```

### Step 2: Contextual & Stylistic Review

Automated tools catch mechanics, but the agent must evaluate:
- **Tone & Dignity**: Confirm solemn, statesmanlike, and inspiring tone fitting for a sovereign royal state portal.
- **Bilingual Symmetry**: Compare with the counterpart page (`hu/<page>.html` $\leftrightarrow$ `en/<page>.html`) to ensure concepts, numbers, and facts are identically aligned.
- **Domain Accuracy**: Check proper usage of aerospace (rockets, orbital stations), alpine (cryo-grid, tiltrotors), nature (biomes, endemic flora/fauna), and constitutional governance vocabulary.

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

Re-run the audit script and the companion sync check script to verify that 0 issues remain:
```bash
python3 .agents/skills/spell-check/scripts/audit.py
python3 .agents/skills/locale-sync/scripts/sync_check.py
```
Expected output:
```text
[SUCCESS] All checks passed! Site copy is 100% clean.
```
