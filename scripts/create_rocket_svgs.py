"""
Script to generate all 12 technical blueprint wireframe SVGs for Waikiki's space rockets and shuttles.
Modeled after icons/planes/plane-af1.svg and plane-concorde.svg.
"""

import os

SVG_DIR = "/Volumes/Samsung X5 SSD/Projektek/Site/icons/rockets"
os.makedirs(SVG_DIR, exist_ok=True)

def wrap_svg(id_prefix, height_str, width_str, content):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="100%" height="100%" fill="none" style="color: #003366;">
  <defs>
    <linearGradient id="{id_prefix}Body" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="currentColor" stop-opacity="0.12" />
      <stop offset="50%" stop-color="currentColor" stop-opacity="0.28" />
      <stop offset="100%" stop-color="currentColor" stop-opacity="0.12" />
    </linearGradient>
    <linearGradient id="{id_prefix}Booster" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="currentColor" stop-opacity="0.15" />
      <stop offset="50%" stop-color="currentColor" stop-opacity="0.32" />
      <stop offset="100%" stop-color="currentColor" stop-opacity="0.15" />
    </linearGradient>
    <linearGradient id="{id_prefix}Wing" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="currentColor" stop-opacity="0.22" />
      <stop offset="100%" stop-color="currentColor" stop-opacity="0.08" />
    </linearGradient>
    <pattern id="{id_prefix}Grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.12" />
    </pattern>
  </defs>

  <!-- Background Coordinate Grid -->
  <rect x="20" y="20" width="760" height="760" fill="url(#{id_prefix}Grid)" />

  <!-- Technical Axis and Grid -->
  <g opacity="0.25" stroke="currentColor" stroke-width="0.75" stroke-dasharray="3 3">
    <line x1="400" y1="25" x2="400" y2="775" />
    <line x1="25" y1="400" x2="775" y2="400" />
    <circle cx="400" cy="400" r="350" />
    <circle cx="400" cy="400" r="220" />
    <circle cx="400" cy="400" r="100" />
  </g>

  <!-- Dimensions Callouts -->
  <g opacity="0.6" stroke="currentColor" stroke-width="1">
    <!-- Height bar -->
    <line x1="160" y1="45" x2="130" y2="45" />
    <line x1="160" y1="755" x2="130" y2="755" />
    <line x1="145" y1="45" x2="145" y2="755" stroke-dasharray="4 4" />
    <text x="130" y="400" text-anchor="middle" fill="currentColor" font-family="monospace" font-size="11" letter-spacing="2" opacity="0.85" transform="rotate(-90 130 400)" stroke="none">HEIGHT {height_str}</text>

    <!-- Width / Diameter bar -->
    <line x1="300" y1="765" x2="300" y2="785" />
    <line x1="500" y1="765" x2="500" y2="785" />
    <line x1="300" y1="775" x2="500" y2="775" stroke-dasharray="4 4" />
    <text x="400" y="792" text-anchor="middle" fill="currentColor" font-family="monospace" font-size="10.5" letter-spacing="2" opacity="0.85" stroke="none">{width_str}</text>
  </g>

  <!-- Rocket Technical Vector Graphic -->
  <g id="vehicle-graphic">
{content}
  </g>
</svg>"""

# 1. Delta III A (Delta 8930: 4m fairing, 2.44m core, 9 GEM-46 strap-on boosters, single RS-27A)
def svg_delta_3a():
    id_p = "d3a"
    content = f"""    <!-- 9 GEM-46 Solid Rocket Boosters (3 on left, 3 on right, 3 central overlap) -->
    <!-- Far Left Booster -->
    <g stroke="currentColor" stroke-width="1.8">
      <path d="M 334 520 L 334 690 L 344 705 L 348 690 L 348 520 Q 341 500 334 520 Z" fill="url(#{id_p}Booster)" />
      <polygon points="334,705 348,705 344,720 338,720" fill="currentColor" opacity="0.3" />
      <!-- Mid Left Booster -->
      <path d="M 350 495 L 350 695 L 360 710 L 366 695 L 366 495 Q 358 475 350 495 Z" fill="url(#{id_p}Booster)" />
      <polygon points="350,710 366,710 362,725 354,725" fill="currentColor" opacity="0.3" />
      <!-- Inner Left Booster -->
      <path d="M 368 470 L 368 700 L 380 715 L 384 700 L 384 470 Q 376 450 368 470 Z" fill="url(#{id_p}Booster)" />
      <polygon points="368,715 384,715 380,730 372,730" fill="currentColor" opacity="0.3" />

      <!-- Inner Right Booster -->
      <path d="M 432 470 L 432 700 L 420 715 L 416 700 L 416 470 Q 424 450 432 470 Z" fill="url(#{id_p}Booster)" />
      <polygon points="416,715 432,715 428,730 420,730" fill="currentColor" opacity="0.3" />
      <!-- Mid Right Booster -->
      <path d="M 450 495 L 450 695 L 440 710 L 434 695 L 434 495 Q 442 475 450 495 Z" fill="url(#{id_p}Booster)" />
      <polygon points="434,710 450,710 446,725 438,725" fill="currentColor" opacity="0.3" />
      <!-- Far Right Booster -->
      <path d="M 466 520 L 466 690 L 456 705 L 452 690 L 452 520 Q 459 500 466 520 Z" fill="url(#{id_p}Booster)" />
      <polygon points="452,705 466,705 462,720 456,720" fill="currentColor" opacity="0.3" />
    </g>

    <!-- First Stage Core (2.44m diameter core) -->
    <rect x="372" y="260" width="56" height="455" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" rx="1" />
    <!-- Core Stage Panel Lines & Weld Ribs -->
    <g stroke="currentColor" stroke-width="1" opacity="0.65">
      <line x1="372" y1="310" x2="428" y2="310" />
      <line x1="372" y1="370" x2="428" y2="370" />
      <line x1="372" y1="440" x2="428" y2="440" />
      <line x1="372" y1="520" x2="428" y2="520" />
      <line x1="372" y1="610" x2="428" y2="610" />
      <line x1="372" y1="680" x2="428" y2="680" />
      <line x1="392" y1="260" x2="392" y2="715" stroke-dasharray="4 4" />
      <line x1="408" y1="260" x2="408" y2="715" stroke-dasharray="4 4" />
    </g>

    <!-- Interstage Transition Skirt (Flaring from 2.44m to 4m fairing) -->
    <polygon points="372,260 428,260 440,210 360,210" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <g stroke="currentColor" stroke-width="1" opacity="0.7">
      <line x1="365" y1="235" x2="435" y2="235" />
      <line x1="380" y1="260" x2="375" y2="210" />
      <line x1="400" y1="260" x2="400" y2="210" />
      <line x1="420" y1="260" x2="425" y2="210" />
    </g>

    <!-- Cryogenic Second Stage (4m diameter) -->
    <rect x="360" y="150" width="80" height="60" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <line x1="360" y1="180" x2="440" y2="180" stroke="currentColor" stroke-width="1" opacity="0.65" />

    <!-- 4-meter Bulbous Payload Fairing (Contraves bisector) -->
    <path d="M 360 150 C 352 110 370 65 400 45 C 430 65 448 110 440 150 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" />
    <!-- Fairing Split Line -->
    <line x1="400" y1="45" x2="400" y2="150" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3 2" />

    <!-- Main RS-27A Engine & Twin Vernier Nozzles -->
    <path d="M 388 715 L 382 745 L 418 745 L 412 715 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="2" />
    <path d="M 374 715 L 372 735 L 380 735 L 378 715 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="1.4" />
    <path d="M 422 715 L 420 735 L 428 735 L 426 715 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="1.4" />"""
    return wrap_svg("d3a", "115.0 M", "CORE 4.0 M", content)

