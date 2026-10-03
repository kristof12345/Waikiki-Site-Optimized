# Sovereign Nation of Waikiki — Technical Architecture
**Modular Static Site Architecture & Build Engine**
*Version 3.0 · Sovereign Identity & Modern Web Standard*

---

## 1. Architectural Philosophy

The Sovereign Nation of Waikiki web portal is engineered as a high-performance, resilient, zero-dependency static web platform with an automated templating and build system. It pairs pure semantic HTML5 with custom CSS custom properties, an organic motion engine in vanilla JavaScript, and an idempotent Python automation pipeline.

### Core Principles
1. **Zero External Runtime Frameworks**: Zero bloat, instant first contentful paint (< 250ms), and full CDN cacheability.
2. **Component-Based Chrome Injection**: Standardized site header, subnavigation rail, section rails, next-chapter cards, and footer injected via `scripts/build_pages.py`.
3. **Dual-Locale Parity**: Perfect 1:1 structural symmetry between English (`en/`) and Hungarian (`hu/`) subtrees.
4. **Resilient Theme Engine**: High-fidelity *Tropical Luxe* default with an instant, non-flashing *Lagoon Night* dark mode backed by CSS variables and local storage.

---

## 2. Directory Structure

```
/
├── css/
│   ├── common.css          # Master design system: tokens, typography, header, footer, animations
│   ├── index.css           # Landing & portal specific layouts
│   ├── society.css         # Interactive province SVG map, city markers, administrative cards
│   ├── economy.css         # Chart containers, comparison bars, financial data cards
│   ├── wealth-fund.css     # Sovereign wealth fund timeline, asset distribution styles
│   ├── citizenship.css     # Immigration screening tier cards, assessment modal
│   ├── bio.css             # Royal biography typography, quote blocks, narrative styling
│   ├── detailed.css        # Detailed ministerial profile cards, portfolio galleries
│   ├── government.css      # Executive branch, cabinet, and state organ styling
│   ├── history.css         # National historical era milestones and timeline markers
│   ├── ideology.css        # Waikiki First foundational principles and visual chambers
│   ├── private.css         # Royal couple chapters (wine, lagoon, deep-sea, and brass themes)
│   ├── sights.css          # Architectural sights, mega-structures, tourism showcase
│   ├── gallery.css         # Media gallery grid, filtering toolbar, lightbox
│   └── tailwind.css        # Utility extensions and interactive AI chatbot styling
├── js/
│   ├── common.js           # Master motion engine: header, theme toggle, curtain, scroll reveals
│   ├── economy.js          # Chart.js economic data models, GDP growth and export visualizations
│   ├── wealth-fund.js      # Wealth fund asset allocation charts and portfolio dynamics
│   ├── citizenship.js      # Interactive citizenship eligibility assessment calculator
│   ├── gallery.js          # Fullscreen responsive gallery viewer and category filters
│   └── chart.min.js        # Standalone Chart.js library
├── scripts/
│   └── build_pages.py      # Idempotent automated page builder & chrome injection engine
├── en/                     # 41 English localized pages
│   ├── index.html          # Main English national portal
│   ├── overview.html       # Sovereign overview & executive summary
│   ├── society.html        # Society, provinces, and interactive administrative map
│   ├── economy.html        # National economic indicators & trade data
│   ├── bio/                # Royal family biographies (Angelina, Raimondo, Selena, Taylor)
│   └── ...                 # 36 additional English topic pages
├── hu/                     # 41 Hungarian localized pages
│   ├── index.html          # Main Hungarian national portal
│   ├── overview.html       # Nemzeti áttekintés
│   ├── society.html        # Társadalom, tartományok és térkép
│   ├── economy.html        # Nemzetgazdaság és kereskedelmi adatok
│   ├── bio/                # Királyi életrajzok
│   └── ...                 # 36 additional Hungarian topic pages
├── images/                 # Optimized high-resolution photography & web assets
├── icons/                  # Vector heraldic symbols (icons/logo.svg), flags, coat of arms
├── index.html              # Multi-lingual entry portal (English & Magyar selector)
├── STYLE-GUIDELINES.md     # Visual design system, token catalog, and typography rules
└── ARCHITECTURE.md         # This document
```

---

## 3. Automated Chrome Injection Pipeline (`scripts/build_pages.py`)

