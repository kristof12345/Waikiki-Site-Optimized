#!/usr/bin/env python3
"""
Rebuild the shared page chrome for every localized page of the Waikiki site.

What it does for each page in en/, hu/, en/bio/ and hu/bio/:
  * <head>    injects SEO meta, fonts, hreflang links and the no-flash theme script
  * header    brand, primary navigation, language pill, theme toggle, menu button
  * menu      full-screen grouped site map with live capital clock
  * hero      converts legacy hero markup into the unified `.hero` component
  * subnav    tab bar between the four pages of each royal couple
  * next      "continue the journey" banner linking to the next page
  * footer    grouped site map, motto, legal line
  * colours   maps the legacy blue palette to the Tropical Luxe palette in
              HTML, page CSS and page JS (idempotent)

Generated regions are wrapped in <!-- @chrome:NAME --> markers so the script can
be re-run safely after menu or copy changes:

    python3 scripts/build_pages.py            # rebuild everything
    python3 scripts/build_pages.py --check    # report pages that would change
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "hu")

# --------------------------------------------------------------------------- #
# Site map
# --------------------------------------------------------------------------- #
GROUPS = [
    ("nation", {"en": "Nation", "hu": "Nemzet"}, [
        ("index", {"en": "Home", "hu": "Főoldal"}),
        ("overview", {"en": "Overview", "hu": "Áttekintés"}),
        ("history", {"en": "History", "hu": "Történelem"}),
        ("society", {"en": "Society", "hu": "Társadalom"}),
        ("culture", {"en": "Culture", "hu": "Kultúra"}),
        ("ideology", {"en": "Waikiki First", "hu": "Waikiki Első"}),
    ]),
    ("governance", {"en": "Governance", "hu": "Kormányzás"}, [
        ("government", {"en": "Government", "hu": "Kormány"}),
        ("leadership", {"en": "Leadership", "hu": "Vezetés"}),
        ("parties", {"en": "Politics", "hu": "Politika"}),
        ("constitution", {"en": "Constitution", "hu": "Alkotmány"}),
        ("citizenship", {"en": "Citizenship", "hu": "Állampolgárság"}),
        ("military", {"en": "Military", "hu": "Hadsereg"}),
        ("diplomacy", {"en": "Diplomacy", "hu": "Diplomácia"}),
    ]),
    ("prosperity", {"en": "Prosperity", "hu": "Jólét"}, [
        ("economy", {"en": "Economy", "hu": "Gazdaság"}),
        ("wealth-fund", {"en": "Wealth Fund", "hu": "Vagyonalap"}),
        ("plane", {"en": "Diplomatic Fleet", "hu": "Diplomáciai Flotta"}),
    ]),
    ("royal", {"en": "Royal Family", "hu": "Királyi Család"}, [
        ("dynasty", {"en": "The Dynasty", "hu": "A Dinasztia"}),
        ("chease-and-jessica", {"en": "Chease and Jessica", "hu": "Chease és Jessica"}),
        ("raimondo-and-selena", {"en": "Raimondo and Selena", "hu": "Raimondo és Selena"}),
        ("angelina-and-taylor", {"en": "Angelina and Taylor", "hu": "Angelina és Taylor"}),
        ("jennifer-and-tyler", {"en": "Jennifer and Tyler", "hu": "Jennifer és Tyler"}),
    ]),
    ("visit", {"en": "Visit", "hu": "Látogatás"}, [
        ("tourism", {"en": "Tourism", "hu": "Turizmus"}),
        ("sights", {"en": "Sights", "hu": "Látnivalók"}),
        ("faq", {"en": "FAQ", "hu": "GYIK"}),
    ]),
]

PRIMARY_NAV = [
    ("tourism", {"en": "Visit", "hu": "Utazás"}),
    ("society", {"en": "Society", "hu": "Társadalom"}),
    ("economy", {"en": "Economy", "hu": "Gazdaság"}),
    ("government", {"en": "Government", "hu": "Kormány"}),
    ("history", {"en": "History", "hu": "Történelem"}),
    ("dynasty", {"en": "Royal Family", "hu": "Királyi Család"}),
]

COUPLES = ["chease-and-jessica", "raimondo-and-selena", "angelina-and-taylor", "jennifer-and-tyler"]
COUPLE_TABS = [
    ("", {"en": "Overview", "hu": "Áttekintés"}),
    ("-detailed", {"en": "Story", "hu": "Történet"}),
    ("-gallery", {"en": "Gallery", "hu": "Galéria"}),
    ("-private", {"en": "Private Life", "hu": "Magánélet"}),
]
BIOS = ["bio/raimondo", "bio/selena", "bio/angelina", "bio/taylor"]

# Reading order used for the "next chapter" banner.
SEQUENCE: list[str] = []
for _, _, _pages in GROUPS:
    for _slug, _ in _pages:
        SEQUENCE.append(_slug)
        if _slug == "dynasty":
            SEQUENCE.extend(BIOS)
        if _slug in COUPLES:
            SEQUENCE.extend(f"{_slug}{suffix}" for suffix, _ in COUPLE_TABS[1:])

# Short leads for pages that have no photographic hero.
COMPACT_LEADS = {
    "constitution": {
        "en": "The founding charter of the Sovereign Nation of Waikiki, adopted by referendum in 2000, defining the rights of citizens and the separation of powers.",
        "hu": "Waikiki Szuverén Állam alapító okirata, amelyet 2000-ben népszavazással fogadtak el, és amely rögzíti az állampolgárok jogait és a hatalmi ágak szétválasztását.",
    },
    "overview": {
        "en": "Three provinces, one nation and a quarter century of extraordinary growth: the essential facts about Waikiki at a glance.",
        "hu": "Három tartomány, egy nemzet és negyedszázadnyi rendkívüli fejlődés: Waikiki legfontosabb tényei egy pillantásra.",
    },
    "faq": {
        "en": "Clear answers to the questions most often asked about Waikiki's government, economy, society and way of life.",
        "hu": "Világos válaszok a Waikiki kormányzatával, gazdaságával, társadalmával és életmódjával kapcsolatos leggyakoribb kérdésekre.",
    },
}

T = {
    "skip": {"en": "Skip to content", "hu": "Ugrás a tartalomra"},
    "tagline": {"en": "Sovereign Nation", "hu": "Szuverén Állam"},
    "home": {"en": "Waikiki home", "hu": "Waikiki főoldal"},
    "primary": {"en": "Primary", "hu": "Fő navigáció"},
    "menu": {"en": "Menu", "hu": "Menü"},
    "close": {"en": "Close", "hu": "Bezárás"},
    "theme": {"en": "Toggle night mode", "hu": "Éjszakai mód váltása"},
    "night": {"en": "Night mode", "hu": "Éjszakai mód"},
    "clock_label": {"en": "Local time in the capital", "hu": "Helyi idő a fővárosban"},
    "clock_city": {"en": "Nova Aurelia, Waikiki Province", "hu": "Nova Aurelia, Waikiki tartomány"},
    "weather": {"en": "Sunny", "hu": "Napos"},
    "weather_temp": {"en": "28°C", "hu": "28°C"},
    "motto": {
        "en": "Prosperity, stability and progress, from the Caribbean to the Amazon.",
        "hu": "Jólét, stabilitás és haladás, a Karib-tengertől az Amazonasig.",
    },
    "about": {
        "en": "The official portal of the Sovereign Nation of Waikiki. Founded 10 March 1999 · Nova Aurelia. This site was generated with AI, any resemblance to real people, countries or institutions is just a coincidence.",
        "hu": "Waikiki Szuverén Állam hivatalos portálja. Alapítva 1999. március 10-én · Nova Aurelia. Ez az oldal mesterséges intelligenciával készült, bármilyen hasonlóság valós személyekhez, országokhoz vagy intézményekhez pusztán a véletlen műve.",
    },
    "rights": {
        "en": "© 2026 The Sovereign Nation of Waikiki. All rights reserved.",
        "hu": "© 2026 Waikiki Szuverén Állam. Minden jog fenntartva.",
    },
    "to_top": {"en": "Back to top", "hu": "Vissza a tetejére"},
    "scroll": {"en": "Scroll", "hu": "Görgetés"},
    "continue": {"en": "Continue the journey", "hu": "Folytassa az utazást"},
    "royal_nav": {"en": "Royal couple pages", "hu": "A királyi pár oldalai"},
    "lang_name": {"en": "English", "hu": "Magyar"},
    "animate": {"en": "Toggle animations", "hu": "Animációk ki-/bekapcsolása"},
    "animate_chip": {"en": "Animate", "hu": "Animáció"},
    "animate_label": {"en": "Animate", "hu": "Animáció"},
}

LEGACY_COLOURS = {
    "0071BC": "11605B",
    "0E308E": "0B3B3A",
    "00B0C3": "4FB3A9",
    "BC9200": "C95A41",
    "0A1930": "072221",
    "F5F9FC": "F5EDE1",
    "555555": "4A5957",
    "2E75B6": "11605B",
    "8BC34A": "7CC6BC",
    "F39C12": "E3735A",
    "F1C40F": "E9B872",
    "5DADE2": "2A8C83",
    "C0392B": "B5523B",
    "9B59B6": "8A6F9E",
    "7D6608": "C29A57",
    "27AE60": "5E8C61",
    "0F2442": "0E2423",
    "0D1F3A": "0E2423",
    "0D2238": "0E2423",
    "11243A": "112A28",
    "0D1B2C": "0A1C1B",
    "8FD3FF": "7CC6BC",
}
LEGACY_RGB = {
    "0, 113, 188": "17, 96, 91",
    "0, 113, 187": "17, 96, 91",
    "14, 48, 142": "11, 59, 58",
    "188, 146, 0": "201, 90, 65",
    "195, 176, 0": "201, 90, 65",
    "10, 25, 48": "7, 34, 33",
    "0, 176, 195": "79, 179, 169",
    "2, 8, 20": "4, 18, 17",
    "143, 211, 255": "124, 198, 188",
    "16, 33, 53": "17, 42, 40",
}

LOGO_FILE = "icons/logo.svg"

GLOBE_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>'
)

THEME_ICON = (
    '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<mask id="theme-mask"><rect width="24" height="24" fill="#fff"/><circle class="theme-cut" cx="26" cy="2" r="6" fill="#000"/></mask>'
    '<circle class="theme-core" cx="12" cy="12" r="5" fill="currentColor" mask="url(#theme-mask)"/>'
    '<g class="theme-rays" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">'
    '<path d="M12 1.5v2.2M12 20.3v2.2M1.5 12h2.2M20.3 12h2.2M4.6 4.6l1.5 1.5M17.9 17.9l1.5 1.5M4.6 19.4l1.5-1.5M17.9 6.1l1.5-1.5"/>'
    "</g></svg>"
)

ANIMATE_ICON = (
    '<svg class="animate-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<polygon points="6 4 18 12 6 20 6 4" fill="currentColor"/>'
    "</svg>"
)

FOOTER_WAVE = (
    '<svg class="footer-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true">'
    '<path d="M0 50c160 0 160-36 320-36s160 36 320 36 160-36 320-36 160 36 320 36 160-36 160-36V90H0z"/></svg>'
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def esc(text: str) -> str:
    return html.escape(text, quote=True)


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", fragment)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def label_for(slug: str, locale: str) -> str | None:
    for _, _, pages in GROUPS:
        for page_slug, labels in pages:
            if page_slug == slug:
                return labels[locale]
    return None


def group_for(slug: str) -> str:
    base = slug.split("/")[-1]
    if slug.startswith("bio/") or base == "raimondo-and-bailey-detailed":
        return "royal"
    for couple in COUPLES:
        if base.startswith(couple):
            return "royal"
    for key, _, pages in GROUPS:
        if any(page_slug == base for page_slug, _ in pages):
            return key
    return "nation"


def group_label(key: str, locale: str) -> str:
    for group_key, labels, _ in GROUPS:
        if group_key == key:
            return labels[locale]
    return ""


def couple_for(slug: str) -> str | None:
    for couple in COUPLES:
        if slug == couple or any(slug == f"{couple}{suffix}" for suffix, _ in COUPLE_TABS[1:]):
            return couple
    return None


class Page:
    """A localized page and its path context."""

    def __init__(self, path: Path):
        self.path = path
        rel = path.relative_to(ROOT)
        self.locale = rel.parts[0]
        self.slug = "/".join(rel.parts[1:])[: -len(".html")]
        self.depth = len(rel.parts) - 1  # en/x.html -> 1, en/bio/x.html -> 2
        self.root_prefix = "../" * self.depth
        self.locale_prefix = "../" * (self.depth - 1)
        self.group = group_for(self.slug)

    def href(self, slug: str) -> str:
        return f"{self.locale_prefix}{slug}.html"

    def other_locale_href(self) -> str:
        other = "hu" if self.locale == "en" else "en"
        return f"{self.root_prefix}{other}/{self.slug}.html"

    def asset(self, path: str) -> str:
        return f"{self.root_prefix}{path}"

    def brand_mark(self, curtain: bool = False, footer: bool = False) -> str:
        src = self.asset("icons/logo.svg")
        size = 64 if curtain else 44
        loading = "lazy" if footer else "eager"
        return f'<img class="brand-mark" src="{src}" alt="Waikiki" width="{size}" height="{size}" loading="{loading}" decoding="async" />'


# --------------------------------------------------------------------------- #
# Chrome builders
# --------------------------------------------------------------------------- #
def build_head(page: Page, description: str) -> str:
    other = "hu" if page.locale == "en" else "en"
    lines = [
        "<!-- @chrome:head -->",
        f'<meta name="description" content="{esc(description)}" />' if description else "",
        '<meta name="theme-color" content="#fbf7f0" />',
        f'<link rel="alternate" hreflang="{page.locale}" href="{page.slug.split("/")[-1]}.html" />',
        f'<link rel="alternate" hreflang="{other}" href="{page.other_locale_href()}" />',
        '<link rel="preconnect" href="https://fonts.googleapis.com" />',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..600&family=Manrope:wght@400..800&display=swap" />',
        "<script>(function(d){var h=d.documentElement;h.classList.add('js');try{if(localStorage.getItem('isDarkMode')==='true')h.classList.add('body-dark');"
        "if(localStorage.getItem('isAnimationDisabled')==='true')h.classList.add('no-reveal')}catch(e){}"
        "setTimeout(function(){if(!h.classList.contains('reveal-ready'))h.classList.remove('js')},3500)})(document);</script>",
        "<!-- /@chrome:head -->",
    ]
    return "\n    ".join(line for line in lines if line)


def build_header(page: Page) -> str:
    loc = page.locale
    other = "hu" if loc == "en" else "en"
    nav_links = []
    for slug, labels in PRIMARY_NAV:
        current = ' aria-current="page"' if (slug == page.slug or (slug == "dynasty" and page.group == "royal")) else ""
        nav_links.append(f'<a href="{page.href(slug)}"{current}>{esc(labels[loc])}</a>')

    groups_html = []
    for key, labels, pages in GROUPS:
        items = []
        for slug, page_labels in pages:
            current = ' aria-current="page"' if slug == page.slug or couple_for(page.slug) == slug else ""
            items.append(f'<li><a href="{page.href(slug)}"{current}>{esc(page_labels[loc])}</a></li>')
        groups_html.append(
            f'<div class="menu-group"><h2>{esc(labels[loc])}</h2><ul>{"".join(items)}</ul></div>'
        )

    lang_chips = (
        f'<a class="menu-chip{" is-active" if loc == "en" else ""}" href="{page.root_prefix}en/{page.slug}.html" hreflang="en" lang="en">English</a>'
        f'<a class="menu-chip{" is-active" if loc == "hu" else ""}" href="{page.root_prefix}hu/{page.slug}.html" hreflang="hu" lang="hu">Magyar</a>'
    )

    return f"""<!-- @chrome:header -->
    <div class="page-curtain" aria-hidden="true">{page.brand_mark(curtain=True)}</div>
    <div class="scroll-progress" aria-hidden="true"></div>
    <header class="site-header">
        <a href="{page.href("index")}" class="brand" aria-label="{esc(T["home"][loc])}">{page.brand_mark()}<span class="brand-word">Waikiki</span></a>
        <nav class="primary-nav" aria-label="{esc(T["primary"][loc])}">{"".join(nav_links)}</nav>
        <div class="header-actions">
            <a class="lang-pill" href="{page.other_locale_href()}" hreflang="{other}" lang="{other}" title="{esc(T["lang_name"][other])}">{GLOBE_ICON}<span>{other.upper()}</span></a>
            <button class="icon-btn theme-toggle" type="button" data-theme-toggle aria-pressed="false" aria-label="{esc(T["theme"][loc])}">{THEME_ICON}</button>
            <button class="icon-btn menu-toggle" id="menu-toggle" type="button" aria-expanded="false" aria-controls="site-menu"><span class="menu-lines" aria-hidden="true"></span><span class="menu-label-open">{esc(T["menu"][loc])}</span><span class="menu-label-close">{esc(T["close"][loc])}</span><span class="visually-hidden">{esc(T["menu"][loc])}</span></button>
        </div>
    </header>
    <div class="site-menu" id="site-menu" aria-hidden="true" inert>
        <div class="site-menu-inner">
            <aside class="menu-aside">
                <div class="menu-clock-block">
                    <div class="menu-clock-header">
                        <p class="menu-clock-label">{esc(T["clock_label"][loc])}</p>
                        <div class="menu-weather" data-capital-weather><span class="weather-icon" aria-hidden="true">☀️</span> <span class="weather-temp">{esc(T["weather_temp"][loc])}</span> <span class="weather-desc">{esc(T["weather"][loc])}</span></div>
                    </div>
                    <p class="menu-clock" data-capital-clock>--:--</p>
                    <p class="menu-clock-city">{esc(T["clock_city"][loc])}</p>
                </div>
                <p class="menu-motto">{esc(T["motto"][loc])}</p>
                <div class="menu-aside-row">{lang_chips}<button class="menu-chip" type="button" data-theme-toggle aria-pressed="false">{esc(T["night"][loc])}</button><button class="menu-chip is-active" type="button" data-animate-toggle aria-pressed="true">{esc(T["animate_chip"][loc])}</button></div>
            </aside>
            {"".join(groups_html)}
        </div>
    </div>
    <!-- /@chrome:header -->"""


def build_footer(page: Page) -> str:
    loc = page.locale
    cols = []
    for _, labels, pages in GROUPS:
        items = "".join(f'<li><a href="{page.href(slug)}">{esc(page_labels[loc])}</a></li>' for slug, page_labels in pages)
        cols.append(f'<div class="footer-col"><h2>{esc(labels[loc])}</h2><ul>{items}</ul></div>')
    other = "hu" if loc == "en" else "en"
    return f"""<!-- @chrome:footer -->
    <footer class="site-footer">
        {FOOTER_WAVE}
        <div class="footer-inner">
            <div class="footer-top">
                <div class="footer-brand">
                    <a href="{page.href("index")}" class="brand" aria-label="{esc(T["home"][loc])}">{page.brand_mark(footer=True)}<span class="brand-word">Waikiki</span></a>
                    <p class="footer-motto">{esc(T["motto"][loc])}</p>
                    <p class="footer-about">{esc(T["about"][loc])}</p>
                </div>
                {"".join(cols)}
            </div>
            <span class="footer-mega" aria-hidden="true">Waikiki</span>
            <div class="footer-bottom">
                <p>{esc(T["rights"][loc])}</p>
                <nav aria-label="Language"><a href="{page.other_locale_href()}" hreflang="{other}" lang="{other}">{esc(T["lang_name"][other])}</a><a href="#main">{esc(T["to_top"][loc])} ↑</a></nav>
            </div>
        </div>
    </footer>
    <button class="to-top" type="button" aria-label="{esc(T["to_top"][loc])}"><svg viewBox="0 0 54 54" aria-hidden="true"><circle class="ring-bg" cx="27" cy="27" r="24"/><circle class="ring" cx="27" cy="27" r="24"/></svg><span aria-hidden="true">↑</span></button>
    <!-- /@chrome:footer -->"""


def build_subnav(page: Page) -> str:
    couple = couple_for(page.slug)
    if not couple:
        return "<!-- @chrome:subnav --><!-- /@chrome:subnav -->"
    items = []
    for suffix, labels in COUPLE_TABS:
        slug = f"{couple}{suffix}"
        if not (ROOT / page.locale / f"{slug}.html").exists():
            continue
        current = ' aria-current="page"' if slug == page.slug else ""
        items.append(f'<li><a href="{page.href(slug)}"{current}>{esc(labels[page.locale])}</a></li>')
    return (
        f'<!-- @chrome:subnav --><nav class="subnav" aria-label="{esc(T["royal_nav"][page.locale])}">'
        f'<ul class="subnav-list">{"".join(items)}</ul></nav><!-- /@chrome:subnav -->'
    )


def build_next(page: Page, meta: dict[str, dict]) -> str:
    if page.slug.endswith("-private"):
        target = "dynasty"
        info = meta.get(f"{page.locale}/{target}")
        if info:
            title = label_for(target, page.locale) or info["title"]
            image = info.get("image") or meta.get(f"{page.locale}/index", {}).get("image")
            img_html = f'<div class="next-media"><img src="{page.asset("images/" + image)}" alt="" loading="lazy" decoding="async" /></div>' if image else ""
            eyebrow = f'{T["continue"][page.locale]} · {group_label(group_for(target), page.locale)}'
            return (
                f'<!-- @chrome:next --><section class="next-chapter"><a class="next-card" href="{page.href(target)}">{img_html}'
                f'<span class="next-body"><span class="next-eyebrow">{esc(eyebrow)}</span>'
                f'<span class="next-title">{esc(title)}</span><span class="next-arrow" aria-hidden="true">→</span></span></a></section><!-- /@chrome:next -->'
            )

    if page.slug not in SEQUENCE:
        if page.slug == "raimondo-and-bailey-detailed":
            target = "angelina-and-taylor"
            info = meta.get(f"{page.locale}/{target}")
        else:
            return "<!-- @chrome:next --><!-- /@chrome:next -->"
    else:
        index = SEQUENCE.index(page.slug)
        for offset in range(1, len(SEQUENCE)):
            target = SEQUENCE[(index + offset) % len(SEQUENCE)]
            info = meta.get(f"{page.locale}/{target}")
            if info:
                break
        else:
            return "<!-- @chrome:next --><!-- /@chrome:next -->"

    title = label_for(target, page.locale) or info["title"]
    image = info.get("image") or meta.get(f"{page.locale}/index", {}).get("image")
    img_html = f'<div class="next-media"><img src="{page.asset("images/" + image)}" alt="" loading="lazy" decoding="async" /></div>' if image else ""
    eyebrow = f'{T["continue"][page.locale]} · {group_label(group_for(target), page.locale)}'
    return (
        f'<!-- @chrome:next --><section class="next-chapter"><a class="next-card" href="{page.href(target)}">{img_html}'
        f'<span class="next-body"><span class="next-eyebrow">{esc(eyebrow)}</span>'
        f'<span class="next-title">{esc(title)}</span><span class="next-arrow" aria-hidden="true">→</span></span></a></section><!-- /@chrome:next -->'
    )


# --------------------------------------------------------------------------- #
# Legacy conversion
# --------------------------------------------------------------------------- #
def hero_html(page: Page, *, eyebrow: str, title: str, lead: str | None, image: str | None,
              img_style: str = "", stats: list[tuple[str, str]] | None = None, extra: str = "") -> str:
    loc = page.locale
    parts = ['<section class="hero{}" data-hero>'.format("" if image else " hero--compact")]
    if image:
        alt = esc(strip_tags(title))
        style = f' style="{img_style}"' if img_style else ""
        parts.append(f'<div class="hero-media"><img src="{image}" alt="{alt}"{style} fetchpriority="high" decoding="async" /></div><div class="hero-veil"></div>')
    parts.append('<div class="hero-content">')
    if eyebrow:
        parts.append(f'<span class="hero-eyebrow">{eyebrow}</span>')
    parts.append(f'<h1 class="hero-title">{title}</h1>')
    if lead:
        parts.append(f'<p class="hero-lead">{lead}</p>')
    if extra:
        parts.append(extra)
    if stats:
        parts.append('<div class="hero-stats">' + "".join(
            f'<div class="stat-item"><span class="stat-number">{n}</span><span class="stat-label">{l}</span></div>' for n, l in stats
        ) + "</div>")
    parts.append("</div>")
    if image:
        parts.append(f'<button class="hero-scroll" type="button">{esc(T["scroll"][loc])}</button>')
    parts.append("</section>")
    return "".join(parts)


def tidy_title(title: str) -> str:
    title = re.sub(r'<span style="color:\s*#(?:BC9200|C95A41)"\s*>(.*?)</span>', r"<em>\1</em>", title, flags=re.I | re.S)
    return re.sub(r"\s+", " ", title).strip()


def convert_hero(page: Page, body: str) -> tuple[str, str]:
    """Return (body, lead_text) with the first legacy hero replaced."""
    loc = page.locale
    eyebrow_default = esc(f"{group_label(page.group, loc)} · {label_for(page.slug, loc) or ''}".strip(" ·"))

    # Variant A: <section class="hero" style="background: url(...)">
    match = re.search(r'<section class="hero" style="background: url\(\'([^\']+)\'\)[^"]*">(.*?)</section>', body, re.S)
    if match:
        image, inner = match.group(1), match.group(2)
        title = re.search(r"<h1[^>]*>(.*?)</h1>", inner, re.S).group(1)
        lead_m = re.search(r'<p class="liquid">(.*?)</p>', inner, re.S)
        lead = lead_m.group(1).strip() if lead_m else None
        stats = re.findall(r'<span class="stat-number">(.*?)</span>\s*<span class="stat-label">(.*?)</span>', inner, re.S)
        new = hero_html(page, eyebrow=eyebrow_default, title=tidy_title(title), lead=lead, image=image, stats=stats)
        return body[: match.start()] + new + body[match.end():], strip_tags(lead or "")

    # Variant B: <section class="hero-section"> with hero-bg / badge / title / desc
    match = re.search(r'<section class="hero-section">(.*?)</section>', body, re.S)
    if match:
        inner = match.group(1)
        img = re.search(r'<img src="([^"]+)" class="hero-img"(?: style="([^"]*)")?\s*/?>', inner)
        badge = re.search(r'<div class="hero-badge[^"]*">(.*?)</div>', inner, re.S)
        title = re.search(r'<h1 class="hero-title">(.*?)</h1>', inner, re.S).group(1)
        lead_m = re.search(r'<p class="hero-desc">(.*?)</p>', inner, re.S)
        actions = re.search(r'<div class="hero-actions".*?</div>', inner, re.S)
        image = img.group(1) if img and "TODO" not in img.group(1) else None
        if img and not image:
            image = page.asset("images/" + FALLBACK_IMAGE)
        new = hero_html(
            page,
            eyebrow=badge.group(1).strip() if badge else eyebrow_default,
            title=tidy_title(title),
            lead=lead_m.group(1).strip() if lead_m else None,
            image=image,
            img_style=(img.group(2) or "") if img else "",
            extra=actions.group(0) if actions else "",
        )
        return body[: match.start()] + new + body[match.end():], strip_tags(lead_m.group(1) if lead_m else "")

    # Variant C: no hero — promote the first page heading into a compact hero.
    lead = COMPACT_LEADS.get(page.slug, {}).get(loc)
    heading = re.search(r'<h1 class="faq-title section-title">(.*?)</h1>', body, re.S) or \
        re.search(r'<h2 class="section-title(?: mt-1)?">(.*?)</h2>', body, re.S)
    if heading and page.slug in COMPACT_LEADS:
        new = hero_html(page, eyebrow=eyebrow_default, title=tidy_title(heading.group(1)), lead=esc(lead), image=None)
        body = body[: heading.start()] + body[heading.end():]
        return new + body, lead or ""

    return body, ""


FALLBACK_IMAGE = "UniversalUpscaler_93281a3c-f408-4f55-b29b-e8a6b87ab85d.jpg"


def replace_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(rf"<!-- @chrome:{name} -->.*?<!-- /@chrome:{name} -->", re.S)
    if pattern.search(text):
        return pattern.sub(lambda _: content, text, count=1)
    return text


def map_colours(text: str) -> str:
    for old, new in LEGACY_COLOURS.items():
        text = re.sub(rf"(#|%23){old}\b", lambda m: m.group(1) + new, text, flags=re.I)
    for old, new in LEGACY_RGB.items():
        channels = old.replace(", ", r",\s*")
        text = re.sub(r"(rgba?)\(\s*" + channels + r"(?=\s*[,)])", lambda m, n=new: m.group(1) + "(" + n, text)
    return text


def convert_legacy(page: Page, text: str) -> str:
    """Turn a page with the old nav/hamburger/footer markup into the marker layout."""
    nav_start = text.find('<nav class="nav-container">')
    panel = text.find('<nav class="hamburger-panel">')
    if nav_start == -1 or panel == -1:
        raise ValueError("legacy navigation not found")
    nav_end = text.find("</nav>", panel) + len("</nav>")
    footer_start = text.find("<footer>")
    footer_end = text.find("</footer>", footer_start) + len("</footer>")
    if footer_start == -1:
        raise ValueError("legacy footer not found")

    body = text[nav_end:footer_start]
    body = body.replace("<!-- Hero -->", "")
    body, _ = convert_hero(page, body)

    # Sub-navigation sits right after the hero; the next-chapter banner closes <main>.
    hero_end = body.find("</section>", body.find("data-hero")) + len("</section>") if "data-hero" in body else 0
    body = body[:hero_end] + "\n    <!-- @chrome:subnav --><!-- /@chrome:subnav -->" + body[hero_end:]
    body = body.rstrip() + "\n    <!-- @chrome:next --><!-- /@chrome:next -->\n"

    head_end = text.find("</head>")
    head = text[:head_end]
    head = re.sub(r'(<meta name="viewport"[^>]*>)', r"\1\n    <!-- @chrome:head --><!-- /@chrome:head -->", head, count=1)

    return (
        head + text[head_end:nav_start].rstrip()
        + "\n    <!-- @chrome:header --><!-- /@chrome:header -->\n    <main id=\"main\">"
        + body + "    </main>\n    <!-- @chrome:footer --><!-- /@chrome:footer -->"
        + text[footer_end:]
    )


# --------------------------------------------------------------------------- #
# Page metadata (titles, hero images, descriptions)
# --------------------------------------------------------------------------- #
def page_meta(text: str) -> dict:
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    # Only look at page content, never at generated or legacy navigation.
    if '<main id="main">' in text:
        content = text[text.find('<main id="main">'):]
    elif '<nav class="hamburger-panel">' in text:
        content = text[text.find("</nav>", text.find('<nav class="hamburger-panel">')):]
    else:
        content = text
    content = re.sub(r"<!-- @chrome:(subnav|next) -->.*?<!-- /@chrome:\1 -->", "", content, flags=re.S)
    image = (
        re.search(r'class="hero-media"><img src="[./]*images/([^"]+)"', content)
        or re.search(r"<section class=\"hero[^>]*?url\('[./]*images/([^']+)'", content)
        or re.search(r'class="hero-overlay"></div><img src="[./]*images/([^"]+)"', content)
        or re.search(r'<img src="[./]*images/([^"]+)" class="w-full h-full', content)
    )
    lead = (
        re.search(r'<p class="hero-lead">(.*?)</p>', content, re.S)
        or re.search(r'<p class="liquid">(.*?)</p>', content, re.S)
        or re.search(r'<p class="hero-desc">(.*?)</p>', content, re.S)
        or re.search(r'<p class="narrative-text[^"]*">(.*?)</p>', content, re.S)
        or re.search(r'<p class="text-(?:lg|xl)[^"]*">(.*?)</p>', content, re.S)
        or re.search(r'<p class="section-intro">(.*?)</p>', content, re.S)
    )
    img = image.group(1) if image and "TODO" not in image.group(1) else None
    return {
        "title": strip_tags(title.group(1)) if title else "Waikiki",
        "image": img,
        "lead": strip_tags(lead.group(1)) if lead else "",
    }


def describe(lead: str) -> str:
    if len(lead) <= 158:
        return lead
    cut = lead[:155].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def all_pages() -> list[Path]:
    pages = []
    for locale in LOCALES:
        pages += sorted((ROOT / locale).glob("*.html"))
        pages += sorted((ROOT / locale / "bio").glob("*.html"))
    return pages


def process(path: Path, meta: dict) -> str:
    page = Page(path)
    text = path.read_text(encoding="utf-8")

    if "<!-- @chrome:header -->" not in text:
        text = convert_legacy(page, text)

    info = meta[f"{page.locale}/{page.slug}"]
    outside_chrome = re.sub(r"<!-- @chrome:head -->.*?<!-- /@chrome:head -->", "", text, flags=re.S)
    has_own_description = re.search(r'<meta name="description"', outside_chrome) is not None
    description = "" if has_own_description else describe(info["lead"] or info["title"])

    # Body hooks used by CSS/JS.
    body_classes = f"page-{page.slug.replace('/', '-')} group-{page.group}"
    text = re.sub(r"<body[^>]*>", f'<body class="{body_classes}">', text, count=1)

    # Legacy single-letter logo / font imports / liquid stats are obsolete.
    text = text.replace(' class="stat-item liquid"', ' class="stat-item"')

    text = replace_block(text, "head", build_head(page, description))
    text = replace_block(text, "header", build_header(page))
    text = replace_block(text, "subnav", build_subnav(page))
    text = replace_block(text, "next", build_next(page, meta))
    text = replace_block(text, "footer", build_footer(page))
    text = map_colours(text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="only report pages that would change")
    args = parser.parse_args()

    paths = all_pages()

    # First pass: gather metadata (from current or legacy markup) for cross-links.
    meta = {}
    for path in paths:
        page = Page(path)
        meta[f"{page.locale}/{page.slug}"] = page_meta(path.read_text(encoding="utf-8"))

    changed = 0
    for path in paths:
        try:
            new_text = process(path, meta)
        except Exception as error:  # noqa: BLE001 - report and keep going
            print(f"!! {path.relative_to(ROOT)}: {error}", file=sys.stderr)
            continue
        if new_text != path.read_text(encoding="utf-8"):
            changed += 1
            if args.check:
                print(f"would update {path.relative_to(ROOT)}")
            else:
                path.write_text(new_text, encoding="utf-8")

    # Page-level stylesheets and scripts share the legacy palette too.
    if not args.check:
        for asset in list((ROOT / "css").glob("*.css")) + [ROOT / "js" / n for n in ("economy.js", "wealth-fund.js", "citizenship.js", "dynasty.js", "gallery.js")]:
            if asset.name in ("common.css",) or not asset.exists():
                continue
            original = asset.read_text(encoding="utf-8")
            mapped = map_colours(original)
            if mapped != original:
                asset.write_text(mapped, encoding="utf-8")
                print(f"recoloured {asset.relative_to(ROOT)}")

    print(f"{'Would update' if args.check else 'Updated'} {changed} of {len(paths)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