# 2. Space Shuttle (NASA STS Orbiter: authentic double-delta winged orbiter)
def svg_shuttle():
    id_p = "sts"
    content = f"""    <!-- Space Shuttle Orbiter (Top-Down / Dorsal Technical Blueprint) -->

    <!-- Wings (Double-Delta Wing Planform: Strakes sweeping at ~81°, leading edge at 45° to wingtips) -->
    <!-- Left Wing Structure -->
    <path d="M 356 220 L 324 410 L 165 595 L 165 620 L 342 620 L 356 610 Z" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />
    <!-- Right Wing Structure -->
    <path d="M 444 220 L 476 410 L 635 595 L 635 620 L 458 620 L 444 610 Z" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />

    <!-- Black RCC (Reinforced Carbon-Carbon) Thermal Protection Leading Edges -->
    <path d="M 356 220 L 324 410 L 165 595 L 165 605 L 328 418 L 358 230 Z" fill="currentColor" opacity="0.35" stroke="currentColor" stroke-width="1.2" />
    <path d="M 444 220 L 476 410 L 635 595 L 635 605 L 472 418 L 442 230 Z" fill="currentColor" opacity="0.35" stroke="currentColor" stroke-width="1.2" />

    <!-- Wing Elevons (Inboard and Outboard Flight Control Surfaces) -->
    <!-- Left Wing Elevons -->
    <g stroke="currentColor" stroke-width="1.4">
      <!-- Outboard Elevon Left -->
      <polygon points="180,598 255,598 255,618 180,618" fill="url(#{id_p}Booster)" />
      <!-- Inboard Elevon Left -->
      <polygon points="262,598 335,598 335,618 262,618" fill="url(#{id_p}Booster)" />
      <line x1="217" y1="598" x2="217" y2="618" stroke-width="1" opacity="0.6" />
      <line x1="298" y1="598" x2="298" y2="618" stroke-width="1" opacity="0.6" />
    </g>
    <!-- Right Wing Elevons -->
    <g stroke="currentColor" stroke-width="1.4">
      <!-- Inboard Elevon Right -->
      <polygon points="465,598 538,598 538,618 465,618" fill="url(#{id_p}Booster)" />
      <!-- Outboard Elevon Right -->
      <polygon points="545,598 620,598 620,618 545,618" fill="url(#{id_p}Booster)" />
      <line x1="502" y1="598" x2="502" y2="618" stroke-width="1" opacity="0.6" />
      <line x1="583" y1="598" x2="583" y2="618" stroke-width="1" opacity="0.6" />
    </g>

    <!-- Wing Panel Expansion & Tile Grid Lines -->
    <g stroke="currentColor" stroke-width="0.8" opacity="0.55">
      <line x1="210" y1="595" x2="260" y2="535" />
      <line x1="260" y1="595" x2="310" y2="535" />
      <line x1="310" y1="595" x2="330" y2="470" />
      <line x1="590" y1="595" x2="540" y2="535" />
      <line x1="540" y1="595" x2="490" y2="535" />
      <line x1="490" y1="595" x2="470" y2="470" />
    </g>

    <!-- Main Fuselage Body (Nose to Aft Bulkhead) -->
    <path d="M 382 95 C 382 68 400 60 400 60 C 400 60 418 68 418 95 L 444 220 L 448 515 L 436 630 L 364 630 L 352 515 L 356 220 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />

    <!-- Black RCC Nose Cap -->
    <path d="M 385 92 C 385 70 400 62 400 62 C 400 62 415 70 415 92 C 415 104 385 104 385 92 Z" fill="currentColor" opacity="0.45" stroke="currentColor" stroke-width="1.8" />

    <!-- Forward Reaction Control System (RCS) Thruster Wells -->
    <g fill="currentColor" opacity="0.65">
      <!-- Left RCS thrusters -->
      <circle cx="387" cy="85" r="1.8" />
      <circle cx="390" cy="90" r="1.8" />
      <circle cx="387" cy="95" r="1.8" />
      <circle cx="391" cy="98" r="1.8" />
      <!-- Right RCS thrusters -->
      <circle cx="413" cy="85" r="1.8" />
      <circle cx="410" cy="90" r="1.8" />
      <circle cx="413" cy="95" r="1.8" />
      <circle cx="409" cy="98" r="1.8" />
    </g>

    <!-- Cockpit Windshield (6 Faceted Crew Flight Deck Windows + 2 Overhead) -->
    <g fill="currentColor" opacity="0.75" stroke="currentColor" stroke-width="0.8">
      <!-- Front-left -->
      <polygon points="393,124 398,122 398,131 392,130" />
      <!-- Front-right -->
      <polygon points="402,122 407,124 408,130 402,131" />
      <!-- Side-left -->
      <polygon points="385,127 391,125 390,132 384,133" />
      <!-- Side-right -->
      <polygon points="409,125 415,127 416,133 410,132" />
      <!-- Outer-left -->
      <polygon points="381,131 384,130 384,134 380,135" />
      <!-- Outer-right -->
      <polygon points="416,130 419,131 420,135 416,134" />
      <!-- Overhead rendezvous windows -->
      <rect x="393" y="137" width="5" height="4" rx="1" />
      <rect x="402" y="137" width="5" height="4" rx="1" />
    </g>
    <!-- Star Tracker Viewports -->
    <circle cx="397" cy="112" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="403" cy="112" r="1.5" fill="currentColor" opacity="0.8" />

    <!-- Payload Bay (60-foot Bay with Centerline Split & Segmented Doors) -->
    <!-- Door Outer Contours & Center Seam -->
    <rect x="360" y="165" width="80" height="350" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="1.4" opacity="0.8" />
    <line x1="400" y1="165" x2="400" y2="515" stroke="currentColor" stroke-width="1.8" />
    <!-- 4 Segment Door Hinges / Seams -->
    <line x1="360" y1="250" x2="440" y2="250" stroke="currentColor" stroke-width="1" opacity="0.65" />
    <line x1="360" y1="340" x2="440" y2="340" stroke="currentColor" stroke-width="1" opacity="0.65" />
    <line x1="360" y1="430" x2="440" y2="430" stroke="currentColor" stroke-width="1" opacity="0.65" />
    <!-- Conformal Radiator Panel Lines -->
    <g stroke="currentColor" stroke-width="0.75" stroke-dasharray="3 3" opacity="0.45">
      <line x1="372" y1="175" x2="372" y2="505" />
      <line x1="386" y1="175" x2="386" y2="505" />
      <line x1="414" y1="175" x2="414" y2="505" />
      <line x1="428" y1="175" x2="428" y2="505" />
    </g>

    <!-- Twin OMS (Orbital Maneuvering System) Pods -->
    <!-- Left OMS Pod -->
    <g stroke="currentColor" stroke-width="1.8">
      <path d="M 354 485 C 336 515 332 560 334 625 L 364 625 L 360 495 Z" fill="url(#{id_p}Booster)" />
      <!-- Left Aft RCS Thrusters -->
      <rect x="335" y="605" width="8" height="14" fill="currentColor" opacity="0.5" stroke="none" />
      <circle cx="339" cy="610" r="1.3" fill="#ffffff" />
      <circle cx="339" cy="615" r="1.3" fill="#ffffff" />
      <!-- Left OMS Engine Nozzle -->
      <polygon points="342,625 352,625 354,642 340,642" fill="currentColor" opacity="0.5" />
    </g>
    <!-- Right OMS Pod -->
    <g stroke="currentColor" stroke-width="1.8">
      <path d="M 446 485 C 464 515 468 560 466 625 L 436 625 L 440 495 Z" fill="url(#{id_p}Booster)" />
      <!-- Right Aft RCS Thrusters -->
      <rect x="457" y="605" width="8" height="14" fill="currentColor" opacity="0.5" stroke="none" />
      <circle cx="461" cy="610" r="1.3" fill="#ffffff" />
      <circle cx="461" cy="615" r="1.3" fill="#ffffff" />
      <!-- Right OMS Engine Nozzle -->
      <polygon points="448,625 458,625 460,642 446,642" fill="currentColor" opacity="0.5" />
    </g>

    <!-- Vertical Stabilizer (Fin & Centerline Rudder / Speed Brake) -->
    <!-- Dorsal Fin Base -->
    <path d="M 400 390 L 396 460 L 396 630 L 404 630 L 404 460 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="1.6" />
    <line x1="400" y1="390" x2="400" y2="630" stroke="currentColor" stroke-width="2" />
    <!-- Rudder Split / Speed Brake Lines -->
    <line x1="396" y1="520" x2="404" y2="520" stroke="currentColor" stroke-width="1.4" />
    <line x1="396" y1="580" x2="404" y2="580" stroke="currentColor" stroke-width="1.4" />

    <!-- Aft Thermal Body Flap -->
    <polygon points="374,630 426,630 430,652 370,652" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="1.8" />
    <line x1="388" y1="630" x2="388" y2="652" stroke="currentColor" stroke-width="1" opacity="0.6" />
    <line x1="412" y1="630" x2="412" y2="652" stroke="currentColor" stroke-width="1" opacity="0.6" />

    <!-- 3 SSME Main Rocket Engines (Inverted Triangle Cluster) -->
    <!-- Top Center SSME Engine Bell -->
    <g stroke="currentColor" stroke-width="2">
      <ellipse cx="400" cy="650" rx="16" ry="14" fill="currentColor" opacity="0.4" />
      <circle cx="400" cy="650" r="8" fill="currentColor" opacity="0.6" />
      <!-- Gimbal Actuator Struts -->
      <line x1="390" y1="634" x2="395" y2="644" stroke-width="1.5" />
      <line x1="410" y1="634" x2="405" y2="644" stroke-width="1.5" />
    </g>
    <!-- Lower Left SSME Engine Bell -->
    <g stroke="currentColor" stroke-width="2">
      <ellipse cx="378" cy="682" rx="16" ry="14" fill="currentColor" opacity="0.45" />
      <circle cx="378" cy="682" r="8" fill="currentColor" opacity="0.65" />
      <line x1="368" y1="666" x2="373" y2="676" stroke-width="1.5" />
      <line x1="388" y1="666" x2="383" y2="676" stroke-width="1.5" />
    </g>
    <!-- Lower Right SSME Engine Bell -->
    <g stroke="currentColor" stroke-width="2">
      <ellipse cx="422" cy="682" rx="16" ry="14" fill="currentColor" opacity="0.45" />
      <circle cx="422" cy="682" r="8" fill="currentColor" opacity="0.65" />
      <line x1="412" y1="666" x2="417" y2="676" stroke-width="1.5" />
      <line x1="432" y1="666" x2="427" y2="676" stroke-width="1.5" />
    </g>"""
    return wrap_svg("sts", "72.0 M", "SPAN 23.8 M", content)

