#!/usr/bin/env python3
"""Load the Waikiki Air Force One deck plan SVG into en/plane.html and hu/plane.html."""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SVG_PATH = ROOT / "images" / "planes" / "plane-deck.svg"

DECKPLAN_SVG_RE = re.compile(
    r'(<div class="deckplan-svg-scroll">\s*)<svg\b[^>]*>.*?</svg>(\s*</div>)',
    re.S,
)

# English -> Hungarian replacements applied when injecting into hu/plane.html
EN_TO_HU = [
    (
        'aria-label="Colorful architectural illustration of Waikiki Air Force One Boeing 7107-B two-level luxury deck plan with Antonov An-225 twin-tail outer silhouette and elongated fuselage"',
        'aria-label="Színes építészeti illusztráció a Waikiki Air Force One Boeing 7107-B kétszintes luxus fedélzeti tervrajzáról Antonov An-225 stílusú dupla vezérsíkkal és nyújtott törzzsel"',
    ),
    # Header ribbon widths to fit Hungarian text
    (
        '<rect x="28" y="268" width="560" height="26" rx="13" fill="#c95a41" />',
        '<rect x="28" y="268" width="585" height="26" rx="13" fill="#c95a41" />',
    ),
    (
        '<rect x="28" y="482" width="495" height="26" rx="13" fill="#c28a29" />',
        '<rect x="28" y="482" width="525" height="26" rx="13" fill="#c28a29" />',
    ),
    # Tier 1: Outer Cutaway telemetry & labels
    (">BOEING 7107-B · AN-225 CLASS<", ">BOEING 7107-B · AN-225 OSZTÁLY<"),
    (">500 M² · 2 FULL LUXURY DECKS<", ">500 M² · 2 TELJES LUXUS SZINT<"),
    (">6× ROLLS-ROYCE TITAN XWB TURBOFANS<", ">6× ROLLS-ROYCE TITAN XWB HAJTÓMŰ<"),
    (
        ">102.0 M LENGTH · 94.0 M WINGSPAN · TWIN-FIN TAIL<",
        ">102,0 M HOSSZ · 94,0 M FESZTTÁV · DUPLA VEZÉRSÍK<",
    ),
    (">SITUATION WAR ROOM<", ">STRATÉGIAI VÁLSÁGSZOBA<"),
    (">SOVEREIGN LIVING LOUNGE<", ">SZUVERÉN NAPPALI SZALON<"),
    (">MASTER BEDROOM SUITE I<", ">I. FŐ HÁLÓSZOBA LAKOSZTÁLY<"),
    (">ROYAL CONSORT SUITE II<", ">II. KIRÁLYI HÁLÓSZOBA<"),
    (">UPPER SKY BAR<", ">FELSŐ SKY BÁR<"),
    (">GRAND FOYER<", ">ELŐCSARNOK<"),
    (">12-SEAT MAHOGANY BANQUET<", ">12 FŐS MAHAGÓNI BANKETT<"),
    (">BARS and VIDEO CONF.<", ">BÁR és VIDEOKONF.<"),
    (">GALLEY<", ">KONYHA<"),
    (">24 GOVERNMENT and MEDIA SEATS<", ">24 KORMÁNY és SAJTÓ ÜLÉS<"),
    (">MEDICAL ICU<", ">ORVOSI MŰTŐ<"),
    (">AN-225 TWIN-FIN TAIL<", ">AN-225 DUPLA VEZÉRSÍK<"),
    # Tier 2: Upper Deck headers & room labels
    (
        ">UPPER DECK · LEVEL 02 · SOVEREIGN RESIDENCE AND COMMAND (210 M²)<",
        ">FELSŐ FEDÉLZET · 02. SZINT · SZUVERÉN REZIDENCIA ÉS PARANCSNOKSÁG (210 M²)<",
    ),
    (
        ">ELONGATED UPPER TRUNK · 2 BEDROOMS · RAIN SHOWERS · SKY LOUNGE · WAR ROOM · COCKPIT<",
        ">NYÚJTOTT FELSŐ TÖRZS · 2 HÁLÓSZOBA · ESŐZUHANYOK · NAPPALI SZALON · VÁLSÁGSZOBA · PILÓTAFÜLKE<",
    ),
    (">FLIGHT DECK<", ">PILÓTAFÜLKE<"),
    (">SPIRAL STAIR 1<", ">1. CSIGALÉPCSŐ<"),
    (">STRATEGIC SITUATION WAR ROOM<", ">STRATÉGIAI VÁLSÁGSZOBA<"),
    (">MAHOGANY SALON CREDENZA AND LIBRARY<", ">MAHAGÓNI KÖNYVTÁR és KOMÓD<"),
    (
        ">SOVEREIGN LIVING ROOM AND SKY LOUNGE<",
        ">SZUVERÉN NAPPALI ÉS PANORÁMA SZALON<",
    ),
    (">STUDY DESK AND WALK-IN WARDROBE<", ">DOLGOZÓASZTAL és GARDRÓBSZOBA<"),
    (">SHOWER<", ">ZUHANY<"),
    (">ROYAL DRESSING VANITY<", ">KIRÁLYI PIPEREASZTAL<"),
    (">SHOWER II<", ">ZUHANY II<"),
    (">ROYAL SUITE II<", ">II. KIRÁLYI HÁLÓSZOBA<"),
    (">SPIRAL STAIR 2<", ">2. CSIGALÉPCSŐ<"),
    # Tier 3: Main Deck headers & room labels
    (
        ">MAIN DECK · LEVEL 01 · DIPLOMATIC AND DELEGATION DECK (290 M²)<",
        ">FŐFEDÉLZET · 01. SZINT · DIPLOMÁCIAI ÉS DELEGÁCIÓS SZINT (290 M²)<",
    ),
    (
        ">ANTONOV AN-225 OUTER SILHOUETTE · 6× TITAN XWB ENGINES · TWIN VERTICAL TAIL FINS<",
        ">ANTONOV AN-225 KÜLSŐ SZILUETT · 6× TITAN XWB HAJTÓMŰ · DUPLA FÜGGŐLEGES VEZÉRSÍK<",
    ),
    (">PORT TWIN TAIL FIN<", ">BAL DUPLA VEZÉRSÍK<"),
    (">STARBOARD TWIN TAIL FIN<", ">JOBB DUPLA VEZÉRSÍK<"),
    (">12-SEAT MAHOGANY STATE BANQUET HALL<", ">12 FŐS MAHAGÓNI ÁLLAMI BANKETT TEREM<"),
    (">VIDEO CONFERENCE THEATER<", ">VIDEOKONFERENCIA TEREM<"),
    (">BARS AND LOUNGES<", ">BÁR és TÁRSALGÓ<"),
    (">WINE CELLAR<", ">BORSZÉF<"),
    (">16 GOVERNMENT LIE-FLAT SUITES<", ">16 MINISZTERI LUXUSFÜLKE<"),
    (">8 MEDIA WORKSTATIONS<", ">8 SAJTÓMUNKAÁLLOMÁS<"),
    (
        ">CENTRAL DELEGATION CORRIDOR · 24 TOTAL SEATS<",
        ">KÖZPONTI DELEGÁCIÓS FOLYOSÓ · ÖSSZESEN 24 ÜLÉS<",
    ),
    (">DEFENSE<", ">VÉDELEM<"),
    # Bottom Architectural Meter Ruler
    (">0.0 M (NOSE PROBE)<", ">0,0 M (ORRSZONDA)<"),
    (">20.0 M<", ">20,0 M<"),
    (">40.0 M<", ">40,0 M<"),
    (">60.0 M<", ">60,0 M<"),
    (">80.0 M<", ">80,0 M<"),
    (">94.0 M (TAILCONE)<", ">94,0 M (FAROKKÚP)<"),
    (">102.0 M (TWIN TAIL)<", ">102,0 M (DUPLA VEZÉRSÍK)<"),
]


