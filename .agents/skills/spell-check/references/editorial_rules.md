# Editorial & Copy Guidelines

This document details the editorial conventions, orthography, and typography rules for the Sovereign Nation of Waikiki site.

---

## 1. Ampersand Policy (AGENTS.md)

- **Rule**: In titles, section headings, card headers, labels, and narrative copy, always prefer the full conjunction word:
  - **English**: Use `and`
  - **Hungarian**: Use `és`
- **Avoid**: The ampersand symbol `&` in prose (e.g., do not write `Chease & Jessica`, write `Chease and Jessica` or `Chease és Jessica`).
- **Exceptions**:
  - Established corporate brands and acronyms: `Walker Finance & Insurance Holding`, `R&D`, `Q&A`, `AT&T`, `S&P`.
  - HTML entities: `&copy;`, `&amp;`, `&nbsp;`, `&quot;`, `&lt;`, `&gt;`.

---

## 2. Typography & Punctuation

- **No Leading Space Before Punctuation**: Punctuation marks (`,`, `.`, `:`, `;`, `?`, `!`) must never be preceded by a space, including across tag boundaries (e.g. `</em> .` is prohibited; must be `</em>.`).
- **No Stray Space After `<br>`**: In multi-line headings or text, `<br>` must be immediately followed by the letter, not `<br> `.
- **Double Punctuation**: Avoid accidental double commas (`,,`) or double periods (`..` unless intentional ellipsis `...`).
- **Quotation Marks**:
  - **Hungarian**: Use bottom-99 and top-99 smart quotes: `„Idézet”`. Never use English curly quotes `“...”` or straight quotes `"` in Hungarian prose.
  - **English**: Use curly quotes: `“quote”`.
- **Dashes & Hyphens**:
  - **En-dash (`–`, U+2013)**: Use for number/year ranges (`1999–2026`) and parenthetical thoughts (`– mondta –`).
  - **Hyphens (`-`)**: Ahol nem kötelező, ott ne használj kötőjelet! Helyette külön írd vagy ahogy eredetileg van.
  - **Covid-19**: Mindig szabályos kötőjellel írandó: `Covid-19` (nem en-dash `Covid–19`, és nem csupa nagybetűs `COVID-19`).

---

## 3. Hungarian Orthography & Style Rules (Magyar helyes alakok)

### Kötelező alakok és átírások:
- **Pacifikus háború -> Csendes-óceáni háború**: A történeti leírásokban mindig `Csendes-óceáni háború` használandó.
- **COVID-19 -> Covid-19**: Egységesen `Covid-19` (kisbetűs ovid, sima kötőjel).
- **zárt körű -> zártkörű**: Egybeírandó (`zártkörű`). Ahol túl sokszor szerepel egymás után, ott cserélendő választékos szinonimákra (*szűk körű*, *privát*, *meghitt*, *kötetlen*, *bizalmas*).
- **infrastruktúrafejlesztés -> infrastruktúra-fejlesztés**: Kötőjellel írandó (és toldalékos alakjai: *infrastruktúra-fejlesztési*, *infrastruktúra-fejlesztésben*).
- **waikiki-i -> Waikiki-i**: Nagy W-vel. Ha van jó alternatíva, kerüld a melléknév alakot (pl. `Waikiki-i polgárok` helyett `Waikiki polgárai`).
- **Nova Aurélia -> Nova Aurelia**: A főváros neve ékezet nélkül `Nova Aurelia`.
- **Nova Aurelia-i -> Nova Auréliai**: A melléknévi forma `Nova Auréliai` (kötőjel nélkül, nagybetűkkel).
- **Idézőjelek**: `“...”` helyett mindig magyar `„...”` (alsó 99 és felső 99).
- **A szuverén szó használata**: A `szuverén` szó ne szerepeljen feleslegesen. Footerben ok (`Waikiki Szuverén Állam`), az állammal / nemzettel kapcsolatban ok (`szuverén állam`), más kontextusban ne szerepeljen (helyette: *önálló*, *független*, *saját* stb.).
- **TODO részek**: A kódban és szövegekben található `TODO` részeket (pl. képhivatkozások, megjegyzések) tilos módosítani helyesírás-javításkor!

### Címek és nagybetűs formák:
- A címekben szereplő nagybetűs alakokat ne módosítsd kisbetűssé, csak egységesítsd oldalakon belül.
- Ha egy oldalon a címek Title Case formátumúak, maradhatnak, de legyenek következetesek.

### Fogalmazás és stílus:
- **Szóismétlések kerülése**: Kerüld az azonos szavak gyakori ismétlődését egymást követő mondatokban.
- **Igényes megfogalmazások**: Méltóságteljes, tiszta, professzionális nyelvezet.

---

## 4. HTML Page Layout & Structure

- **4-Space Indentation**: All HTML markup must be indented with 4 spaces.
- **0 Empty Lines**: No blank lines are permitted in the HTML document.
- **Alternating Section Styles**: Top-level page sections must alternate between normal and `light-bg` styles.
- **Page Titles**: Include standard site suffix ` — Waikiki Szuverén Állam` (or ` — Sovereign Nation of Waikiki` in English).