# 3. Saturn X (Apollo Saturn V / MLV: 10m diameter, 5 F-1 engines, S-IC fins, CSM & Launch Escape Tower)
def svg_saturn_x():
    id_p = "satx"
    content = f"""    <!-- Launch Escape System (LES) Tower at Apex -->
    <line x1="400" y1="35" x2="400" y2="105" stroke="currentColor" stroke-width="2" />
    <polygon points="397,35 403,35 401,55 399,55" fill="currentColor" />
    <line x1="392" y1="75" x2="408" y2="75" stroke="currentColor" stroke-width="1.2" />
    <!-- Truss Tower Legs -->
    <line x1="395" y1="105" x2="399" y2="60" stroke="currentColor" stroke-width="1" />
    <line x1="405" y1="105" x2="401" y2="60" stroke="currentColor" stroke-width="1" />
    <line x1="395" y1="90" x2="405" y2="75" stroke="currentColor" stroke-width="0.8" />
    <line x1="405" y1="90" x2="395" y2="75" stroke="currentColor" stroke-width="0.8" />

    <!-- Command & Service Module (CSM) -->
    <!-- Command Module Cone -->
    <polygon points="394,105 406,105 412,130 388,130" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="1.8" />
    <!-- Service Module Cylinder -->
    <rect x="388" y="130" width="24" height="40" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="1.8" />
    <!-- Spacecraft Lunar Module Adapter (SLA) Taper -->
    <polygon points="388,170 412,170 422,230 378,230" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2" />

    <!-- Third Stage (S-IVB) -->
    <rect x="378" y="230" width="44" height="95" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <!-- Instrument Unit (IU) Ring -->
    <rect x="378" y="230" width="44" height="10" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="1" />
    <!-- Interstage Ring Taper to 10m Core -->
    <polygon points="378,325 422,325 432,365 368,365" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2" />

    <!-- Second Stage (S-II: 10m diameter) -->
    <rect x="368" y="365" width="64" height="150" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <line x1="368" y1="435" x2="432" y2="435" stroke="currentColor" stroke-width="1.2" opacity="0.7" />
    <!-- Interstage Corrugation -->
    <rect x="368" y="505" width="64" height="25" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="1.4" />

    <!-- First Stage (S-IC: 10m diameter) -->
    <rect x="368" y="530" width="64" height="190" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" />
    <!-- Vertical Fuel Lines and Panels -->
    <line x1="380" y1="530" x2="380" y2="720" stroke="currentColor" stroke-width="1" opacity="0.6" />
    <line x1="420" y1="530" x2="420" y2="720" stroke="currentColor" stroke-width="1" opacity="0.6" />
    <line x1="368" y1="625" x2="432" y2="625" stroke="currentColor" stroke-width="1.2" opacity="0.7" />

    <!-- 4 Aerodynamic Stabilizing Fins & Engine Fairings -->
    <!-- Left Fin -->
    <polygon points="368,665 310,720 310,735 368,720" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" />
    <!-- Right Fin -->
    <polygon points="432,665 490,720 490,735 432,720" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" />

    <!-- 5 Massive F-1 Engines (4 outer fairing bells, 1 center bell) -->
    <path d="M 358 720 L 350 755 L 372 755 L 368 720 Z" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="2" />
    <path d="M 374 720 L 370 755 L 392 755 L 388 720 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="2" />
    <path d="M 390 720 L 388 755 L 412 755 L 410 720 Z" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="2" />
    <path d="M 412 720 L 408 755 L 430 755 L 426 720 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="2" />
    <path d="M 432 720 L 428 755 L 450 755 L 442 720 Z" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="2" />"""
    return wrap_svg("satx", "125.0 M", "CORE 10.0 M", content)

# 4. Falcon (Falcon 9 Block 5: 3.7m diameter, Octaweb 9 Merlin engines, 4 folded landing legs, 4 grid fins)
def svg_falcon():
    id_p = "f9"
    content = f"""    <!-- Payload Fairing (5.2m bi-conic) -->
    <path d="M 378 175 L 378 120 C 378 70 400 45 400 45 C 400 45 422 70 422 120 L 422 175 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />
    <line x1="400" y1="45" x2="400" y2="175" stroke="currentColor" stroke-width="1" stroke-dasharray="3 2" />

    <!-- Second Stage -->
    <rect x="382" y="175" width="36" height="105" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <!-- Interstage Section (Carbon Composite Black) -->
    <rect x="382" y="280" width="36" height="40" fill="currentColor" opacity="0.25" stroke="currentColor" stroke-width="2" />

    <!-- 4 Titanium Hypersonic Grid Fins (Deployed at top of Stage 1) -->
    <!-- Left Grid Fin -->
    <g stroke="currentColor" stroke-width="1.4">
      <rect x="348" y="285" width="34" height="18" fill="url(#{id_p}Wing)" />
      <line x1="358" y1="285" x2="358" y2="303" />
      <line x1="368" y1="285" x2="368" y2="303" />
      <line x1="348" y1="294" x2="382" y2="294" />
    </g>
    <!-- Right Grid Fin -->
    <g stroke="currentColor" stroke-width="1.4">
      <rect x="418" y="285" width="34" height="18" fill="url(#{id_p}Wing)" />
      <line x1="430" y1="285" x2="430" y2="303" />
      <line x1="442" y1="285" x2="442" y2="303" />
      <line x1="418" y1="294" x2="452" y2="294" />
    </g>

    <!-- First Stage Booster Body (3.7m diameter) -->
    <rect x="382" y="320" width="36" height="395" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <!-- Raceway Conduit Line -->
    <line x1="408" y1="175" x2="408" y2="715" stroke="currentColor" stroke-width="1.6" />
    <!-- Tank Weld Lines -->
    <g stroke="currentColor" stroke-width="0.8" opacity="0.6">
      <line x1="382" y1="390" x2="418" y2="390" />
      <line x1="382" y1="465" x2="418" y2="465" />
      <line x1="382" y1="540" x2="418" y2="540" />
      <line x1="382" y1="615" x2="418" y2="615" />
    </g>

    <!-- 4 Deployable Landing Legs (Folded A-frame configuration) -->
    <!-- Left Landing Leg -->
    <polygon points="382,530 354,715 364,715 382,590" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="1.8" />
    <line x1="382" y1="700" x2="356" y2="715" stroke="currentColor" stroke-width="2" />
    <!-- Right Landing Leg -->
    <polygon points="418,530 446,715 436,715 418,590" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="1.8" />
    <line x1="418" y1="700" x2="444" y2="715" stroke="currentColor" stroke-width="2" />

    <!-- Octaweb Base & Merlin 1D Engine Cluster (9 engines) -->
    <polygon points="380,715 420,715 416,735 384,735" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="2" />
    <!-- Engine Bells -->
    <path d="M 386 735 L 382 750 L 396 750 L 392 735 Z" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="1.4" />
    <path d="M 394 735 L 392 752 L 408 752 L 406 735 Z" fill="currentColor" opacity="0.7" stroke="currentColor" stroke-width="1.6" />
    <path d="M 408 735 L 404 750 L 418 750 L 414 735 Z" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="1.4" />"""
    return wrap_svg("f9", "90.0 M", "CORE 3.7 M", content)

