# Locale Synchronization Guidelines & Conventions

This reference outlines standard terminology, spec mappings, and translation conventions used across bilingual pages in the Sovereign Nation of Waikiki portal.

---

## 1. Technical Specification Labels (Common Translations)

When synchronizing cards with technical specifications between Hungarian and English, use the following standard pairings:

| Hungarian Label | English Label | Typical Units / Formatting |
| :--- | :--- | :--- |
| **Magasság** | **Height** | `115 m`, `72 m` |
| **Fesztáv** | **Wingspan** | `34 m`, `64,8 m` / `64.8 m` |
| **Hossz** | **Length** | `45 m` |
| **Legénység** | **Crew** | `0 fő` <-> `Uncrewed`, `10 fő` <-> `10 Astronauts` / `10 Crew` |
| **Kapacitás** | **Capacity** | `180 utas` <-> `180 Passengers` |
| **Rakomány** | **Payload** | `180 000 kg`, `40 000 kg` |
| **Hatótáv** / **Hatótávolság** | **Range** | `14 800 km` |
| **Gyorsulás** / **Tolóerő** | **Thrust** | `35 000 kN`, `40 000 kN` |
| **Sebesség** / **Utazósebesség** | **Cruise Speed** | `Mach 0,85` / `Mach 0.85` |
| **Csúcssebesség** | **Top Speed** | `Mach 2,2` / `Mach 2.2` |
| **Szolgálati magasság** | **Service Ceiling** | `13 700 m` |
| **Költség** | **Unit Cost** / **Cost** | `300 millió $` <-> `$300 Million`, `2 milliárd $` <-> `$2 Billion` |
| **Státusz** | **Status** | `Aktív` <-> `Active`, `Tervezett` <-> `In Development` |
| **Tervezett pálya** | **Target Orbit** | `Hold körüli halópálya` <-> `Near-Rectilinear Halo Orbit` |
| **Partnerintézmények** | **Partnership** | `WSA és NASA közös fejlesztés` <-> `WSA and NASA Joint Project` |
| **Célkitűzés** | **Key Objective** | `Extrém mélyűri kísérletek` <-> `Extreme Deep-Space Experiments` |

---

## 2. Spec Badges

Spec badges in cards categorize operational or fleet readiness:

| Hungarian Badge | English Badge |
| :--- | :--- |
| `Aktív Flotta` | `Active Fleet` |
| `Fejlesztés Alatt` | `In Development` |
| `Koncepció` | `Concept Phase` |
| `Új Távlatok` | `Next Generation` |
| `Zászlóshajó` | `Flagship` |
| `Szolgálatban` | `In Service` |

---

## 3. Formatting Numbers Across Locales

- **Grouping Separator**:
  - Hungarian: Space separator for thousands (e.g. `180 000 kg`, `35 000 kN`, `200 000 kg`).
  - English: Comma separator (e.g. `180,000 kg`, `35,000 kN`) or space matching the source.
- **Decimals**:
  - Hungarian: Comma decimal (e.g. `2,5 milliárd $`, `Mach 0,85`).
  - English: Period decimal (e.g. `$2.5 Billion`, `Mach 0.85`).
- **Currency**:
  - Hungarian: `300 millió $`, `2 milliárd $`, `120 Mrd Ft`.
  - English: `$300 Million`, `$2 Billion`.

---

## 4. Layout & Structural Parity Checklist

When synchronizing a source page to its target counterpart, ensure:
1. Every `<section>` tag in the target matches the `id` and `class` (`light-bg`, `fade-in`) of the source.
2. The count of `<div class="card">` elements within every section is identical.
3. Every `.aircraft-watermark` or `.watermark` image has the identical `src` path.
4. Top-level sections alternate strictly between normal and `light-bg`.
5. Run `python3 scripts/build_pages.py --format <target.html>` upon completion.
