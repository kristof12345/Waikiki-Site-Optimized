# Agent Workflow & Rules for Sovereign Nation of Waikiki Site

## Editorial & Content Guidelines

1. **Prefer "and" / "és" over ampersand ("&")**: Use the word "and" (in English) and "és" (in Hungarian) instead of the "&" symbol in titles, section headings, card headers, labels, and copy.
2. **Alternating Section Styles**: Top-level page sections must alternate between normal and `light-bg` styles.

## Graphics, SVGs and Icon Guidelines

1. **Complex Graphics and Icons in Separate Files**:
   - All SVG icons (e.g. MDI icons, card icons, location markers, badges, action buttons) must be stored as separate standalone `.svg` files in `icons/mdi/` and linked via `<img>` tags (`<img src="../icons/mdi/<name>.svg" alt="" />`).
   - Complex graphics, network topologies, blueprints, and standalone technical illustrations (e.g., in `icons/banking/`, `icons/space/`, `icons/nature/`) must also be kept as separate files in the `icons/` directory.
2. **Card Grid Arts Directly in HTML**:
   - Card grid artwork and inline card illustrations (such as `.building-art`, `.hotel-art`, `.city-ill-frame`, `.hero-art`, `.ill-panel`, or scenic visuals tied directly to card grid structures) should be directly included inline within the HTML document.
3. **Pure Vector SVGs (No Rasterized Parts)**:
   - All SVGs must consist purely of native vector elements (`<path>`, `<polygon>`, `<rect>`, `<circle>`, `<ellipse>`, `<line>`, vector gradients, SVG patterns, etc.).
   - SVGs should not contain rasterized parts: never embed `<image>` tags, base64 bitmap data URIs (`data:image/png`, `data:image/jpeg`, etc.), or pixel bitmaps inside SVG files or inline SVG markup.

## CSS & Media Query Guidelines

1. **Desktop-First Media Queries**: Write default styles for large screens (desktop). Use `@media (max-width: ...)` queries to adapt for smaller screens, avoiding `min-width` media queries.
2. **Compact CSS Comments**: Keep stylesheet comments concise, single-line, and free of decorative ASCII banners or `=` marks:
   - Remove redundant design system subtitles (e.g., `/* Tropical Luxe and Lagoon Night Design System */` and similar).
   - Simplify stylesheet titles by removing verbose prefixes and suffixes (`/* Sovereign Nation of Waikiki - Royal Family Tree Stylesheet */` » `/* Royal Family Tree Stylesheet */` and similar).
   - Compact multi-line comments into clean, single-line comments without `=` marks.
   - Standardize dark mode comments (`Lagoon Night (Dark Mode) Theme Engine` » `Dark Mode`).

## HTML Page Builds and Edits

After building or editing any HTML page:
1. **Format document**: Format the HTML document with 4-space indentation.
2. **Remove empty lines in document**: Ensure there are no empty/blank lines in the document.

### Automation Utilities

- Format and clean a specific file:
  `python3 scripts/build_pages.py --format <file.html>`
- Format and clean all pages:
  `python3 scripts/build_pages.py --format --all`
- Build pages (automatically formats and strips empty lines):
  `python3 scripts/build_pages.py`
- Structural check (valid tags, tag matching, referenced files, CSS):
  `python3 scripts/build_pages.py --check-structure`
- Copy quality and spell checker (via `spell-check` skill):
  `python3 .agents/skills/spell-check/scripts/audit.py`
- Locale sync checker (via `locale-sync` skill):
  `python3 .agents/skills/locale-sync/scripts/sync_check.py`
- Clean and purge unused CSS (via `clear-css` skill):
  `purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes`
- Publish to all remotes (via `publish` skill):
  `python3 .agents/skills/publish/scripts/publish.py`
- Text length and line balance auditor (via `text-balance` skill):
  `python3 .agents/skills/text-balance/scripts/text_balance.py <file.html>`
- Multi-viewport layout and contrast auditor (via `layout-audit` skill):
  `python3 .agents/skills/layout-audit/scripts/layout_audit.py <file.html>`