# 5. Falcon Heavy (3 Falcon cores side-by-side: 2 side boosters + 1 center core, 27 Merlin engines)
def svg_falcon_heavy():
    id_p = "fh"
    content = f"""    <!-- Left Side Booster -->
    <g stroke="currentColor" stroke-width="2">
      <!-- Aerodynamic Nosecone -->
      <path d="M 326 230 C 326 185 344 165 344 165 C 344 165 362 185 362 230 Z" fill="url(#{id_p}Booster)" />
      <!-- Left Core Body -->
      <rect x="326" y="230" width="36" height="485" fill="url(#{id_p}Booster)" />
      <!-- Grid Fin Left Booster -->
      <rect x="304" y="250" width="22" height="15" fill="url(#{id_p}Wing)" stroke-width="1.2" />
      <line x1="314" y1="250" x2="314" y2="265" stroke-width="1" />
      <!-- Folded Leg Left Booster -->
      <polygon points="326,550 304,715 312,715 326,605" fill="currentColor" opacity="0.3" stroke-width="1.6" />
      <!-- Octaweb & Engine Bells -->
      <polygon points="324,715 364,715 360,735 328,735" fill="currentColor" opacity="0.5" />
      <path d="M 330 735 L 327 748 L 342 748 L 338 735 Z" fill="currentColor" opacity="0.6" />
      <path d="M 346 735 L 344 748 L 358 748 L 354 735 Z" fill="currentColor" opacity="0.6" />
    </g>

    <!-- Right Side Booster -->
    <g stroke="currentColor" stroke-width="2">
      <!-- Aerodynamic Nosecone -->
      <path d="M 438 230 C 438 185 456 165 456 165 C 456 165 474 185 474 230 Z" fill="url(#{id_p}Booster)" />
      <!-- Right Core Body -->
      <rect x="438" y="230" width="36" height="485" fill="url(#{id_p}Booster)" />
      <!-- Grid Fin Right Booster -->
      <rect x="474" y="250" width="22" height="15" fill="url(#{id_p}Wing)" stroke-width="1.2" />
      <line x1="486" y1="250" x2="486" y2="265" stroke-width="1" />
      <!-- Folded Leg Right Booster -->
      <polygon points="474,550 496,715 488,715 474,605" fill="currentColor" opacity="0.3" stroke-width="1.6" />
      <!-- Octaweb & Engine Bells -->
      <polygon points="436,715 476,715 472,735 440,735" fill="currentColor" opacity="0.5" />
      <path d="M 442 735 L 440 748 L 454 748 L 450 735 Z" fill="currentColor" opacity="0.6" />
      <path d="M 458 735 L 456 748 L 470 748 L 466 735 Z" fill="currentColor" opacity="0.6" />
    </g>

    <!-- Structural Inter-Core Braces -->
    <line x1="362" y1="240" x2="382" y2="240" stroke="currentColor" stroke-width="3" />
    <line x1="418" y1="240" x2="438" y2="240" stroke="currentColor" stroke-width="3" />
    <line x1="362" y1="680" x2="382" y2="680" stroke="currentColor" stroke-width="3" />
    <line x1="418" y1="680" x2="438" y2="680" stroke="currentColor" stroke-width="3" />

    <!-- Center Core & Upper Stage with 5.2m Fairing -->
    <!-- Payload Fairing -->
    <path d="M 374 150 L 374 105 C 374 60 400 35 400 35 C 400 35 426 60 426 105 L 426 150 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />
    <!-- Center Upper Stage -->
    <rect x="382" y="150" width="36" height="95" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2" />
    <!-- Center Interstage -->
    <rect x="382" y="245" width="36" height="35" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="2" />
    <!-- Center Core Body -->
    <rect x="382" y="280" width="36" height="435" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <!-- Center Core Octaweb & Engines -->
    <polygon points="380,715 420,715 416,735 384,735" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="2" />
    <path d="M 386 735 L 383 750 L 398 750 L 394 735 Z" fill="currentColor" opacity="0.7" stroke="currentColor" stroke-width="1.6" />
    <path d="M 404 735 L 402 750 L 417 750 L 413 735 Z" fill="currentColor" opacity="0.7" stroke="currentColor" stroke-width="1.6" />"""
    return wrap_svg("fh", "98.0 M", "WIDTH 12.2 M", content)

# 6. Delta III B (Delta Heavy Variant: 5m crew fairing, launch abort tower, heavy strap-ons, 120m)
def svg_delta_3b():
    id_p = "d3b"
    content = f"""    <!-- Launch Abort Tower at Apex -->
    <line x1="400" y1="35" x2="400" y2="85" stroke="currentColor" stroke-width="2.2" />
    <polygon points="397,35 403,35 401,50 399,50" fill="currentColor" />
    <polygon points="392,85 408,85 414,125 386,125" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2" />

    <!-- 5-Meter Heavy Payload / Crew Fairing -->
    <path d="M 365 180 L 365 140 C 365 110 385 85 400 85 C 415 85 435 110 435 140 L 435 180 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <!-- Second Stage Cryogenic Tank -->
    <rect x="365" y="180" width="70" height="75" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <line x1="365" y1="215" x2="435" y2="215" stroke="currentColor" stroke-width="1" opacity="0.65" />

    <!-- Interstage Transition -->
    <polygon points="365,255 435,255 425,290 375,290" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2" />

    <!-- Core Booster (Stretched First Stage) -->
    <rect x="375" y="290" width="50" height="425" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <g stroke="currentColor" stroke-width="1" opacity="0.65">
      <line x1="375" y1="360" x2="425" y2="360" />
      <line x1="375" y1="440" x2="425" y2="440" />
      <line x1="375" y1="520" x2="425" y2="520" />
      <line x1="375" y1="610" x2="425" y2="610" />
      <line x1="375" y1="680" x2="425" y2="680" />
    </g>

    <!-- Heavy Strap-On Solid Rocket Boosters (GEM-60 style) -->
    <!-- Left Heavy Booster -->
    <g stroke="currentColor" stroke-width="2">
      <path d="M 335 440 C 335 390 355 365 355 365 C 355 365 375 390 375 440 Z" fill="url(#{id_p}Booster)" />
      <rect x="335" y="440" width="40" height="270" fill="url(#{id_p}Booster)" />
      <line x1="335" y1="530" x2="375" y2="530" stroke-width="1" />
      <line x1="335" y1="620" x2="375" y2="620" stroke-width="1" />
      <polygon points="330,710 380,710 375,735 335,735" fill="currentColor" opacity="0.4" />
    </g>
    <!-- Right Heavy Booster -->
    <g stroke="currentColor" stroke-width="2">
      <path d="M 425 440 C 425 390 445 365 445 365 C 445 365 465 390 465 440 Z" fill="url(#{id_p}Booster)" />
      <rect x="425" y="440" width="40" height="270" fill="url(#{id_p}Booster)" />
      <line x1="425" y1="530" x2="465" y2="530" stroke-width="1" />
      <line x1="425" y1="620" x2="465" y2="620" stroke-width="1" />
      <polygon points="420,710 470,710 465,735 425,735" fill="currentColor" opacity="0.4" />
    </g>

    <!-- Core Main Engines -->
    <path d="M 385 715 L 380 745 L 415 745 L 410 715 Z" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="2" />"""
    return wrap_svg("d3b", "120.0 M", "CORE 5.0 M", content)