def load_svg(svg_path: Path, lang: str) -> str:
    """Load the SVG file content and localize text if needed."""
    raw_svg = svg_path.read_text(encoding="utf-8").strip()

    # Validate XML structure
    try:
        ET.fromstring(raw_svg)
    except ET.ParseError as exc:
        sys.exit(f"Error: {svg_path} is not valid XML: {exc}")

    # Strip standalone xmlns attribute for inline HTML5 embedding
    inline_svg = re.sub(r'\s+xmlns="http://www\.w3\.org/2000/svg"', "", raw_svg, count=1)

    if lang == "hu":
        for en_str, hu_str in EN_TO_HU:
            inline_svg = inline_svg.replace(en_str, hu_str)

    return inline_svg


def update_plane_html(svg_path: Path = DEFAULT_SVG_PATH) -> None:
    """Inject the loaded SVG into en/plane.html and hu/plane.html."""
    try:
        from build_pages import format_and_remove_empty_lines
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_pages import format_and_remove_empty_lines

    if not svg_path.is_file():
        sys.exit(f"Error: SVG file not found at {svg_path}")

    for lang in ("en", "hu"):
        html_path = ROOT / lang / "plane.html"
        html = html_path.read_text(encoding="utf-8")

        match = DECKPLAN_SVG_RE.search(html)
        if not match:
            sys.exit(f"Error: could not find <div class=\"deckplan-svg-scroll\"><svg>...</svg></div> in {html_path}")

        svg_content = load_svg(svg_path, lang)
        replacement = f"{match.group(1)}{svg_content}{match.group(2)}"
        updated_html = html[: match.start()] + replacement + html[match.end() :]
        cleaned_html = format_and_remove_empty_lines(updated_html)
        html_path.write_text(cleaned_html, encoding="utf-8")

        rel_html = html_path.relative_to(ROOT)
        rel_svg = svg_path.relative_to(ROOT) if svg_path.is_relative_to(ROOT) else svg_path
        size_kb = len(svg_content.encode("utf-8")) / 1024
        print(f"Loaded {rel_svg} -> {rel_html} ({size_kb:.1f} KB)")


def main() -> None:
    svg_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_SVG_PATH
    update_plane_html(svg_path)


if __name__ == "__main__":
    main()
