# Agent Workflow & Rules for Sovereign Nation of Waikiki Site

## Editorial & Content Guidelines

1. **Prefer "and" / "és" over ampersand ("&")**: Use the word "and" (in English) and "és" (in Hungarian) instead of the "&" symbol in titles, section headings, card headers, labels, and copy.
2. **Alternating Section Styles**: Top-level page sections must alternate between normal and `light-bg` styles.
3. **Realistic Worldbuilding and Plausible Technology (No Too Many Sci-Fi Elements)**: Ground worldbuilding, institutions, defense, infrastructure, and aerospace in realistic, plausible science and engineering. Avoid far-fetched or fantasy tropes across all pages (e.g. no anti-gravity, flying stratospheric airborne supercarriers, or "Skynet" references; avoid interstellar claims for current spaceflight). **Canonical Lore Exceptions**: Retain the canonical Waikiki technologies: the **Intermedic Elixir** (life-extension elixir), **Palladium robots** (and miniature palladium reactors), and **Fusion reactors** (fusion energy grid and facilities).

## Graphics, SVGs and Icon Guidelines

1. **Asset Structure and Generation Classification (All Pages)**:
   - **Card illustrations**: `inline, generated` (e.g. hotel cards, resort cards, landmark cards directly within HTML card grids).
   - **Maps**: `linked, generated` (e.g. interactive ski trail maps, artificial island maps, infrastructure maps).
   - **Other localized**: `linked, generated` (e.g. banking tripartite network and rate corridor, space research station and interplanetary corridor — linked via `<img>` tags with `-en.svg` and `-hu.svg` variants).
   - **Other not localized**: `linked, not generated` (e.g. hero illustrations, nature biomes, Nova Aurelia large illustrations and skyline, rockets, icons/mdi — linked via `<img>` tags to standalone `.svg` files in `icons/`, edited directly and never generated from Python scripts).
2. **Pure Vector SVGs (No Rasterized Parts)**:
   - All SVGs must consist purely of native vector elements (`<path>`, `<polygon>`, `<rect>`, `<circle>`, `<ellipse>`, `<line>`, vector gradients, SVG patterns, etc.).
   - SVGs should not contain rasterized parts: never embed `<image>` tags, base64 bitmap data URIs (`data:image/png`, `data:image/jpeg`, etc.), or pixel bitmaps inside SVG files or inline SVG markup.
3. **No Loading Attribute on Images (Keep Default Eager)**:
   - Do not use `loading="lazy"` or `loading="eager"` attributes on `<img>` tags across site pages. Retain the browser's empty default (no `loading` attribute) so all imagery renders immediately and cleanly without explicit loading properties.

## CSS & Media Query Guidelines

1. **Desktop-First Media Queries**: Write default styles for large screens (desktop). Use `@media (max-width: ...)` queries to adapt for smaller screens, avoiding `min-width` media queries.
2. **Compact CSS Comments**: Keep stylesheet comments concise, single-line, and free of decorative ASCII banners or `=` marks:
   - Remove redundant design system subtitles (e.g., `/* Tropical Luxe and Lagoon Night Design System */` and similar).
   - Simplify stylesheet titles by removing verbose prefixes and suffixes (`/* Sovereign Nation of Waikiki - Royal Family Tree Stylesheet */` » `/* Royal Family Tree Stylesheet */` and similar).
   - Compact multi-line comments into clean, single-line comments without `=` marks.
   - Standardize dark mode comments (`Lagoon Night (Dark Mode) Theme Engine` » `Dark Mode`).
3. **Four-Part Stylesheet Structure**: All CSS stylesheets must strictly follow a 4-part structure in order:
   - **Normal styles** (base components and layout, no new separate section comment line)
   - **Dark mode** (`/* Dark Mode */`)
   - **Responsive** (`/* Responsive */` with desktop-first `@media (max-width: ...)` queries)
   - **Animations** (`/* Animations */` containing `@keyframes` definitions)

## Git & Publishing Guidelines

1. **Never Automatically Push or Publish**: Never run `git push` or execute the `publish` skill (`publish.py`) automatically. Pushing and publishing must only occur when explicitly instructed by the user.

## Visual Testing & Browser Inspection Guidelines

1. **Local HTTP Server Required**: Always serve site files via a local HTTP static server (e.g., `http://127.0.0.1:8080/`) when auditing or capturing screenshots with Playwright / Chrome. Never load via `file://` URLs outside the site root, as relative paths (`../css/`, `../images/`, `../icons/`) will fail or 404.
2. **Progressive Step-by-Step Scrolling with Compositor Sync**:
   - Elements with `data-reveal` (`.card`, `.stat-card`, `.section-title`, `.timeline-item`, etc.) use `IntersectionObserver` with `rootMargin: '0px 0px -5% 0px'`. Cards and content will stay hidden (`opacity: 0`, `transform: translate3d(0, 44px, 0)`) unless scrolled into the viewport.
   - Do not jump instantly to the bottom in a tight JS loop. Scroll down in progressive increments (300–400px) paired with dual `requestAnimationFrame` and a short delay (30–45ms) at each step so Chromium's compositor updates and triggers `.is-in`.
3. **Wait for CSS Transitions and Stagger Delays**:
   - `css/common.css` transitions take `1s–1.2s` with `--delay-increment: 50ms` (staggering up to `--i: 8`).
   - Always wait **at least 2.0–2.2 seconds** after reaching the bottom for all animations, stagger delays, and image decodes to complete before taking screenshots.
4. **Asynchronous Galleries & Lazy Data**:
   - For photo galleries (`*gallery.html`), wait for the Google Apps Script endpoint (`Gallery.init`) to populate `#gallery-grid` before scrolling.
   - Convert `img[loading="lazy"]` to eager, ensure `data-src` is assigned to `src`, and await all `img.decode()` / load events.
5. **Dismiss Curtain & Reset Scroll for Top Viewports**:
   - Dismiss or hide `.page-curtain` (`display: none !important`) so the 1.05s exit animation never obscures screenshots.
   - When capturing full-page or top-of-page screenshots, scroll back to `(0, 0)` and pause (500–600ms) for sticky navigation, header state, and top layout to settle.
6. **Card Visibility Verification**:
   - Verify before taking screenshots that `hiddenCardsCount === 0` and all cards have `opacity: 1` and resting transform (`none`).
7. **Screenshot Location**:
   - Save all visual test screenshots into the gitignored `screenshots/` directory at the repository root. Never commit screenshots to git.

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