# 7. Space Shuttle v2 (Modernized Next-Gen Orbiter: blended delta wing, canted winglets, panoramic canopy, twin V-tail fins)
def svg_shuttle_v2():
    id_p = "sts2"
    content = f"""    <!-- Space Shuttle v2 Next-Gen Orbiter (Top-Down / Dorsal Technical Blueprint) -->

    <!-- Advanced Blended Delta Wings with Organic Strakes and Canted Winglets -->
    <!-- Left Wing Structure -->
    <path d="M 364 200 C 350 290 325 380 305 440 L 145 580 L 145 615 L 345 615 L 362 605 Z" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />
    <!-- Right Wing Structure -->
    <path d="M 436 200 C 450 290 475 380 495 440 L 655 580 L 655 615 L 455 615 L 438 605 Z" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />

    <!-- Modern Canted Aerodynamic Winglets (Vertical Wingtips) -->
    <!-- Left Winglet -->
    <polygon points="145,580 132,540 142,545 145,615" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="1.8" />
    <line x1="138" y1="545" x2="145" y2="600" stroke="currentColor" stroke-width="1" />
    <!-- Right Winglet -->
    <polygon points="655,580 668,540 658,545 655,615" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="1.8" />
    <line x1="662" y1="545" x2="655" y2="600" stroke="currentColor" stroke-width="1" />

    <!-- Sleek Stealth Thermal Leading Edge Chine (Black Carbon-Silicon Matrix) -->
    <path d="M 364 200 C 350 290 325 380 305 440 L 145 580 L 145 590 L 310 448 C 330 388 355 298 368 208 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="1.2" />
    <path d="M 436 200 C 450 290 475 380 495 440 L 655 580 L 655 590 L 490 448 C 470 388 445 298 432 208 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="1.2" />

    <!-- Modern Multi-Segment Fly-By-Wire Elevons -->
    <g stroke="currentColor" stroke-width="1.4">
      <!-- Left Elevons (3 Segments) -->
      <polygon points="160,592 220,592 220,612 160,612" fill="url(#{id_p}Booster)" />
      <polygon points="226,592 286,592 286,612 226,612" fill="url(#{id_p}Booster)" />
      <polygon points="292,592 342,592 342,612 292,612" fill="url(#{id_p}Booster)" />
      <!-- Right Elevons (3 Segments) -->
      <polygon points="458,592 508,592 508,612 458,612" fill="url(#{id_p}Booster)" />
      <polygon points="514,592 574,592 574,612 514,612" fill="url(#{id_p}Booster)" />
      <polygon points="580,592 640,592 640,612 580,612" fill="url(#{id_p}Booster)" />
    </g>

    <!-- Modern Composite Fuselage Body -->
    <path d="M 384 85 C 384 55 400 48 400 48 C 400 48 416 55 416 85 L 442 200 L 446 510 L 434 625 L 366 625 L 354 510 L 358 200 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />

    <!-- Streamlined Aerodynamic Carbon Nose Cap -->
    <path d="M 386 82 C 386 58 400 50 400 50 C 400 50 414 58 414 82 C 414 96 386 96 386 82 Z" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="1.8" />

    <!-- Integrated Conformal Flush RCS Thrusters -->
    <g fill="currentColor" opacity="0.7">
      <line x1="388" y1="78" x2="388" y2="90" stroke="currentColor" stroke-width="1.5" />
      <line x1="412" y1="78" x2="412" y2="90" stroke="currentColor" stroke-width="1.5" />
      <circle cx="390" cy="84" r="1.5" />
      <circle cx="410" cy="84" r="1.5" />
    </g>

    <!-- Modern Panoramic Glass Flight Deck (Wraparound Dark Canopy Visor) -->
    <path d="M 382 120 C 388 112 400 110 400 110 C 400 110 412 112 418 120 L 415 132 C 408 126 400 124 400 124 C 400 124 392 126 385 132 Z" fill="currentColor" opacity="0.85" stroke="currentColor" stroke-width="1.2" />
    <line x1="400" y1="110" x2="400" y2="124" stroke="#ffffff" stroke-width="1.2" opacity="0.8" />

    <!-- Modern Payload Bay with Conformal Hexagonal Photovoltaic Radiator Doors -->
    <rect x="362" y="160" width="76" height="350" rx="3" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="1.5" />
    <line x1="400" y1="160" x2="400" y2="510" stroke="currentColor" stroke-width="1.8" />
    <line x1="362" y1="245" x2="438" y2="245" stroke="currentColor" stroke-width="1" opacity="0.65" />
    <line x1="362" y1="335" x2="438" y2="335" stroke="currentColor" stroke-width="1" opacity="0.65" />
    <line x1="362" y1="425" x2="438" y2="425" stroke="currentColor" stroke-width="1" opacity="0.65" />
    <!-- Hex / diamond panel pattern accents -->
    <g stroke="currentColor" stroke-width="0.8" opacity="0.4">
      <polygon points="380,180 390,175 400,180 400,190 390,195 380,190" fill="none" />
      <polygon points="400,180 410,175 420,180 420,190 410,195 400,190" fill="none" />
      <polygon points="380,270 390,265 400,270 400,280 390,285 380,280" fill="none" />
      <polygon points="400,270 410,265 420,270 420,280 410,285 400,280" fill="none" />
    </g>

    <!-- Modern Streamlined OMS Fairings -->
    <path d="M 354 480 C 340 505 334 545 336 620 L 364 620 Z" fill="url(#{id_p}Booster)" stroke="currentColor" stroke-width="1.8" />
    <path d="M 446 480 C 460 505 466 545 464 620 L 436 620 Z" fill="url(#{id_p}Booster)" stroke="currentColor" stroke-width="1.8" />

    <!-- Twin Canted Vertical Stabilizers (Modern V-Tail on OMS Pods) -->
    <!-- Left Canted Fin (Angled out at ~25°) -->
    <g stroke="currentColor" stroke-width="1.8">
      <polygon points="350,520 310,430 325,435 362,545" fill="url(#{id_p}Wing)" />
      <line x1="322" y1="455" x2="354" y2="528" stroke-width="1" opacity="0.6" />
    </g>
    <!-- Right Canted Fin (Angled out at ~25°) -->
    <g stroke="currentColor" stroke-width="1.8">
      <polygon points="450,520 490,430 475,435 438,545" fill="url(#{id_p}Wing)" />
      <line x1="478" y1="455" x2="446" y2="528" stroke-width="1" opacity="0.6" />
    </g>

    <!-- Modern Flush Aerospike / Advanced Linear Multi-Engine Cluster -->
    <polygon points="370,625 430,625 434,650 366,650" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2" />
    <!-- 3 Advanced Linear Aerospike Bells -->
    <ellipse cx="400" cy="652" rx="14" ry="12" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="1.8" />
    <ellipse cx="378" cy="678" rx="14" ry="12" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="1.8" />
    <ellipse cx="422" cy="678" rx="14" ry="12" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="1.8" />
    <circle cx="400" cy="652" r="6" fill="#ffffff" opacity="0.7" />
    <circle cx="378" cy="678" r="6" fill="#ffffff" opacity="0.7" />
    <circle cx="422" cy="678" r="6" fill="#ffffff" opacity="0.7" />"""
    return wrap_svg("sts2", "78.0 M", "SPAN 28.0 M", content)

# 8. Saturn Nova (NASA Nova C8 concept: 14m core, 8 F-1 engines, colossal direct-ascent rocket, 137m)
def svg_saturn_nova():
    id_p = "nova"
    content = f"""    <!-- Direct-Ascent Apollo/Mars Super Escape Tower -->
    <line x1="400" y1="30" x2="400" y2="100" stroke="currentColor" stroke-width="2.5" />
    <polygon points="396,30 404,30 402,50 398,50" fill="currentColor" />
    <line x1="390" y1="65" x2="410" y2="65" stroke="currentColor" stroke-width="1.4" />
    <!-- Tower Truss -->
    <line x1="394" y1="100" x2="400" y2="55" stroke="currentColor" stroke-width="1.2" />
    <line x1="406" y1="100" x2="400" y2="55" stroke="currentColor" stroke-width="1.2" />

    <!-- Massive Direct-Ascent Lander Command Shroud -->
    <polygon points="392,100 408,100 424,145 376,145" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <rect x="376" y="145" width="48" height="50" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />

    <!-- Upper Transition to 10m / 12m Stages -->
    <polygon points="376,195 424,195 438,265 362,265" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <rect x="362" y="265" width="76" height="110" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" />
    <line x1="362" y1="320" x2="438" y2="320" stroke="currentColor" stroke-width="1.2" opacity="0.7" />

    <!-- Giant Flared Interstage Transition to 14m Nova Core -->
    <polygon points="362,375 438,375 455,445 345,445" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" />
    <rect x="345" y="445" width="110" height="270" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.6" />

    <!-- First Stage Structural Stiffeners & Feedlines -->
    <line x1="365" y1="445" x2="365" y2="715" stroke="currentColor" stroke-width="1.4" opacity="0.6" />
    <line x1="385" y1="445" x2="385" y2="715" stroke="currentColor" stroke-width="1.4" opacity="0.6" />
    <line x1="415" y1="445" x2="415" y2="715" stroke="currentColor" stroke-width="1.4" opacity="0.6" />
    <line x1="435" y1="445" x2="435" y2="715" stroke="currentColor" stroke-width="1.4" opacity="0.6" />
    <line x1="345" y1="540" x2="455" y2="540" stroke="currentColor" stroke-width="1.4" opacity="0.7" />
    <line x1="345" y1="630" x2="455" y2="630" stroke="currentColor" stroke-width="1.4" opacity="0.7" />

    <!-- 4 Colossal Nova Stabilizing Fins -->
    <polygon points="345,630 275,715 275,735 345,715" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.4" />
    <polygon points="455,630 525,715 525,735 455,715" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.4" />

    <!-- 8 Massive F-1A Rocket Engines at Base -->
    <path d="M 345 715 L 340 755 L 358 755 L 355 715 Z" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="1.8" />
    <path d="M 358 715 L 355 755 L 373 755 L 370 715 Z" fill="currentColor" opacity="0.4" stroke="currentColor" stroke-width="1.8" />
    <path d="M 373 715 L 370 755 L 388 755 L 385 715 Z" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="1.8" />
    <path d="M 388 715 L 386 755 L 404 755 L 401 715 Z" fill="currentColor" opacity="0.7" stroke="currentColor" stroke-width="1.8" />
    <path d="M 404 715 L 402 755 L 420 755 L 417 715 Z" fill="currentColor" opacity="0.7" stroke="currentColor" stroke-width="1.8" />
    <path d="M 420 715 L 418 755 L 436 755 L 433 715 Z" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="1.8" />
    <path d="M 436 715 L 434 755 L 452 755 L 449 715 Z" fill="currentColor" opacity="0.5" stroke="currentColor" stroke-width="1.8" />"""
    return wrap_svg("nova", "137.0 M", "CORE 14.0 M", content)

