"""
Script to replace .rocket-wireframe-wrapper blocks with .aircraft-watermark watermark <img> tags in hu/space-research.html and en/space-research.html.
"""

import re

MAP = [
    ("Delta III A", "rocket-delta-3a.svg"),
    ("Space Shuttle", "rocket-shuttle.svg"),
    ("Saturn X", "rocket-saturn-x.svg"),
    ("Falcon Heavy", "rocket-falcon-heavy.svg"), # match Falcon Heavy before Falcon
    ("Falcon", "rocket-falcon.svg"),
    ("Delta III B", "rocket-delta-3b.svg"),
    ("Space Shuttle v2", "rocket-shuttle-v2.svg"),
    ("Saturn Nova", "rocket-saturn-nova.svg"),
    ("Falcon v2", "rocket-falcon-v2.svg"),
    ("Big Falcon Rocket", "rocket-bfr.svg"),
    ("Delta IV", "rocket-delta-4.svg"),
    ("Bolygóközi Űrsikló", "rocket-interplanetary-shuttle.svg"),
    ("Interplanetary Shuttle", "rocket-interplanetary-shuttle.svg"),
]

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match each card inside #fleet
    # First, let's remove any <div class="rocket-wireframe-wrapper">...</div>
    content = re.sub(r'\s*<div class="rocket-wireframe-wrapper">.*?</div>\s*</div>', '', content, flags=re.DOTALL)

    # Now, each card ends with </ul>\s*</div>
    # But wait, we want to know WHICH card it is so we can add the right watermark <img> before </div>
    # Let's match each <div class="card">...</div> inside the fleet section
    # Let's isolate the fleet section
    fleet_start = content.find('<section id="fleet"')
    if fleet_start == -1:
        print("Could not find #fleet in", filepath)
        return

    # Find end of section
    fleet_end = content.find('</section>', fleet_start)
    if fleet_end == -1:
        print("Could not find </section> for #fleet in", filepath)
        return

    fleet_html = content[fleet_start:fleet_end]

    # Split into cards
    # Each card starts with '<div class="card">'
    cards = fleet_html.split('<div class="card">')
    new_fleet_html = cards[0]

    for card in cards[1:]:
        # Find which rocket this card is for by checking h3
        h3_match = re.search(r'<h3>(.*?)</h3>', card)
        if not h3_match:
            print("Warning: no h3 in card:", card[:100])
            new_fleet_html += '<div class="card">' + card
            continue

        h3_title = h3_match.group(1).strip()
        matched_svg = None
        for title, svg_file in MAP:
            if title == h3_title:
                matched_svg = svg_file
                break

        if not matched_svg:
            print(f"Warning: no matching SVG for '{h3_title}'")
            new_fleet_html += '<div class="card">' + card
            continue

        # Strip any existing watermark if present
        card = re.sub(r'\s*<img src="[^"]*rocket-[^"]*" alt="" class="[^"]*" aria-hidden="true" />', '', card)

        # Insert watermark right before the closing </div> of this card
        # The closing </div> is at the end of the card block
        last_div_idx = card.rfind('</div>')
        if last_div_idx != -1:
            watermark_tag = f'\n                    <img src="../icons/rockets/{matched_svg}" alt="" class="aircraft-watermark aircraft-watermark--plane" aria-hidden="true" />\n                '
            card = card[:last_div_idx] + watermark_tag + card[last_div_idx:]
        else:
            print(f"Warning: no closing </div> for '{h3_title}'")

        new_fleet_html += '<div class="card">' + card

    # Replace fleet section in content
    new_content = content[:fleet_start] + new_fleet_html + content[fleet_end:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully updated {filepath}")

process_file("hu/space-research.html")
process_file("en/space-research.html")