To ensure maintenance scalability without introducing heavy SSG (Static Site Generator) build dependencies, the site utilizes `scripts/build_pages.py`. 

### Chrome Injection Markers
Each localized HTML document contains semantic HTML comments delimiting site chrome:
- `<!-- @chrome:head -->`: Meta tags, OpenGraph tags, Google Fonts (`Fraunces` + `Manrope`), master stylesheets.
- `<!-- @chrome:header -->`: Fixed glass navigation bar, sovereign brand insignia, navigation links, locale switch button, dark mode toggle, hamburger trigger, and fullscreen overlay menu.
- `<!-- @chrome:subnav -->`: Dynamic sticky pill subnavigation rail extracted from the page's `<section id="...">` headings.
- `<!-- @chrome:next -->`: Curated next-chapter card inviting users forward into sequential chapters of the national archive.
- `<!-- @chrome:footer -->`: Sovereign footer, wave divider, categorized links, copyright, and floating back-to-top button.

### Execution Modes
```bash
# Preview changes without modifying files (returns exit code 0)
python3 scripts/build_pages.py --check

# Build and synchronize all 82 subpages
python3 scripts/build_pages.py
```

---

## 4. Master Motion Engine (`js/common.js`)

The front-end engine is built in native vanilla ES6+, completely event-driven and modular:

```
┌─────────────────────────────────────────────────────────────┐
│                    Master Motion Engine                     │
├─────────────────┬──────────────────────┬────────────────────┤
│  Theme Manager  │    Smart Header      │   Page Curtain     │
│  (Light/Night)  │  (Scroll direction,  │  (Smooth internal  │
│                 │   compact mode)      │   page navigation) │
├─────────────────┼──────────────────────┼────────────────────┤
│  Scroll Reveal  │   Counter Animator   │   Spotlight Hover  │
│  (Word-split &  │ (Easing numerical    │  (Mouse radial     │
│   fade-in)      │  count-up)           │   gradient tracks) │
├─────────────────┼──────────────────────┼────────────────────┤
│  Overlay Menu   │   Progress FAB       │   Section Rails    │
│  (With live     │ (SVG circular        │  (Automated deep   │
│   Havana clock) │  scroll progress)    │   page navigation) │
└─────────────────┴──────────────────────┴────────────────────┘
```

### Motion Modules
1. **Curtain Transit Engine (`initPageTransitions`)**:
   - Intercepts internal document links, slides a sleek glass curtain upward, and executes instant location switching for an app-like seamless cadence.
2. **Smart Header Controller (`initHeader`)**:
   - Listens to scroll delta via passive event listeners. Shrinks to compact mode after 40px; slides up and conceals upon rapid downward scrolling; reveals instantly upon scroll-up.
3. **Split-Text Reveal (`initScrollAnimations`)**:
   - Identifies titles with `.split-word` or `.hero-title` and partitions words into individual CSS translated spans with staggered delay timing.
4. **Spotlight Tracking (`initCardEffects`)**:
   - Calculates relative cursor coordinates within cards and updates `--mouse-x` and `--mouse-y` custom properties in real time, rendering a tactile glass reflection.
5. **Back-to-Top with Progress Ring (`initBackToTop`)**:
   - Calculates `scrollTop / (scrollHeight - clientHeight)` and updates the SVG `stroke-dashoffset` in real-time, providing immediate visual feedback of reading progress.
6. **Live Nova Aurelia Time Clock (`initClock`)**:
   - Displays real-time synchronized Atlantic/Havana standard time in the fullscreen overlay drawer.

---

## 5. Performance, Accessibility & SEO

- **CSS Bundling**: Core design system consolidated in `css/common.css` with page-specific modular sheets (`css/society.css`, `css/economy.css`, etc.) for optimal browser caching.
- **Resource Hints**: Google Fonts preconnected with `crossorigin`; hero imagery loaded with `fetchpriority="high"` and below-the-fold media tagged with `loading="lazy"`.
- **Search Engine Optimization**: Every page features localized metadata (`og:title`, `og:description`, `og:locale`, `canonical`, and `hreflang` alternates).
- **Reduced Motion Support**: Fully respects `@media (prefers-reduced-motion: reduce)` by immediately rendering all split-word, curtain, and counter states in their completed positions.