# 9. Falcon v2 (Falcon Next-Gen: 4m carbon body, stealth swept grid fins, hot-staging vented ring, 95m)
def svg_falcon_v2():
    id_p = "f9v2"
    content = f"""    <!-- Enlarged 6m Payload Fairing with RCS Thruster Blocks -->
    <path d="M 374 165 L 374 110 C 374 65 400 40 400 40 C 400 40 426 65 426 110 L 426 165 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" />
    <line x1="400" y1="40" x2="400" y2="165" stroke="currentColor" stroke-width="1" stroke-dasharray="3 2" />
    <!-- RCS Thruster Pods -->
    <rect x="368" y="90" width="6" height="12" fill="currentColor" opacity="0.7" />
    <rect x="426" y="90" width="6" height="12" fill="currentColor" opacity="0.7" />

    <!-- Second Stage (Full Carbon Composite) -->
    <rect x="380" y="165" width="40" height="100" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />

    <!-- Hot Staging Vented Interstage Ring (Perforated) -->
    <g stroke="currentColor" stroke-width="1.5">
      <rect x="380" y="265" width="40" height="40" fill="currentColor" opacity="0.2" />
      <line x1="385" y1="275" x2="385" y2="295" stroke-width="2" />
      <line x1="395" y1="275" x2="395" y2="295" stroke-width="2" />
      <line x1="405" y1="275" x2="405" y2="295" stroke-width="2" />
      <line x1="415" y1="275" x2="415" y2="295" stroke-width="2" />
    </g>

    <!-- Advanced Swept Stealth Grid Fins -->
    <polygon points="380,270 338,260 338,285 380,290" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="1.8" />
    <polygon points="420,270 462,260 462,285 420,290" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="1.8" />

    <!-- First Stage Booster Body -->
    <rect x="380" y="305" width="40" height="410" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <line x1="410" y1="165" x2="410" y2="715" stroke="currentColor" stroke-width="1.6" />
    <g stroke="currentColor" stroke-width="0.8" opacity="0.6">
      <line x1="380" y1="380" x2="420" y2="380" />
      <line x1="380" y1="460" x2="420" y2="460" />
      <line x1="380" y1="540" x2="420" y2="540" />
      <line x1="380" y1="620" x2="420" y2="620" />
    </g>

    <!-- Flush Aero Landing Leg Fairings -->
    <polygon points="380,520 350,715 362,715 380,590" fill="currentColor" opacity="0.35" stroke="currentColor" stroke-width="1.8" />
    <polygon points="420,520 450,715 438,715 420,590" fill="currentColor" opacity="0.35" stroke="currentColor" stroke-width="1.8" />

    <!-- High-Expansion Next-Gen Engine Cluster -->
    <polygon points="378,715 422,715 418,735 382,735" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="2" />
    <path d="M 384 735 L 380 752 L 396 752 L 392 735 Z" fill="currentColor" opacity="0.7" stroke="currentColor" stroke-width="1.6" />
    <path d="M 395 735 L 392 755 L 408 755 L 405 735 Z" fill="currentColor" opacity="0.8" stroke="currentColor" stroke-width="1.8" />
    <path d="M 408 735 L 404 752 L 420 752 L 416 735 Z" fill="currentColor" opacity="0.7" stroke="currentColor" stroke-width="1.6" />"""
    return wrap_svg("f9v2", "95.0 M", "CORE 4.0 M", content)

# 10. Big Falcon Rocket (SpaceX BFR / Starship + Super Heavy: 9m diameter, forward flaps, aft delta fins, 33 Raptors, 128m)
def svg_bfr():
    id_p = "bfr"
    content = f"""    <!-- Starship Spacecraft (Second Stage) -->
    <!-- Forward Actuated Aerodynamic Flaps -->
    <polygon points="372,130 330,140 330,165 372,150" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" />
    <polygon points="428,130 470,140 470,165 428,150" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" />

    <!-- Starship Gothic Curved Nosecone & Hull -->
    <path d="M 372 320 L 372 160 C 372 90 400 45 400 45 C 400 45 428 90 428 160 L 428 320 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" />
    <!-- Thermal Protection Tile Division Curve -->
    <path d="M 400 45 Q 418 160 418 320" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3 2" opacity="0.7" />
    <!-- Cabin Windows Row -->
    <circle cx="400" cy="115" r="4" fill="currentColor" opacity="0.8" />
    <circle cx="390" cy="120" r="3" fill="currentColor" opacity="0.8" />
    <circle cx="410" cy="120" r="3" fill="currentColor" opacity="0.8" />

    <!-- Aft Large Aerodynamic Flaps / Fins at Base of Ship -->
    <polygon points="372,250 310,320 320,335 372,310" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.2" />
    <polygon points="428,250 490,320 480,335 428,310" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2.2" />

    <!-- Interstage Separation Ring (Vented Hot Staging) -->
    <rect x="372" y="320" width="56" height="30" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="2.2" />
    <line x1="380" y1="320" x2="380" y2="350" stroke="currentColor" stroke-width="1.5" />
    <line x1="390" y1="320" x2="390" y2="350" stroke="currentColor" stroke-width="1.5" />
    <line x1="400" y1="320" x2="400" y2="350" stroke="currentColor" stroke-width="1.5" />
    <line x1="410" y1="320" x2="410" y2="350" stroke="currentColor" stroke-width="1.5" />
    <line x1="420" y1="320" x2="420" y2="350" stroke="currentColor" stroke-width="1.5" />

    <!-- Super Heavy Booster (9m diameter stainless steel core) -->
    <rect x="372" y="350" width="56" height="365" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" />

    <!-- 4 Diamond-Shaped Planar Titanium Grid Fins -->
    <polygon points="372,360 340,350 330,365 372,375" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="1.8" />
    <polygon points="428,360 460,350 470,365 428,375" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="1.8" />

    <!-- Booster Weld Ring Sections -->
    <g stroke="currentColor" stroke-width="1" opacity="0.6">
      <line x1="372" y1="415" x2="428" y2="415" />
      <line x1="372" y1="475" x2="428" y2="475" />
      <line x1="372" y1="535" x2="428" y2="535" />
      <line x1="372" y1="595" x2="428" y2="595" />
      <line x1="372" y1="655" x2="428" y2="655" />
    </g>

    <!-- 33 Raptor Engine Cluster & Skirt -->
    <polygon points="370,715 430,715 425,745 375,745" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="2" />
    <circle cx="388" cy="740" r="5" fill="currentColor" opacity="0.8" />
    <circle cx="400" cy="740" r="5" fill="currentColor" opacity="0.8" />
    <circle cx="412" cy="740" r="5" fill="currentColor" opacity="0.8" />"""
    return wrap_svg("bfr", "106.0 M", "CORE 9.0 M", content)

