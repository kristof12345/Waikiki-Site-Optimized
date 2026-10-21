# Responsive Layout, Viewports & Contrast Guidelines

This reference documents the architectural guidelines, responsive viewport standards, and visual contrast rules for the Sovereign Nation of Waikiki portal.

---

## 1. Canonical Viewport Matrix

All site pages are audited across three standard viewports:

| Viewport Profile | Width × Height | Device Class / Purpose | Key Layout Invariants |
| :--- | :--- | :--- | :--- |
| **Ultra-wide Desktop** | `2560 × 1440` | 27" 4K/5K displays, iMac | Primary desktop-first base width (`--width-full`, `--width-xl`). |
| **Standard Desktop** | `1280 × 800` | 13-14" laptops, tablets landscape | Intermediate breakpoint (`@media (max-width: 1280px)`). |
| **Mobile Phone** | `430 × 932` | Modern smartphones (e.g. iPhone Pro Max / Plus) | Single-column stacks, mobile menu, touch buttons. |

---

## 2. Preventing Horizontal Viewport Spills

A horizontal viewport scrollbar on mobile or desktop is an unacceptable defect:
1. **Never use fixed pixel widths on containers**: Use `width: 100%`, `max-width: ...`, or `min(100%, ...)`.
2. **Prevent flex child overflow**: Flex items default to `min-width: auto`. Add `min-width: 0` to flex children that contain text or images to allow proper shrinking.
3. **Handle Long Words / URLs**: Ensure text containers include `overflow-wrap: break-word` or `word-break: break-word`.
4. **SVG & Image Max-Width**: Ensure all `img` and `svg` elements are constrained (`max-width: 100%; height: auto;`).

---

## 3. Container & Text Clipping Safeguards

1. **Avoid Fixed Heights on Text Containers**: Never set `height: 200px` on cards containing dynamic or bilingual prose. Use `min-height` or let flexbox/grid naturally determine card height.
2. **Line Clamping (`-webkit-line-clamp`)**: If intentional text truncation is required, ensure `-webkit-box-orient: vertical`, `display: -webkit-box`, and proper `overflow: hidden`.
3. **Spec Badges & Chips**: Ensure inline badges (`.spec-badge`, `.tag`, `.chip`) have `white-space: nowrap` or wrap cleanly without overflowing their parent card.

---

## 4. Element Collision & Overlap Prevention

1. **Relative vs. Absolute Stacking**: Only purely decorative assets (e.g. `.aircraft-watermark`, background gradients) may be positioned absolutely with `pointer-events: none` and `z-index: 0`.
2. **Interactive Elements**: Buttons, card headers, links, and forms must always remain in normal document flow or have unambiguous stacking contexts (`z-index`) without overlapping neighbor cards.

---

## 5. WCAG 2.1 Color Contrast Standards

Both Light Mode and Dark Mode (`.body-dark`) must satisfy WCAG AA contrast standards:

| Text Type | Font Size / Weight | Minimum Contrast Ratio |
| :--- | :--- | :--- |
| **Normal Text** | Below 24px regular, or below 18.66px bold | **$\ge 4.5:1$** |
| **Large Text** | 24px+ regular, or 18.66px+ bold | **$\ge 3.0:1$** |
| **UI Components & Icons** | Essential borders and form controls | **$\ge 3.0:1$** |

### Theme Variable Token Mappings:
- **Light Mode**: Text uses `--text` (`#2d3748`) on `--bg` (`#fbf7f0`), Headings use `--heading` (`#0f172a`).
- **Dark Mode (`.body-dark`)**: Text uses `--dark-text` (`#cbd5e1`) on `--neutral-900` (`#0a192f`), Headings use `--dark-heading` (`#f8fafc`).
- **Accent Elements**: Accent badges and links (`--primary`, `--accent`) must be verified on both light and dark backgrounds.