# 11. Delta IV (ULA Delta IV Heavy: 3 Common Booster Cores side-by-side, 3 RS-68A engines, 130m)
def svg_delta_4():
    id_p = "d4"
    content = f"""    <!-- Left Common Booster Core (CBC) -->
    <g stroke="currentColor" stroke-width="2.2">
      <!-- Conical Nosecone -->
      <polygon points="325,230 365,230 345,170" fill="url(#{id_p}Booster)" />
      <!-- Left CBC Body (5.1m diameter) -->
      <rect x="325" y="230" width="40" height="485" fill="url(#{id_p}Booster)" />
      <!-- Weld Rings -->
      <line x1="325" y1="330" x2="365" y2="330" stroke-width="1" opacity="0.65" />
      <line x1="325" y1="450" x2="365" y2="450" stroke-width="1" opacity="0.65" />
      <line x1="325" y1="570" x2="365" y2="570" stroke-width="1" opacity="0.65" />
      <!-- RS-68A Main Engine Bell & Turbine Exhaust Duct -->
      <polygon points="332,715 358,715 362,745 328,745" fill="currentColor" opacity="0.5" />
      <line x1="358" y1="715" x2="362" y2="745" stroke-width="3" />
    </g>

    <!-- Right Common Booster Core (CBC) -->
    <g stroke="currentColor" stroke-width="2.2">
      <!-- Conical Nosecone -->
      <polygon points="435,230 475,230 455,170" fill="url(#{id_p}Booster)" />
      <!-- Right CBC Body (5.1m diameter) -->
      <rect x="435" y="230" width="40" height="485" fill="url(#{id_p}Booster)" />
      <!-- Weld Rings -->
      <line x1="435" y1="330" x2="475" y2="330" stroke-width="1" opacity="0.65" />
      <line x1="435" y1="450" x2="475" y2="450" stroke-width="1" opacity="0.65" />
      <line x1="435" y1="570" x2="475" y2="570" stroke-width="1" opacity="0.65" />
      <!-- RS-68A Main Engine Bell & Turbine Exhaust Duct -->
      <polygon points="442,715 468,715 472,745 438,745" fill="currentColor" opacity="0.5" />
      <line x1="468" y1="715" x2="472" y2="745" stroke-width="3" />
    </g>

    <!-- Heavy Structural Attach Struts -->
    <line x1="365" y1="240" x2="380" y2="240" stroke="currentColor" stroke-width="3.5" />
    <line x1="420" y1="240" x2="435" y2="240" stroke="currentColor" stroke-width="3.5" />
    <line x1="365" y1="680" x2="380" y2="680" stroke="currentColor" stroke-width="3.5" />
    <line x1="420" y1="680" x2="435" y2="680" stroke="currentColor" stroke-width="3.5" />

    <!-- Center Common Booster Core (CCBC) -->
    <!-- 5.1-meter Metallic Payload Fairing -->
    <path d="M 375 160 L 375 110 C 375 65 400 40 400 40 C 400 40 425 65 425 110 L 425 160 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" />
    <!-- Delta Cryogenic Second Stage (DCSS) -->
    <rect x="375" y="160" width="50" height="85" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.2" />
    <line x1="375" y1="205" x2="425" y2="205" stroke="currentColor" stroke-width="1.2" opacity="0.7" />
    <!-- Center Core Body -->
    <rect x="380" y="245" width="40" height="470" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" />
    <!-- Center Engine RS-68A -->
    <polygon points="387,715 413,715 417,745 383,745" fill="currentColor" opacity="0.6" stroke="currentColor" stroke-width="2.2" />
    <line x1="413" y1="715" x2="417" y2="745" stroke="currentColor" stroke-width="3.5" />"""
    return wrap_svg("d4", "130.0 M", "WIDTH 15.0 M", content)

# 12. Interplanetary Shuttle (SpaceX ITS - Interplanetary Transport System: 12m full stack, 140m)
def svg_interplanetary_shuttle():
    id_p = "ips"
    content = f"""    <!-- SpaceX Interplanetary Transport System (ITS) Full Launch Stack (12m Architecture) -->

    <!-- ==================== UPPER STAGE: ITS SPACESHIP ==================== -->

    <!-- Spaceship Lateral Aerodynamic Sponsons / Delta Wings (Outer Fairings) -->
    <!-- Left Wing Sponson -->
    <path d="M 365 135 C 352 160 332 185 332 215 L 332 245 C 332 252 342 255 358 255 L 365 255 Z" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
    <!-- Right Wing Sponson -->
    <path d="M 435 135 C 448 160 468 185 468 215 L 468 245 C 468 252 458 255 442 255 L 435 255 Z" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />

    <!-- Wing Sponson Surface Lettering (USA) -->
    <g font-family="sans-serif" font-weight="700" font-size="7.5" fill="currentColor" opacity="0.75" letter-spacing="1.5" text-anchor="middle">
      <text x="345" y="190">U</text>
      <text x="345" y="202">S</text>
      <text x="345" y="214">A</text>
      <text x="455" y="190">U</text>
      <text x="455" y="202">S</text>
      <text x="455" y="214">A</text>
    </g>

    <!-- Wing Trailing Edge RCS Thruster Cluster Dots -->
    <circle cx="337" cy="246" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="341" cy="246" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="345" cy="246" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="463" cy="246" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="459" cy="246" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="455" cy="246" r="1.5" fill="currentColor" opacity="0.8" />

    <!-- Spaceship Main Aerodynamic Fuselage (12m Diameter Ogive Hull) -->
    <!-- Ogive Nose transitioning to Cylindrical Base at Y=255 -->
    <path d="M 400 45 C 388 55 365 95 365 140 L 365 255 L 435 255 L 435 140 C 435 95 412 55 400 45 Z" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" />

    <!-- Black Carbon-Composite Thermal Nose Cap -->
    <path d="M 400 45 C 392 51 385 58 382 66 L 418 66 C 415 58 408 51 400 45 Z" fill="currentColor" opacity="0.75" stroke="currentColor" stroke-width="1.8" />
    <line x1="384" y1="62" x2="416" y2="62" stroke="currentColor" stroke-width="0.8" opacity="0.4" />

    <!-- Multiple Tiers of Passenger Cabin Portholes / Windows -->
    <g fill="currentColor" opacity="0.85">
      <!-- Tier 1 (Apex): 4 Portholes -->
      <circle cx="392" cy="74" r="1.6" />
      <circle cx="397" cy="74" r="1.6" />
      <circle cx="403" cy="74" r="1.6" />
      <circle cx="408" cy="74" r="1.6" />

      <!-- Tier 2: 8 Portholes -->
      <circle cx="380" cy="88" r="1.6" />
      <circle cx="386" cy="88" r="1.6" />
      <circle cx="392" cy="88" r="1.6" />
      <circle cx="397" cy="88" r="1.6" />
      <circle cx="403" cy="88" r="1.6" />
      <circle cx="408" cy="88" r="1.6" />
      <circle cx="414" cy="88" r="1.6" />
      <circle cx="420" cy="88" r="1.6" />

      <!-- Tier 3: 12 Portholes -->
      <circle cx="372" cy="102" r="1.6" />
      <circle cx="377" cy="102" r="1.6" />
      <circle cx="382" cy="102" r="1.6" />
      <circle cx="387" cy="102" r="1.6" />
      <circle cx="392" cy="102" r="1.6" />
      <circle cx="397" cy="102" r="1.6" />
      <circle cx="403" cy="102" r="1.6" />
      <circle cx="408" cy="102" r="1.6" />
      <circle cx="413" cy="102" r="1.6" />
      <circle cx="418" cy="102" r="1.6" />
      <circle cx="423" cy="102" r="1.6" />
      <circle cx="428" cy="102" r="1.6" />

      <!-- Tier 4: 12 Portholes -->
      <circle cx="370" cy="116" r="1.6" />
      <circle cx="375" cy="116" r="1.6" />
      <circle cx="380" cy="116" r="1.6" />
      <circle cx="385" cy="116" r="1.6" />
      <circle cx="390" cy="116" r="1.6" />
      <circle cx="395" cy="116" r="1.6" />
      <circle cx="405" cy="116" r="1.6" />
      <circle cx="410" cy="116" r="1.6" />
      <circle cx="415" cy="116" r="1.6" />
      <circle cx="420" cy="116" r="1.6" />
      <circle cx="425" cy="116" r="1.6" />
      <circle cx="430" cy="116" r="1.6" />
    </g>

    <!-- Large Panoramic Observation Viewports (Left & Right) -->
    <rect x="372" y="145" width="16" height="24" rx="4" fill="none" stroke="currentColor" stroke-width="1.8" />
    <rect x="412" y="145" width="16" height="24" rx="4" fill="none" stroke="currentColor" stroke-width="1.8" />

    <!-- Center Aerodynamic Chine & Recessed Thermal Shield -->
    <path d="M 400 95 L 405 200 L 400 255 L 395 200 Z" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.6" />
    <polygon points="388,205 412,205 418,255 382,255" fill="currentColor" opacity="0.35" stroke="currentColor" stroke-width="1.2" />
    <!-- Inner Dark Ventral Sponson Chine -->
    <polygon points="392,215 408,215 414,255 386,255" fill="currentColor" opacity="0.65" />

    <!-- Attitude Thruster Quads (Nose Section) -->
    <circle cx="385" cy="130" r="1.5" fill="currentColor" />
    <circle cx="389" cy="130" r="1.5" fill="currentColor" />
    <circle cx="411" cy="130" r="1.5" fill="currentColor" />
    <circle cx="415" cy="130" r="1.5" fill="currentColor" />

    <!-- ==================== INTERSTAGE SEPARATION RING ==================== -->
    <rect x="365" y="255" width="70" height="15" fill="currentColor" opacity="0.85" stroke="currentColor" stroke-width="1.8" />
    <line x1="365" y1="262" x2="435" y2="262" stroke="url(#{id_p}Body)" stroke-width="1" opacity="0.5" />

    <!-- ==================== FIRST STAGE: ITS BOOSTER ==================== -->

    <!-- Booster Cylindrical Core (12m Diameter) -->
    <rect x="365" y="270" width="70" height="440" fill="url(#{id_p}Body)" stroke="currentColor" stroke-width="2.4" />

    <!-- Diamond Planar Titanium Grid Fin Assembly (Upper Core) -->
    <!-- Grid Fin Mounting Bracket -->
    <rect x="394" y="282" width="12" height="6" fill="currentColor" opacity="0.75" />
    <!-- Diamond Grid Fin -->
    <g stroke="currentColor" stroke-width="1.4">
      <polygon points="400,288 418,312 400,338 382,312" fill="currentColor" opacity="0.35" stroke-width="1.8" />
      <!-- Internal Grid Mesh Lattice Lines -->
      <line x1="388" y1="304" x2="412" y2="304" stroke-width="0.9" />
      <line x1="384" y1="312" x2="416" y2="312" stroke-width="1" />
      <line x1="388" y1="320" x2="412" y2="320" stroke-width="0.9" />
      <line x1="392" y1="328" x2="408" y2="328" stroke-width="0.9" />
      <line x1="394" y1="296" x2="394" y2="330" stroke-width="0.9" />
      <line x1="400" y1="288" x2="400" y2="338" stroke-width="1" />
      <line x1="406" y1="296" x2="406" y2="330" stroke-width="0.9" />
    </g>

    <!-- Longitudinal Aerodynamic Raceways / Stringers -->
    <line x1="371" y1="270" x2="371" y2="710" stroke="currentColor" stroke-width="1" opacity="0.4" />
    <line x1="429" y1="270" x2="429" y2="710" stroke="currentColor" stroke-width="1" opacity="0.4" />

    <!-- Prominent Vertical "SPACEX" Fuselage Lettering -->
    <g font-family="sans-serif" font-weight="900" font-size="20" fill="currentColor" letter-spacing="4" text-anchor="middle" opacity="0.9">
      <text x="400" y="380">S</text>
      <text x="400" y="412">P</text>
      <text x="400" y="444">A</text>
      <text x="400" y="476">C</text>
      <text x="400" y="508">E</text>
      <!-- Stylized X with swoosh -->
      <text x="400" y="540">X</text>
      <path d="M 374 542 Q 400 535 436 525" stroke="currentColor" stroke-width="2.6" fill="none" />
    </g>

    <!-- National Insignia Flag Emblem (Lower Booster Core) -->
    <g stroke="currentColor" stroke-width="1">
      <rect x="382" y="582" width="36" height="22" fill="currentColor" opacity="0.1" />
      <!-- Flag Stripes -->
      <line x1="382" y1="586" x2="418" y2="586" stroke-width="1" />
      <line x1="382" y1="590" x2="418" y2="590" stroke-width="1" />
      <line x1="382" y1="594" x2="418" y2="594" stroke-width="1" />
      <line x1="382" y1="598" x2="418" y2="598" stroke-width="1" />
      <line x1="382" y1="602" x2="418" y2="602" stroke-width="1" />
      <!-- Canton -->
      <rect x="382" y="582" width="16" height="11" fill="currentColor" opacity="0.75" />
    </g>

    <!-- Booster Propellant Tank Weld Seams -->
    <line x1="365" y1="360" x2="435" y2="360" stroke="currentColor" stroke-width="1" opacity="0.5" />
    <line x1="365" y1="565" x2="435" y2="565" stroke="currentColor" stroke-width="1" opacity="0.5" />
    <line x1="365" y1="620" x2="435" y2="620" stroke="currentColor" stroke-width="1" opacity="0.5" />

    <!-- Aft Flared Aerodynamic Landing Leg Fairings (Matching ITS Stance) -->
    <!-- Left Flare -->
    <polygon points="365,640 344,710 365,710" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" />
    <line x1="352" y1="675" x2="352" y2="710" stroke="currentColor" stroke-width="1" opacity="0.6" />
    <!-- Right Flare -->
    <polygon points="435,640 456,710 435,710" fill="url(#{id_p}Wing)" stroke="currentColor" stroke-width="2" />
    <line x1="448" y1="675" x2="448" y2="710" stroke="currentColor" stroke-width="1" opacity="0.6" />
    <!-- Center Flared Chine Ridge -->
    <line x1="400" y1="640" x2="400" y2="710" stroke="currentColor" stroke-width="1.8" />
    <polygon points="394,675 406,675 404,710 396,710" fill="currentColor" opacity="0.25" stroke="currentColor" stroke-width="1.2" />

    <!-- Aft Dark Engine Skirt Base -->
    <rect x="358" y="710" width="84" height="16" fill="currentColor" opacity="0.85" stroke="currentColor" stroke-width="2" />

    <!-- 42 Raptor Engine Cluster Bell Nozzles (Dense Array at Base) -->
    <g stroke="currentColor" stroke-width="1.2">
      <!-- Outer Ring Engine Bell Nozzles protruding slightly from base -->
      <polygon points="361,726 369,726 368,734 362,734" fill="currentColor" opacity="0.75" />
      <polygon points="370,726 378,726 377,734 371,734" fill="currentColor" opacity="0.75" />
      <polygon points="379,726 387,726 386,734 380,734" fill="currentColor" opacity="0.75" />
      <polygon points="388,726 396,726 395,734 389,734" fill="currentColor" opacity="0.75" />
      <polygon points="396,726 404,726 403,734 397,734" fill="currentColor" opacity="0.85" />
      <polygon points="404,726 412,726 411,734 405,734" fill="currentColor" opacity="0.75" />
      <polygon points="413,726 421,726 420,734 414,734" fill="currentColor" opacity="0.75" />
      <polygon points="422,726 430,726 429,734 423,734" fill="currentColor" opacity="0.75" />
      <polygon points="431,726 439,726 438,734 432,734" fill="currentColor" opacity="0.75" />
    </g>"""
    return wrap_svg("ips", "140.0 M", "CORE 12.0 M · SPAN 18.0 M", content)

# Map all 12 files
ROCKETS = {
    "rocket-delta-3a.svg": svg_delta_3a,
    "rocket-shuttle.svg": svg_shuttle,
    "rocket-saturn-x.svg": svg_saturn_x,
    "rocket-falcon.svg": svg_falcon,
    "rocket-falcon-heavy.svg": svg_falcon_heavy,
    "rocket-delta-3b.svg": svg_delta_3b,
    "rocket-shuttle-v2.svg": svg_shuttle_v2,
    "rocket-saturn-nova.svg": svg_saturn_nova,
    "rocket-falcon-v2.svg": svg_falcon_v2,
    "rocket-bfr.svg": svg_bfr,
    "rocket-delta-4.svg": svg_delta_4,
    "rocket-interplanetary-shuttle.svg": svg_interplanetary_shuttle,
}

for filename, func in ROCKETS.items():
    path = os.path.join(SVG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(func())
    print(f"Generated {filename}")

print(f"Successfully generated all {len(ROCKETS)} rocket SVG wireframes in {SVG_DIR}")
