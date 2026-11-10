#!/usr/bin/env python3
"""
Generate animated SVG illustrations for infrastructure.html (#energy section).

Generates:
1. icons/infrastructure/fusion-grid-en.svg & fusion-grid-hu.svg (1160x520)
   Commercial Hydrogen Fusion Power Complex and Intelligent Grid

Visual Concept & Animation:
- Cutaway of Tokamak / Stellarator Chamber: Glowing deuterium-tritium plasma vortex
  pulsating in the magnetic confinement chamber (@keyframes pulse + rotating particle rings).
- Magnetic Coils and Cryostat: High-temperature superconducting magnet fields rendered
  with glowing flux lines.
- Live Grid Power Transmission: Animated dashed energy flows routing high-voltage power
  across the three provinces, with live telemetry gauges.

Links standalone SVGs into en/infrastructure.html and hu/infrastructure.html (#energy section) via <img> tags.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "icons" / "infrastructure"

W, H = 1160, 520

INK = "#04121c"
PANEL_BG = "#061826"
GOLD = "#f5c46e"
ORANGE = "#ff7b29"
PLASMA_CORE = "#fff7d6"
PLASMA_MID = "#ff9233"
PLASMA_EDGE = "#c026d3"
CYAN = "#38bdf8"
BLUE = "#6BA4D9"
GREEN = "#2ecc71"
MUTED = "#9ec5db"


def n(val: float) -> str:
    if isinstance(val, int):
        return str(val)
    return f"{val:.1f}".rstrip("0").rstrip(".")


def polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def arc_path(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f"M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 {large} {sweep} {n(x1)},{n(y1)}"


def d_coil_path(cx: float, cy: float, r_in: float, r_out: float, h_half: float, side: int = 1) -> str:
    """Return a D-shaped toroidal field coil path on the left (side=-1) or right (side=1) of cx."""
    x_in = cx + side * r_in
    x_out = cx + side * r_out
    x_ctrl = cx + side * (r_out + (r_out - r_in) * 0.28)
    y_top = cy - h_half
    y_bot = cy + h_half
    return (
        f"M{n(x_in)},{n(y_top)} "
        f"C{n(x_ctrl)},{n(y_top)} {n(x_ctrl)},{n(y_bot)} {n(x_in)},{n(y_bot)} "
        f"Z"
    )


def build_fusion_grid_svg(lang: str = "en") -> str:
    is_hu = lang == "hu"
    clip_id = "fg-clip-hu" if is_hu else "fg-clip-en"

    if is_hu:
        hud_title = "KERESKEDELMI HIDROGÉNFÚZIÓS KOMPLEXUM ÉS INTELLIGENS HÁLÓZAT"
        hud_status = "5 REAKTOR AKTÍV · 12,8 GW"
        zone1_hdr = "01 // TOKAMAK-SZTELLARÁTOR MÁGNESES ÖSSZETARTÁSÚ REAKTORMAG"
        zone2_hdr = "02 // ±800 KV HVDC INTELLIGENS HÁLÓZAT ÉS ÉLŐ TELEMETRIA"

        lbl_solenoid = "KÖZPONTI SZOLENOID"
        lbl_solenoid_sub = "INDUKCIÓS MAG · 20 K"
        lbl_hts_coil = "REBCO SZUPRAVEZETŐ TEKERCSEK"
        lbl_hts_sub = "18,5 T MÁGNESES TÉR"
        lbl_plasma = "D-T PLAZMAÖRVÉNY (150M °C)"
        lbl_plasma_sub = "FORGÓ RÉSZECSKEGYŰRŰK · Q = 18,4"
        lbl_blanket = "LÍTIUM TRÍCIUMKÖPENY ÉS KRIOSZTÁT"
        lbl_blanket_sub = "HŐKINYERÉS ÉS NEUTRONPAJZS"

        lbl_nbi = "NBI FŰTÉS"
        lbl_nbi_sub = "110 MW"
        lbl_hvdc_hub = "HVDC KONVERTER"
        lbl_hvdc_sub = "±800 KV"

        g1_title = "FÚZIÓS RÉSZARÁNY"
        g1_val = "27%"
        g1_sub1 = "5 AKTÍV REAKTOR (2017 ÓTA)"
        g1_sub2 = "D-T MAGHŐMÉRSÉKLET: 150M °C"
        g1_pill = "ALAPERŐMŰ: 12,8 GW"

        g2_title = "TISZTA ENERGIA MIX"
        g2_val = "91%"
        g2_sub1 = "FÚZIÓ · NAP · ATOM · VÍZ · SZÉL"
        g2_sub2 = "120 HIBRID POWERPACK ÁLLOMÁS"
        g2_pill = "2035: KARBONSEMLEGES"

        g3_title = "SZUPRAVEZETŐ TÉR"
        g3_val = "18,5 T"
        g3_sub1 = "KRIOSZTÁT HŰTÉS: 20 K (-253 °C)"
        g3_sub2 = "HÁLÓZATI FREKVENCIA: 60,00 HZ"
        g3_pill = "STABILITÁS: 99,998%"

        p1_name = "WAIKIKI TARTOMÁNY"
        p1_tz = "UTC-4 · KARIBI"
        p1_desc = "Nova Aurelia · Tenger alatti HVDC · 48 Powerpack"
        p1_load = "4,8 GW"
        p1_mix = "FÚZIÓ + NAPENERGIA"
        p1_stat = "SZINKRONBAN"

        p2_name = "AMAZÓNIA TARTOMÁNY"
        p2_tz = "UTC-4 · MEDENCE"
        p2_desc = "Vízerőmű alaperőmű · 34 Powerpack állomás"
        p2_load = "3,1 GW"
        p2_mix = "VÍZENERGIA + FÚZIÓ"
        p2_stat = "SZINKRONBAN"

        p3_name = "BRAZÍLIA TARTOMÁNY"
        p3_tz = "UTC-3 · ATLANTI"
        p3_desc = "São Pauló-i fúzió · Recife kikötő · 38 Powerpack"
        p3_load = "4,9 GW"
        p3_mix = "FÚZIÓ + VÍZENERGIA"
        p3_stat = "SZINKRONBAN"

        badge_l1 = "D-T MÁGNESES FÚZIÓ (2017 ÓTA)"
        badge_l2 = "PLAZMA: 150M °C · SZUPRAVEZETŐ: 18,5 T"
        badge_r1 = "INTELLIGENS NEMZETI HÁLÓZAT"
        badge_r2 = "3 TARTOMÁNY · 2 IDŐZÓNA · 120 POWERPACK"
        legend_items = [
            ("D-T plazmaáram", "plasma"),
            ("Szupravezető fluxus", "flux"),
            ("±800 kV HVDC átvitel", "grid"),
        ]
    else:
        hud_title = "COMMERCIAL HYDROGEN FUSION COMPLEX AND INTELLIGENT GRID"
        hud_status = "5 REACTORS ONLINE · 12.8 GW"
        zone1_hdr = "01 // TOKAMAK-STELLARATOR MAGNETIC CONFINEMENT CORE"
        zone2_hdr = "02 // ±800 KV HVDC INTELLIGENT GRID AND LIVE TELEMETRY"

        lbl_solenoid = "CENTRAL SOLENOID"
        lbl_solenoid_sub = "INDUCTION CORE · 20 K"
        lbl_hts_coil = "REBCO HTS MAGNET COILS"
        lbl_hts_sub = "18.5 T CONFINEMENT FIELD"
        lbl_plasma = "D-T PLASMA VORTEX (150M °C)"
        lbl_plasma_sub = "ROTATING PARTICLE RINGS · Q = 18.4"
        lbl_blanket = "LITHIUM BLANKET AND CRYOSTAT"
        lbl_blanket_sub = "THERMAL EXTRACTION SHIELD"

        lbl_nbi = "NBI INJECTOR"
        lbl_nbi_sub = "110 MW"
        lbl_hvdc_hub = "HVDC CONVERTER"
        lbl_hvdc_sub = "±800 KV"

        g1_title = "FUSION POWER SHARE"
        g1_val = "27%"
        g1_sub1 = "5 COMMERCIAL PLANTS (SINCE 2017)"
        g1_sub2 = "D-T CORE TEMP: 150M °C"
        g1_pill = "BASELOAD: 12.8 GW"

        g2_title = "CLEAN ENERGY SUPPLY"
        g2_val = "91%"
        g2_sub1 = "FUSION · SOLAR · NUCLEAR · HYDRO"
        g2_sub2 = "120 HYBRID POWERPACK STATIONS"
        g2_pill = "2035 CARBON-NEUTRAL"

        g3_title = "HTS MAGNETIC FIELD"
        g3_val = "18.5 T"
        g3_sub1 = "CRYOSTAT COOLING: 20 K (-253 °C)"
        g3_sub2 = "GRID FREQUENCY LOCK: 60.00 HZ"
        g3_pill = "STABILITY: 99.998%"

        p1_name = "WAIKIKI PROVINCE"
        p1_tz = "UTC-4 · CARIBBEAN"
        p1_desc = "Nova Aurelia · Subsea HVDC · 48 Powerpacks"
        p1_load = "4.8 GW"
        p1_mix = "FUSION + SOLAR"
        p1_stat = "NOMINAL"

        p2_name = "AMAZONIA PROVINCE"
        p2_tz = "UTC-4 · BASIN"
        p2_desc = "River Basin Hydro Baseload · 34 Powerpacks"
        p2_load = "3.1 GW"
        p2_mix = "HYDRO + FUSION"
        p2_stat = "NOMINAL"

        p3_name = "BRAZILIA PROVINCE"
        p3_tz = "UTC-3 · ATLANTIC"
        p3_desc = "São Paulo Fusion · Recife Port · 38 Powerpacks"
        p3_load = "4.9 GW"
        p3_mix = "FUSION + HYDRO"
        p3_stat = "NOMINAL"

        badge_l1 = "D-T MAGNETIC CONFINEMENT (2017)"
        badge_l2 = "PLASMA: 150M °C · HTS FIELD: 18.5 T"
        badge_r1 = "INTELLIGENT NATIONAL GRID"
        badge_r2 = "3 PROVINCES · 2 TIME ZONES · 120 POWERPACKS"
        legend_items = [
            ("D-T Plasma Stream", "plasma"),
            ("HTS Magnetic Flux", "flux"),
            ("±800 kV HVDC Grid Flow", "grid"),
        ]

    # Reactor center
    rcx, rcy = 276.0, 264.0

    defs = f"""    <defs>
        <clipPath id="{clip_id}">
            <rect width="{W}" height="{H}" />
        </clipPath>
        <clipPath id="{clip_id}-plasma-torus">
            <path d="M{n(rcx - 150)},{n(rcy)} A150,72 0 1,0 {n(rcx + 150)},{n(rcy)} A150,72 0 1,0 {n(rcx - 150)},{n(rcy)} Z M{n(rcx - 46)},{n(rcy)} A46,21 0 1,1 {n(rcx + 46)},{n(rcy)} A46,21 0 1,1 {n(rcx - 46)},{n(rcy)} Z" fill-rule="evenodd" />
        </clipPath>
        <style>
            @keyframes fg-pulse {{
                0%, 100% {{ opacity: 0.82; transform: scale(0.985); }}
                50% {{ opacity: 1; transform: scale(1.025); }}
            }}
            @keyframes fg-core-pulse {{
                0%, 100% {{ opacity: 0.78; stroke-width: 14px; }}
                50% {{ opacity: 1; stroke-width: 20px; }}
            }}
            @keyframes fg-beacon {{
                0%, 100% {{ opacity: 0.35; transform: scale(0.85); }}
                50% {{ opacity: 1; transform: scale(1.35); }}
            }}
            @keyframes fg-dash-flow {{
                to {{ stroke-dashoffset: -56; }}
            }}
            @keyframes fg-dash-rev {{
                to {{ stroke-dashoffset: 56; }}
            }}
            @keyframes fg-flux-flow {{
                to {{ stroke-dashoffset: -36; }}
            }}
            @keyframes fg-spin-cw {{
                to {{ transform: rotate(360deg); }}
            }}
            @keyframes fg-spin-ccw {{
                to {{ transform: rotate(-360deg); }}
            }}
            .plasma-pulse {{
                transform-box: fill-box;
                transform-origin: center;
                animation: fg-pulse 3.2s ease-in-out infinite;
            }}
            .core-pulse {{
                animation: fg-core-pulse 2.6s ease-in-out infinite;
            }}
            .beacon {{
                transform-box: fill-box;
                transform-origin: center;
                animation: fg-beacon 2.4s ease-in-out infinite;
            }}
            .particle-ring-cw {{
                stroke-dasharray: 18 10 6 10;
                animation: fg-dash-flow 2.2s linear infinite;
            }}
            .particle-ring-ccw {{
                stroke-dasharray: 12 8 4 8;
                animation: fg-dash-rev 2.8s linear infinite;
            }}
            .rotor-cw {{
                transform-box: fill-box;
                transform-origin: center;
                animation: fg-spin-cw 14s linear infinite;
            }}
            .rotor-ccw {{
                transform-box: fill-box;
                transform-origin: center;
                animation: fg-spin-ccw 10s linear infinite;
            }}
            .flux-line {{
                stroke-dasharray: 9 6;
                animation: fg-flux-flow 2.4s linear infinite;
            }}
            .grid-flow {{
                stroke-dasharray: 10 6;
                animation: fg-dash-flow 1.8s linear infinite;
            }}
            .grid-flow-fast {{
                stroke-dasharray: 7 7;
                animation: fg-dash-flow 1.2s linear infinite;
            }}
            @media (prefers-reduced-motion: reduce) {{
                .plasma-pulse, .core-pulse, .beacon, .particle-ring-cw, .particle-ring-ccw,
                .rotor-cw, .rotor-ccw, .flux-line, .grid-flow, .grid-flow-fast {{
                    animation: none !important;
                }}
            }}
            text {{
                font-family: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
        </style>
        <linearGradient id="fg-bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#030d17" />
            <stop offset="45%" stop-color="#06192b" />
            <stop offset="100%" stop-color="#030f1a" />
        </linearGradient>
        <radialGradient id="fg-reactor-ambience" cx="24%" cy="52%" r="36%">
            <stop offset="0%" stop-color="#ff7b29" stop-opacity="0.28" />
            <stop offset="42%" stop-color="#a855f7" stop-opacity="0.14" />
            <stop offset="75%" stop-color="#0284c7" stop-opacity="0.08" />
            <stop offset="100%" stop-color="#030d17" stop-opacity="0" />
        </radialGradient>
        <radialGradient id="fg-grid-ambience" cx="76%" cy="50%" r="38%">
            <stop offset="0%" stop-color="#0284c7" stop-opacity="0.20" />
            <stop offset="55%" stop-color="#0f3d5e" stop-opacity="0.10" />
            <stop offset="100%" stop-color="#030d17" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="fg-cryostat-shell" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#2c4c66" />
            <stop offset="40%" stop-color="#173147" />
            <stop offset="80%" stop-color="#0b1d2c" />
            <stop offset="100%" stop-color="#06111b" />
        </linearGradient>
        <linearGradient id="fg-blanket-metal" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#487294" />
            <stop offset="50%" stop-color="#23425c" />
            <stop offset="100%" stop-color="#0e2233" />
        </linearGradient>
        <linearGradient id="fg-hts-coil" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffe299" />
            <stop offset="35%" stop-color="#e5a93c" />
            <stop offset="75%" stop-color="#9e6916" />
            <stop offset="100%" stop-color="#593808" />
        </linearGradient>
        <linearGradient id="fg-plasma-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#ec4899" />
            <stop offset="22%" stop-color="#ff6a00" />
            <stop offset="50%" stop-color="#fff3b0" />
            <stop offset="78%" stop-color="#ff6a00" />
            <stop offset="100%" stop-color="#a855f7" />
        </linearGradient>
        <radialGradient id="fg-d-section-plasma" cx="50%" cy="50%" r="52%">
            <stop offset="0%" stop-color="#ffffff" />
            <stop offset="32%" stop-color="#fde047" />
            <stop offset="65%" stop-color="#f97316" />
            <stop offset="90%" stop-color="#c026d3" stop-opacity="0.85" />
            <stop offset="100%" stop-color="#7e22ce" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="fg-solenoid-cyl" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#173752" />
            <stop offset="35%" stop-color="#5ca4d6" />
            <stop offset="60%" stop-color="#cdeaff" />
            <stop offset="85%" stop-color="#2a5c85" />
            <stop offset="100%" stop-color="#0d2236" />
        </linearGradient>
        <linearGradient id="fg-flux-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.95" />
            <stop offset="50%" stop-color="#bae6fd" stop-opacity="1" />
            <stop offset="100%" stop-color="#0284c7" stop-opacity="0.85" />
        </linearGradient>
        <linearGradient id="fg-card-bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#082135" stop-opacity="0.95" />
            <stop offset="100%" stop-color="#041320" stop-opacity="0.95" />
        </linearGradient>
        <filter id="fg-glow" x="-25%" y="-25%" width="150%" height="150%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <filter id="fg-soft-glow" x="-35%" y="-35%" width="170%" height="170%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>"""

    body: list[str] = []

    # 1. Background & Ambient Glows
    body.append(f'<rect width="{W}" height="{H}" fill="url(#fg-bg)" />')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#fg-reactor-ambience)" />')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#fg-grid-ambience)" />')

    # 2. Engineering Blueprint Coordinate Grid
    grid_lines = []
    for x in range(40, W, 40):
        grid_lines.append(f"M{x},0 V{H}")
    for y in range(40, H, 40):
        grid_lines.append(f"M0,{y} H{W}")
    body.append(
        f'<path d="{" ".join(grid_lines)}" stroke="#6BA4D9" stroke-width="0.6" opacity="0.09" />'
    )
    # Polar target rings around Tokamak center
    body.append(f"""    <g stroke="#6BA4D9" stroke-width="0.7" fill="none" opacity="0.16">
        <circle cx="{n(rcx)}" cy="{n(rcy)}" r="210" stroke-dasharray="3 6" />
        <circle cx="{n(rcx)}" cy="{n(rcy)}" r="172" />
        <line x1="{n(rcx - 222)}" y1="{n(rcy)}" x2="{n(rcx + 222)}" y2="{n(rcy)}" stroke-dasharray="4 4" />
        <line x1="{n(rcx)}" y1="{n(rcy - 190)}" x2="{n(rcx)}" y2="{n(rcy + 180)}" stroke-dasharray="4 4" />
    </g>""")

    # Zone Headers (y=72)
    body.append(f"""    <!-- Zone Headers -->
    <g font-size="9.5" font-weight="800" letter-spacing="1.1">
        <text x="28" y="72" fill="{GOLD}">{zone1_hdr}</text>
        <line x1="28" y1="78" x2="532" y2="78" stroke="{GOLD}" stroke-width="0.8" opacity="0.4" />
        <text x="580" y="72" fill="{CYAN}">{zone2_hdr}</text>
        <line x1="580" y1="78" x2="1132" y2="78" stroke="{CYAN}" stroke-width="0.8" opacity="0.4" />
    </g>""")

    # ==========================================================================
    # 3. LEFT ZONE: TOKAMAK / STELLARATOR CUTAWAY CHAMBER & CRYOSTAT
    # ==========================================================================
    tokamak: list[str] = []

    # 3a. Cryostat Lower Pedestal, Sub-Reactor Cryo-Manifolds & Divertor Exhaust
    tokamak.append(f"""    <!-- Cryostat Base Pedestal & Divertor Sub-Assembly -->
    <g>
        <polygon points="{n(rcx - 160)},428 {n(rcx - 136)},378 {n(rcx + 136)},378 {n(rcx + 160)},428" fill="#071826" stroke="#2c5370" stroke-width="1.4" />
        <rect x="{n(rcx - 178)}" y="424" width="356" height="10" rx="3" fill="#122c42" stroke="#3c6e91" stroke-width="1.2" />
        <!-- Support struts -->
        <g stroke="#3c6e91" stroke-width="2.5">
            <line x1="{n(rcx - 116)}" y1="382" x2="{n(rcx - 130)}" y2="424" />
            <line x1="{n(rcx - 62)}" y1="388" x2="{n(rcx - 68)}" y2="424" />
            <line x1="{n(rcx + 62)}" y1="388" x2="{n(rcx + 68)}" y2="424" />
            <line x1="{n(rcx + 116)}" y1="382" x2="{n(rcx + 130)}" y2="424" />
        </g>
        <!-- Cryo-cooling He-4 pipes (20 K) -->
        <path d="M{n(rcx - 94)},406 H{n(rcx + 94)}" stroke="{CYAN}" stroke-width="2" stroke-dasharray="6 4" class="flux-line" opacity="0.8" />
    </g>""")

    # 3b. Outer Cryostat Vacuum Vessel & Lithium Breeding Blanket (Rear Cutaway Shell)
    tokamak.append(f"""    <!-- Outer Cryostat Vessel & Lithium Breeding Blanket -->
    <g>
        <!-- Outer cryostat shell -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="198" ry="124" fill="url(#fg-cryostat-shell)" stroke="#4c7ea3" stroke-width="2" />
        <!-- Cryostat structural ribs -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="188" ry="116" fill="none" stroke="#294d69" stroke-width="2" stroke-dasharray="10 8" />
        <!-- Thermal cryo-shield (20 K) -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="178" ry="108" fill="#071724" stroke="{CYAN}" stroke-width="1.2" stroke-opacity="0.65" />
        <!-- Lithium-6 Tritium Breeding Blanket -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="165" ry="96" fill="url(#fg-blanket-metal)" stroke="#6ba4d9" stroke-width="1.5" />
        <!-- Inner vacuum chamber dark background -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="152" ry="82" fill="#040b14" stroke="#3b698c" stroke-width="1.2" />
    </g>""")

    # 3c. Neutral Beam Injector (NBI) Port on Left Side (x=24..86)
    tokamak.append(f"""    <!-- Neutral Beam Injector (NBI) Port -->
    <g>
        <polygon points="30,{n(rcy - 22)} 86,{n(rcy - 16)} 86,{n(rcy + 16)} 30,{n(rcy + 22)}" fill="url(#fg-blanket-metal)" stroke="#5c93ba" stroke-width="1.4" />
        <rect x="22" y="{n(rcy - 16)}" width="12" height="32" rx="2" fill="#18364f" stroke="{GOLD}" stroke-width="1.2" />
        <!-- High-energy Deuterium neutral beam injection stream -->
        <line x1="34" y1="{n(rcy)}" x2="140" y2="{n(rcy)}" stroke="{CYAN}" stroke-width="4" opacity="0.35" filter="url(#fg-glow)" />
        <line x1="34" y1="{n(rcy)}" x2="140" y2="{n(rcy)}" stroke="#e0f2fe" stroke-width="1.8" stroke-dasharray="6 4" class="grid-flow-fast" />
        <g>
            <rect x="16" y="{n(rcy - 47)}" width="82" height="24" rx="5" fill="{INK}" stroke="#3c6e91" stroke-width="0.9" opacity="0.94" />
            <text x="57" y="{n(rcy - 36)}" fill="{CYAN}" font-size="7.0" font-weight="800" text-anchor="middle" letter-spacing="0.3">{lbl_nbi}</text>
            <text x="57" y="{n(rcy - 26.5)}" fill="{MUTED}" font-size="6.5" font-weight="700" text-anchor="middle">{lbl_nbi_sub}</text>
        </g>
    </g>""")

    # 3d. Rear Toroidal Field (TF) Superconducting Coils (Upper Arching Ribs)
    rear_coils = []
    for angle_deg in (-68, -42, -18, 18, 42, 68):
        rad = math.radians(angle_deg)
        x_outer = rcx + 164 * math.sin(rad)
        y_outer = rcy - 96 * math.cos(rad)
        x_inner = rcx + 26 * math.sin(rad)
        y_inner = rcy - 52 * math.cos(rad)
        ctrl_x = rcx + 112 * math.sin(rad)
        ctrl_y = rcy - 120 * math.cos(rad)
        rear_coils.append(
            f'<path d="M{n(x_inner)},{n(y_inner)} Q{n(ctrl_x)},{n(ctrl_y)} {n(x_outer)},{n(y_outer)}" '
            f'fill="none" stroke="url(#fg-hts-coil)" stroke-width="6.5" stroke-linecap="round" opacity="0.82" />'
        )
        rear_coils.append(
            f'<path d="M{n(x_inner)},{n(y_inner)} Q{n(ctrl_x)},{n(ctrl_y)} {n(x_outer)},{n(y_outer)}" '
            f'fill="none" stroke="{CYAN}" stroke-width="1.3" stroke-dasharray="5 4" class="flux-line" opacity="0.7" />'
        )
    tokamak.append("    <!-- Rear Toroidal Field (TF) HTS Coils -->\n    <g>\n        " + "\n        ".join(rear_coils) + "\n    </g>")

    # 3e. Poloidal Field (PF) Outer Ring Coils (Back Half)
    tokamak.append(f"""    <!-- Poloidal Field (PF) Outer Coils (Rear Arcs) -->
    <g fill="none">
        <path d="M{n(rcx - 182)},{n(rcy - 52)} A182,46 0 0,1 {n(rcx + 182)},{n(rcy - 52)}" stroke="#3b76a3" stroke-width="5" opacity="0.75" />
        <path d="M{n(rcx - 192)},{n(rcy)} A192,54 0 0,1 {n(rcx + 192)},{n(rcy)}" stroke="#3b76a3" stroke-width="5.5" opacity="0.75" />
        <path d="M{n(rcx - 182)},{n(rcy + 52)} A182,46 0 0,1 {n(rcx + 182)},{n(rcy + 52)}" stroke="#3b76a3" stroke-width="5" opacity="0.75" />
    </g>""")

    # 3f. Glowing Deuterium-Tritium (D-T) Plasma Vortex & Rotating Particle Rings
    helical_lines = []
    num_twists = 12
    for i in range(num_twists):
        a0 = i * 360.0 / num_twists
        a1 = a0 + 110.0
        r0_x, r0_y = 144.0, 68.0
        r1_x, r1_y = 52.0, 24.0
        x0 = rcx + r0_x * math.cos(math.radians(a0))
        y0 = rcy + r0_y * math.sin(math.radians(a0))
        x1 = rcx + r1_x * math.cos(math.radians(a1))
        y1 = rcy + r1_y * math.sin(math.radians(a1))
        xm = rcx + 98.0 * math.cos(math.radians((a0 + a1) * 0.5))
        ym = rcy + 46.0 * math.sin(math.radians((a0 + a1) * 0.5))
        helical_lines.append(
            f'<path d="M{n(x0)},{n(y0)} Q{n(xm)},{n(ym)} {n(x1)},{n(y1)}" '
            f'fill="none" stroke="#fde047" stroke-width="1.6" stroke-dasharray="7 5" class="particle-ring-cw" opacity="0.65" />'
        )

    tokamak.append(f"""    <!-- Glowing Deuterium-Tritium (D-T) Plasma Torus Vortex -->
    <g class="plasma-pulse">
        <!-- Outer magenta-orange plasma mantle -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="112" ry="50" fill="none" stroke="#c026d3" stroke-width="44" opacity="0.32" filter="url(#fg-soft-glow)" />
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="104" ry="46" fill="none" stroke="url(#fg-plasma-grad)" stroke-width="32" opacity="0.78" filter="url(#fg-glow)" />
        <!-- Ignited 150M °C core plasma ring -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="100" ry="44" fill="none" stroke="#ffae34" stroke-width="17" class="core-pulse" filter="url(#fg-glow)" />
        <ellipse cx="{n(rcx)}" cy="{n(rcy)}" rx="100" ry="44" fill="none" stroke="#ffffff" stroke-width="6" opacity="0.95" />
    </g>
    <!-- Helical Magnetic Twist Filaments & Rotating Particle Rings -->
    <g clip-path="url(#{clip_id}-plasma-torus)">
        {"".join(helical_lines)}
    </g>
    <g fill="none">
        <!-- Rotating Particle Ring 1 (Outer Fast Deuterium Stream) -->
        <ellipse id="fg-orbit-1-{lang}" cx="{n(rcx)}" cy="{n(rcy)}" rx="120" ry="54" stroke="#fde047" stroke-width="2" class="particle-ring-cw" opacity="0.9" />
        <!-- Rotating Particle Ring 2 (Counter-Rotating Tritium Stream) -->
        <ellipse id="fg-orbit-2-{lang}" cx="{n(rcx)}" cy="{n(rcy)}" rx="85" ry="37" stroke="#38bdf8" stroke-width="1.8" class="particle-ring-ccw" opacity="0.9" />
        <!-- Rotating Particle Ring 3 (Core Alpha Heating Stream) -->
        <ellipse id="fg-orbit-3-{lang}" cx="{n(rcx)}" cy="{n(rcy)}" rx="102" ry="45" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="10 14" class="particle-ring-cw" opacity="0.85" />
    </g>
    <!-- Orbiting High-Energy Fusion Ions (SMIL animateMotion) -->
    <g filter="url(#fg-glow)">
        <circle r="4" fill="#ffffff" stroke="#f97316" stroke-width="1.5">
            <animateMotion dur="3.4s" repeatCount="indefinite">
                <mpath href="#fg-orbit-1-{lang}" />
            </animateMotion>
        </circle>
        <circle r="3.5" fill="#fde047">
            <animateMotion dur="3.4s" begin="-1.7s" repeatCount="indefinite">
                <mpath href="#fg-orbit-1-{lang}" />
            </animateMotion>
        </circle>
        <circle r="3.5" fill="#38bdf8" stroke="#ffffff" stroke-width="1">
            <animateMotion dur="2.8s" repeatCount="indefinite">
                <mpath href="#fg-orbit-2-{lang}" />
            </animateMotion>
        </circle>
        <circle r="3" fill="#e0f2fe">
            <animateMotion dur="2.8s" begin="-1.4s" repeatCount="indefinite">
                <mpath href="#fg-orbit-2-{lang}" />
            </animateMotion>
        </circle>
        <circle r="4.2" fill="#fffbeb" stroke="#ec4899" stroke-width="1.4">
            <animateMotion dur="2.2s" repeatCount="indefinite">
                <mpath href="#fg-orbit-3-{lang}" />
            </animateMotion>
        </circle>
    </g>""")

    # 3g. Cutaway Cross-Sections (Left & Right D-Shaped Plasma & Blanket Cutaways)
    for side, label_tag in ((-1, "L"), (1, "R")):
        dcx = rcx + side * 100.0
        dcy = rcy
        frame_d = d_coil_path(rcx, dcy, 60, 142, 52, side)
        vessel_d = d_coil_path(rcx, dcy, 66, 134, 44, side)
        plasma_d1 = d_coil_path(rcx, dcy, 72, 128, 36, side)
        plasma_d2 = d_coil_path(rcx, dcy, 80, 118, 25, side)
        plasma_d3 = d_coil_path(rcx, dcy, 88, 110, 13, side)
        div_x = rcx + side * 93.0
        tokamak.append(f"""    <!-- Cutaway Torus Cross-Section ({label_tag}) -->
    <g>
        <path d="{frame_d}" fill="#0f293d" stroke="#75b0db" stroke-width="2" />
        <path d="{vessel_d}" fill="#06131f" stroke="{GOLD}" stroke-width="1.3" />
        <!-- Glowing D-Shaped Plasma Cross-Section -->
        <path d="{plasma_d1}" fill="url(#fg-d-section-plasma)" class="plasma-pulse" filter="url(#fg-glow)" />
        <!-- Nested Magnetic Flux Surfaces -->
        <path d="{plasma_d1}" fill="none" stroke="#f97316" stroke-width="1.4" stroke-dasharray="4 3" class="flux-line" />
        <path d="{plasma_d2}" fill="none" stroke="#fde047" stroke-width="1.3" stroke-dasharray="3 3" class="flux-line" />
        <path d="{plasma_d3}" fill="#ffffff" stroke="#ffffff" stroke-width="1.5" />
        <!-- Rotating Particle Vortex Indicator inside D-Section -->
        <g transform="translate({n(dcx)}, {n(dcy)})">
            <circle r="15" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-dasharray="5 4" class="rotor-cw" opacity="0.85" />
            <circle r="8.5" fill="none" stroke="{CYAN}" stroke-width="1.1" stroke-dasharray="3 3" class="rotor-ccw" opacity="0.9" />
            <circle r="2.8" fill="#ffffff" />
        </g>
        <!-- Tungsten Divertor Cassette & X-Point Strike Plume at bottom of D-Section -->
        <path d="M{n(div_x - 15)},{n(dcy + 44)} L{n(div_x - 9)},{n(dcy + 56)} L{n(div_x + 9)},{n(dcy + 56)} L{n(div_x + 15)},{n(dcy + 44)} Z" fill="#1e3f5a" stroke="{GOLD}" stroke-width="1.2" />
        <path d="M{n(div_x)},{n(dcy + 34)} L{n(div_x - 8)},{n(dcy + 53)} M{n(div_x)},{n(dcy + 34)} L{n(div_x + 8)},{n(dcy + 53)}" stroke="#ff9233" stroke-width="2" stroke-linecap="round" opacity="0.9" />
    </g>""")

    # 3h. Central Solenoid (CS) Superconducting Induction Column (Center of Torus)
    tokamak.append(f"""    <!-- Central Solenoid (CS) Superconducting Column -->
    <g>
        <rect x="{n(rcx - 23)}" y="{n(rcy - 74)}" width="46" height="148" rx="6" fill="url(#fg-solenoid-cyl)" stroke="#8fd3ff" stroke-width="1.8" />
        <!-- Stacked REBCO Solenoid Pancake Windings -->
        <g stroke="#06192b" stroke-width="1.6">
            <line x1="{n(rcx - 23)}" y1="{n(rcy - 54)}" x2="{n(rcx + 23)}" y2="{n(rcy - 54)}" />
            <line x1="{n(rcx - 23)}" y1="{n(rcy - 36)}" x2="{n(rcx + 23)}" y2="{n(rcy - 36)}" />
            <line x1="{n(rcx - 23)}" y1="{n(rcy - 18)}" x2="{n(rcx + 23)}" y2="{n(rcy - 18)}" />
            <line x1="{n(rcx - 23)}" y1="{n(rcy)}" x2="{n(rcx + 23)}" y2="{n(rcy)}" />
            <line x1="{n(rcx - 23)}" y1="{n(rcy + 18)}" x2="{n(rcx + 23)}" y2="{n(rcy + 18)}" />
            <line x1="{n(rcx - 23)}" y1="{n(rcy + 36)}" x2="{n(rcx + 23)}" y2="{n(rcy + 36)}" />
            <line x1="{n(rcx - 23)}" y1="{n(rcy + 54)}" x2="{n(rcx + 23)}" y2="{n(rcy + 54)}" />
        </g>
        <!-- Glowing superconducting induction rings on Central Solenoid -->
        <g stroke="{CYAN}" stroke-width="1.6" stroke-dasharray="5 3" class="flux-line">
            <line x1="{n(rcx - 25)}" y1="{n(rcy - 45)}" x2="{n(rcx + 25)}" y2="{n(rcy - 45)}" />
            <line x1="{n(rcx - 25)}" y1="{n(rcy - 9)}" x2="{n(rcx + 25)}" y2="{n(rcy - 9)}" />
            <line x1="{n(rcx - 25)}" y1="{n(rcy + 27)}" x2="{n(rcx + 25)}" y2="{n(rcy + 27)}" />
        </g>
        <!-- Solenoid Top Dome & Cryo Busbar -->
        <ellipse cx="{n(rcx)}" cy="{n(rcy - 74)}" rx="23" ry="8" fill="#5ca4d6" stroke="#cdeaff" stroke-width="1.4" />
        <ellipse cx="{n(rcx)}" cy="{n(rcy + 74)}" rx="23" ry="8" fill="#173752" stroke="#5ca4d6" stroke-width="1.4" />
    </g>""")

    # 3i. Front Cutaway Toroidal Field (TF) Coils & Glowing Magnetic Flux Lines
    left_tf_outer = d_coil_path(rcx, rcy, 23, 155, 72, -1)
    left_tf_inner = d_coil_path(rcx, rcy, 29, 143, 62, -1)
    right_tf_outer = d_coil_path(rcx, rcy, 23, 155, 72, 1)
    right_tf_inner = d_coil_path(rcx, rcy, 29, 143, 62, 1)

    tokamak.append(f"""    <!-- Front Cutaway REBCO Superconducting TF Coils & Glowing Flux Lines -->
    <g>
        <!-- Left Master TF Coil Casing -->
        <path d="{left_tf_outer}" fill="none" stroke="url(#fg-hts-coil)" stroke-width="7.5" stroke-linejoin="round" />
        <path d="{left_tf_inner}" fill="none" stroke="#081b2b" stroke-width="3" />
        <!-- Right Master TF Coil Casing -->
        <path d="{right_tf_outer}" fill="none" stroke="url(#fg-hts-coil)" stroke-width="7.5" stroke-linejoin="round" />
        <path d="{right_tf_inner}" fill="none" stroke="#081b2b" stroke-width="3" />
        <!-- Glowing HTS Magnetic Flux Lines Looping Through Coils -->
        <path d="{left_tf_outer}" fill="none" stroke="url(#fg-flux-grad)" stroke-width="2" class="flux-line" filter="url(#fg-glow)" />
        <path d="{right_tf_outer}" fill="none" stroke="url(#fg-flux-grad)" stroke-width="2" class="flux-line" filter="url(#fg-glow)" />
        <!-- Outer Poloidal Magnetic Dipole Flux Field Loops -->
        <path d="M{n(rcx)},{n(rcy - 82)} C{n(rcx - 228)},{n(rcy - 142)} {n(rcx - 228)},{n(rcy + 142)} {n(rcx)},{n(rcy + 82)}" fill="none" stroke="{CYAN}" stroke-width="1.5" class="flux-line" opacity="0.72" />
        <path d="M{n(rcx)},{n(rcy - 82)} C{n(rcx + 228)},{n(rcy - 142)} {n(rcx + 228)},{n(rcy + 142)} {n(rcx)},{n(rcy + 82)}" fill="none" stroke="{CYAN}" stroke-width="1.5" class="flux-line" opacity="0.72" />
        <!-- Front Poloidal Coil Cutaway Segments (Left & Right Flanks) -->
        <path d="M{n(rcx - 190)},{n(rcy - 12)} A190,54 0 0,0 {n(rcx - 128)},{n(rcy + 40)}" fill="none" stroke="#5ca4d6" stroke-width="6" stroke-linecap="round" />
        <path d="M{n(rcx + 190)},{n(rcy - 12)} A190,54 0 0,1 {n(rcx + 128)},{n(rcy + 40)}" fill="none" stroke="#5ca4d6" stroke-width="6" stroke-linecap="round" />
        <!-- Cutaway Bolt Flanges on Poloidal Rings -->
        <circle cx="{n(rcx - 128)}" cy="{n(rcy + 40)}" r="4.5" fill="{GOLD}" stroke="{INK}" stroke-width="1" />
        <circle cx="{n(rcx + 128)}" cy="{n(rcy + 40)}" r="4.5" fill="{GOLD}" stroke="{INK}" stroke-width="1" />
    </g>""")

    # 3j. Callout Labels Around Tokamak Chamber
    tokamak.append(f"""    <!-- Engineering Callout Labels for Reactor Chamber -->
    <g font-size="8.2" font-weight="800" letter-spacing="0.5">
        <!-- Top-Left Callout: HTS Magnet Coils -->
        <g>
            <line x1="{n(rcx - 92)}" y1="{n(rcy - 66)}" x2="132" y2="115" stroke="{GOLD}" stroke-width="1.1" />
            <circle cx="{n(rcx - 92)}" cy="{n(rcy - 66)}" r="3" fill="{GOLD}" />
            <rect x="24" y="90" width="216" height="34" rx="6" fill="{INK}" stroke="{GOLD}" stroke-width="1" opacity="0.94" />
            <text x="36" y="105" fill="{GOLD}">{lbl_hts_coil}</text>
            <text x="36" y="118" fill="{MUTED}" font-size="7.2" font-weight="600">{lbl_hts_sub}</text>
        </g>

        <!-- Top-Center Callout: Central Solenoid -->
        <g>
            <line x1="{n(rcx)}" y1="{n(rcy - 76)}" x2="355" y2="115" stroke="{CYAN}" stroke-width="1.1" />
            <circle cx="{n(rcx)}" cy="{n(rcy - 76)}" r="3" fill="{CYAN}" />
            <rect x="326" y="90" width="186" height="34" rx="6" fill="{INK}" stroke="{CYAN}" stroke-width="1" opacity="0.94" />
            <text x="338" y="105" fill="{CYAN}">{lbl_solenoid}</text>
            <text x="338" y="118" fill="{MUTED}" font-size="7.2" font-weight="600">{lbl_solenoid_sub}</text>
        </g>

        <!-- Bottom-Left Callout: Lithium Blanket & Cryostat -->
        <g>
            <line x1="{n(rcx - 144)}" y1="{n(rcy + 60)}" x2="120" y2="394" stroke="#6BA4D9" stroke-width="1.1" />
            <circle cx="{n(rcx - 144)}" cy="{n(rcy + 60)}" r="3" fill="#6BA4D9" />
            <rect x="24" y="386" width="234" height="34" rx="6" fill="{INK}" stroke="#6BA4D9" stroke-width="1" opacity="0.94" />
            <text x="36" y="401" fill="#e0f2fe">{lbl_blanket}</text>
            <text x="36" y="414" fill="{MUTED}" font-size="7.2" font-weight="600">{lbl_blanket_sub}</text>
        </g>

        <!-- Center-Bottom Callout: D-T Plasma Vortex -->
        <g>
            <line x1="{n(rcx)}" y1="{n(rcy + 44)}" x2="412" y2="394" stroke="{ORANGE}" stroke-width="1.2" />
            <circle cx="{n(rcx)}" cy="{n(rcy + 44)}" r="3.2" fill="{ORANGE}" />
            <rect x="300" y="386" width="224" height="34" rx="6" fill="{INK}" stroke="{ORANGE}" stroke-width="1.1" opacity="0.95" />
            <text x="312" y="401" fill="#fde047">{lbl_plasma}</text>
            <text x="312" y="414" fill="{MUTED}" font-size="7.2" font-weight="600">{lbl_plasma_sub}</text>
        </g>
    </g>""")

    body.extend(tokamak)

    # ==========================================================================
    # 4. THERMAL-TO-HVDC CONVERTER BRIDGE (x = 468 .. 580)
    # ==========================================================================
    body.append(f"""    <!-- Thermal Blanket to ±800 kV HVDC Converter Coupling -->
    <g>
        <!-- Primary superheated helium/lithium thermal transfer ducts -->
        <path d="M466,{n(rcy - 18)} H538" stroke="{ORANGE}" stroke-width="5" opacity="0.32" filter="url(#fg-glow)" />
        <path d="M466,{n(rcy + 18)} H538" stroke="{CYAN}" stroke-width="5" opacity="0.32" filter="url(#fg-glow)" />
        <path d="M466,{n(rcy - 18)} H538" stroke="#fde047" stroke-width="2.2" stroke-dasharray="8 5" class="grid-flow-fast" />
        <path d="M466,{n(rcy + 18)} H538" stroke="{CYAN}" stroke-width="2.2" stroke-dasharray="8 5" class="grid-flow" />

        <!-- HVDC Converter & Transformer Hub Node (cx=538, cy=264) -->
        <rect x="490" y="{n(rcy - 38)}" width="96" height="76" rx="10" fill="url(#fg-card-bg)" stroke="{GOLD}" stroke-width="1.6" />
        <!-- Transformer coils symbol -->
        <circle cx="528" cy="{n(rcy - 8)}" r="11" fill="none" stroke="{GOLD}" stroke-width="1.8" />
        <circle cx="548" cy="{n(rcy - 8)}" r="11" fill="none" stroke="{CYAN}" stroke-width="1.8" />
        <line x1="538" y1="{n(rcy - 22)}" x2="538" y2="{n(rcy + 6)}" stroke="#ffffff" stroke-width="1.4" />
        <text x="538" y="{n(rcy + 19)}" fill="{GOLD}" font-size="6.8" font-weight="800" text-anchor="middle" letter-spacing="0.4">{lbl_hvdc_hub}</text>
        <text x="538" y="{n(rcy + 29.5)}" fill="{CYAN}" font-size="6.7" font-weight="800" text-anchor="middle" letter-spacing="0.5">{lbl_hvdc_sub}</text>
    </g>""")

    # ==========================================================================
    # 5. CENTER-RIGHT ZONE: LIVE TELEMETRY GAUGES (x = 596 .. 834, width = 238)
    # ==========================================================================
    gauges = [
        (92, g1_title, g1_val, g1_sub1, g1_sub2, g1_pill, ORANGE, "#fde047", 0.27),
        (206, g2_title, g2_val, g2_sub1, g2_sub2, g2_pill, GREEN, "#86efac", 0.91),
        (320, g3_title, g3_val, g3_sub1, g3_sub2, g3_pill, CYAN, "#bae6fd", 0.86),
    ]

    gauge_els: list[str] = []
    # Main vertical HVDC busbar linking the converter hub to the 3 telemetry gauges
    gauge_els.append(f"""    <!-- HVDC Primary Dispatch Busbar -->
    <g fill="none">
        <path d="M586,{n(rcy)} H588 V142 H596 M588,256 H596 M588,{n(rcy)} V370 H596" stroke="{GOLD}" stroke-width="2.2" />
        <path d="M586,{n(rcy)} H588 V142 H596 M588,256 H596 M588,{n(rcy)} V370 H596" stroke="#ffffff" stroke-width="1.4" class="grid-flow-fast" />
    </g>""")

    for gy, title, val, sub1, sub2, pill, col, hi_col, frac in gauges:
        gcx = 632.0
        gcy = gy + 50.0
        gr = 28.5
        track_d = arc_path(gcx, gcy, gr, 135, 405)
        fill_angle = 135 + 270 * frac
        val_d = arc_path(gcx, gcy, gr, 135, fill_angle)
        tip_x, tip_y = polar(gcx, gcy, gr, fill_angle)

        gauge_els.append(f"""    <!-- Telemetry Gauge Card: {title} -->
    <g>
        <rect x="596" y="{gy}" width="238" height="100" rx="10" fill="url(#fg-card-bg)" stroke="{col}" stroke-width="1.3" stroke-opacity="0.8" />
        <!-- Circular Arc Telemetry Gauge -->
        <path d="{track_d}" fill="none" stroke="#122d42" stroke-width="6.5" stroke-linecap="round" />
        <path d="{val_d}" fill="none" stroke="{col}" stroke-width="6.5" stroke-linecap="round" filter="url(#fg-glow)" />
        <circle cx="{n(tip_x)}" cy="{n(tip_y)}" r="3.5" fill="#ffffff" class="beacon" />
        <circle cx="{n(gcx)}" cy="{n(gcy)}" r="20" fill="#04101a" stroke="#1e3f5a" stroke-width="1" />
        <text x="{n(gcx)}" y="{n(gcy + 4)}" fill="{hi_col}" font-size="12" font-weight="800" text-anchor="middle">{val}</text>
        <!-- Telemetry Readout Text -->
        <text x="672" y="{gy + 22}" fill="{hi_col}" font-size="8.5" font-weight="800" letter-spacing="0.5">{title}</text>
        <text x="672" y="{gy + 37.5}" fill="#e2f1fc" font-size="6.8" font-weight="600">{sub1}</text>
        <text x="672" y="{gy + 50}" fill="{MUTED}" font-size="6.7" font-weight="600">{sub2}</text>
        <!-- Status Pill -->
        <rect x="670" y="{gy + 62}" width="154" height="22" rx="11" fill="#04121c" stroke="{col}" stroke-width="1" />
        <circle cx="682" cy="{gy + 73}" r="3" fill="{col}" class="beacon" />
        <text x="753" y="{gy + 76}" fill="{hi_col}" font-size="6.7" font-weight="800" text-anchor="middle" letter-spacing="0.3">{pill}</text>
    </g>""")

    body.extend(gauge_els)

    # ==========================================================================
    # 6. FAR-RIGHT ZONE: LIVE GRID POWER TRANSMISSION TO 3 PROVINCES (x = 832 .. 1132)
    # ==========================================================================
    corridors = [
        ("waikiki", "M834,142 C852,142 862,142 884,142", GOLD, "2.2s"),
        ("amazonia", "M834,256 C852,256 862,256 884,256", GREEN, "2.5s"),
        ("brazilia", "M834,370 C852,370 862,370 884,370", CYAN, "2.0s"),
    ]
    corr_els: list[str] = []
    corr_els.append(f"""    <!-- Inter-Provincial Synchronous Tie-Line (3 Provinces / 2 Time Zones) -->
    <g fill="none">
        <path id="fg-tie-bus-{lang}" d="M858,142 V370" stroke="#3b76a3" stroke-width="4" opacity="0.45" />
        <path d="M858,142 V370" stroke="{CYAN}" stroke-width="1.8" stroke-dasharray="6 5" class="flux-line" />
        <!-- Transmission Substation Nodes along the Tie-Line -->
        <g stroke="{GOLD}" stroke-width="1.2" fill="#061826">
            <circle cx="858" cy="142" r="5" />
            <circle cx="858" cy="256" r="5" />
            <circle cx="858" cy="370" r="5" />
        </g>
        <circle r="3.5" fill="#ffffff" filter="url(#fg-glow)">
            <animateMotion dur="3.6s" repeatCount="indefinite" keyPoints="0;1;0" keyTimes="0;0.5;1" calcMode="linear">
                <mpath href="#fg-tie-bus-{lang}" />
            </animateMotion>
        </circle>
    </g>""")

    for cid, cpath, ccol, cdur in corridors:
        pid = f"fg-corr-{cid}-{lang}"
        corr_els.append(f"""    <!-- Corridor: {cid} -->
    <g>
        <path id="{pid}" d="{cpath}" fill="none" stroke="{ccol}" stroke-width="5" opacity="0.25" filter="url(#fg-glow)" />
        <path d="{cpath}" fill="none" stroke="{ccol}" stroke-width="2.4" class="grid-flow" />
        <circle r="4" fill="#ffffff" stroke="{ccol}" stroke-width="1.5" filter="url(#fg-glow)">
            <animateMotion dur="{cdur}" repeatCount="indefinite">
                <mpath href="#{pid}" />
            </animateMotion>
        </circle>
    </g>""")

    body.extend(corr_els)

    # Three Provincial Distribution Nodes (x = 884 .. 1132, width = 248)
    provinces = [
        (92, p1_name, p1_tz, p1_desc, p1_load, p1_mix, p1_stat, GOLD, "#fde047", 0.82),
        (206, p2_name, p2_tz, p2_desc, p2_load, p2_mix, p2_stat, GREEN, "#86efac", 0.68),
        (320, p3_name, p3_tz, p3_desc, p3_load, p3_mix, p3_stat, CYAN, "#bae6fd", 0.86),
    ]

    prov_els: list[str] = []
    stat_dot_offset = 74 if is_hu else 52
    for py, name, tz, desc, load, mix, stat, col, hi_col, bar_w in provinces:
        fill_px = int(152 * bar_w)
        prov_els.append(f"""    <!-- Provincial Grid Node: {name} -->
    <g>
        <rect x="884" y="{py}" width="248" height="100" rx="10" fill="url(#fg-card-bg)" stroke="{col}" stroke-width="1.5" />
        <!-- Province Header & Time Zone Pill -->
        <text x="898" y="{py + 21}" fill="#ffffff" font-size="8.6" font-weight="800" letter-spacing="0.3">{name}</text>
        <rect x="1024" y="{py + 9}" width="96" height="16" rx="8" fill="#04101a" stroke="#2c5370" stroke-width="0.9" />
        <text x="1072" y="{py + 20}" fill="{hi_col}" font-size="6.1" font-weight="800" text-anchor="middle" letter-spacing="0.2">{tz}</text>
        <!-- Infrastructure Sub-description -->
        <text x="898" y="{py + 37}" fill="{MUTED}" font-size="7.0" font-weight="600">{desc}</text>
        <!-- Live Load Bar -->
        <rect x="898" y="{py + 46}" width="152" height="8" rx="4" fill="#04101a" stroke="#1c3b54" stroke-width="0.8" />
        <rect x="898" y="{py + 46}" width="{fill_px}" height="8" rx="4" fill="{col}" />
        <!-- Animated energy pulse overlay on load bar -->
        <line x1="900" y1="{py + 50}" x2="{898 + fill_px - 2}" y2="{py + 50}" stroke="#ffffff" stroke-width="2" stroke-dasharray="6 8" class="grid-flow-fast" opacity="0.65" />
        <text x="1118" y="{py + 54}" fill="{hi_col}" font-size="11" font-weight="800" text-anchor="end">{load}</text>
        <!-- Bottom Telemetry Row -->
        <text x="898" y="{py + 76}" fill="#e2f1fc" font-size="7.2" font-weight="800" letter-spacing="0.3">{mix}</text>
        <circle cx="{1118 - stat_dot_offset}" cy="{py + 73}" r="3.2" fill="{GREEN}" class="beacon" />
        <text x="1118" y="{py + 76}" fill="{GREEN}" font-size="7.2" font-weight="800" text-anchor="end" letter-spacing="0.4">{stat}</text>
        <!-- Mini Live Waveform Sine Curve -->
        <path d="M898,{py + 88} Q910,{py + 82} 922,{py + 88} T946,{py + 88} T970,{py + 88} T994,{py + 88} T1018,{py + 88} T1042,{py + 88} T1066,{py + 88} T1090,{py + 88} T1118,{py + 88}" fill="none" stroke="{col}" stroke-width="1.1" opacity="0.65" />
    </g>""")

    body.extend(prov_els)

    # ==========================================================================
    # 7. TOP & BOTTOM HUD OVERLAYS (Consistent with station & missile-defense SVGs)
    # ==========================================================================
    status_dot_x = 768 if is_hu else 752
    body.append(f"""    <!-- TOP HUD STATUS BAR -->
    <g font-size="10.2" font-weight="800" letter-spacing="1.0">
        <rect x="176" y="16" width="808" height="32" rx="16" fill="{INK}" stroke="{GOLD}" stroke-width="1.2" opacity="0.95" />
        <text x="200" y="36.5" fill="#fbf7f0">{hud_title}</text>
        <circle cx="{n(status_dot_x)}" cy="32" r="4" fill="{GREEN}" class="beacon" />
        <circle cx="{n(status_dot_x)}" cy="32" r="2.8" fill="{GREEN}" />
        <text x="960" y="36.5" fill="{GREEN}" text-anchor="end">{hud_status}</text>
    </g>""")

    # Bottom Center Legend Pill
    legend_x0 = 355
    lx = legend_x0
    legend_els = []
    for text, kind in legend_items:
        if kind == "plasma":
            legend_els.append(
                f'<line x1="{lx}" y1="{H - 37}" x2="{lx + 22}" y2="{H - 37}" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round" />'
                f'<circle cx="{lx + 11}" cy="{H - 37}" r="2.5" fill="#fde047" />'
            )
        elif kind == "flux":
            legend_els.append(
                f'<line x1="{lx}" y1="{H - 37}" x2="{lx + 22}" y2="{H - 37}" stroke="{CYAN}" stroke-width="2" stroke-dasharray="5 3" class="flux-line" />'
            )
        else:
            legend_els.append(
                f'<line x1="{lx}" y1="{H - 37}" x2="{lx + 22}" y2="{H - 37}" stroke="{GOLD}" stroke-width="2.2" stroke-dasharray="6 4" class="grid-flow" />'
            )
        legend_els.append(f'<text x="{lx + 28}" y="{H - 33.5}" fill="#d5e9f7">{text}</text>')
        lx += 28 + len(text) * 6.0 + 22

    legend_w = lx - legend_x0 - 22 + 36
    shift = (W / 2) - (legend_x0 - 18 + legend_w / 2)
    body.append(f"""    <!-- Bottom Legend Pill -->
    <g transform="translate({n(shift)}, 0)" font-size="8.8" font-weight="700" letter-spacing="0.5">
        <rect x="{legend_x0 - 18}" y="{H - 55}" width="{n(legend_w)}" height="36" rx="18" fill="{INK}" stroke="rgba(107, 164, 217, 0.45)" stroke-width="1" opacity="0.95" />
        {"".join(legend_els)}
    </g>""")

    # Bottom-Left & Bottom-Right Corner Telemetry Badges
    body.append(f"""    <!-- Bottom-left corner badge -->
    <g font-size="8.8" font-weight="700" letter-spacing="0.5">
        <rect x="24" y="{H - 68}" width="296" height="48" rx="8" fill="{INK}" stroke="rgba(245, 196, 110, 0.45)" stroke-width="1" opacity="0.95" />
        <text x="38" y="{H - 46}" fill="{GOLD}">{badge_l1}</text>
        <text x="38" y="{H - 31}" fill="#bedbd6" font-size="7.8" letter-spacing="0.4">{badge_l2}</text>
    </g>
    <!-- Bottom-right corner badge -->
    <g font-size="8.8" font-weight="700" letter-spacing="0.5" text-anchor="end">
        <rect x="{W - 320}" y="{H - 68}" width="296" height="48" rx="8" fill="{INK}" stroke="rgba(56, 189, 248, 0.45)" stroke-width="1" opacity="0.95" />
        <text x="{W - 38}" y="{H - 46}" fill="{CYAN}">{badge_r1}</text>
        <text x="{W - 38}" y="{H - 31}" fill="#bedbd6" font-size="7.8" letter-spacing="0.4">{badge_r2}</text>
    </g>""")

    inner = "\n".join(body)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 {W} {H}">
{defs}
    <g clip-path="url(#{clip_id})">
{inner}
    </g>
</svg>"""


def update_infrastructure_energy_section(file_path: Path, lang: str = "en") -> None:
    content = file_path.read_text(encoding="utf-8")

    if lang == "hu":
        alt_text = "Kereskedelmi hidrogénfúziós erőműkomplexum és intelligens nemzeti villamoshálózat"
        cap_main = "A D-T mágneses összetartású fúziós reaktormag metszete és a három tartományt összekötő ±800 kV-os intelligens villamoshálózat."
        cap_sub = "150M °C plazmaörvény · 18,5 T REBCO szupravezető tekercsek · 120 hibrid Powerpack állomás"
    else:
        alt_text = "Commercial Hydrogen Fusion Power Complex and Intelligent National Grid"
        cap_main = "Cutaway of the D-T magnetic confinement fusion core and the ±800 kV intelligent grid balancing supply across all three provinces."
        cap_sub = "150M °C Plasma Vortex · 18.5 T REBCO Superconducting Coils · 120 Hybrid Powerpack Stations"

    img = f'<img class="ill" src="../icons/infrastructure/fusion-grid-{lang}.svg" alt="{alt_text}" width="{W}" height="{H}" />'
    panel = (
        f'<div class="ill-panel">\n{img}\n<div class="ill-caption">\n'
        f"<span>{cap_main}</span>\n<span>{cap_sub}</span>\n</div>\n</div>\n"
    )

    existing = re.compile(
        r'(<section id="energy"[^>]*>.*?<div class="ill-panel">\s*)(?:<svg.*?</svg>|<img[^>]*class="ill"[^>]*>)(\s*<div class="ill-caption">.*?</div>\s*</div>)',
        re.DOTALL,
    )
    if existing.search(content):
        content = existing.sub(
            lambda m: (
                m.group(1)
                + img
                + f'\n<div class="ill-caption">\n<span>{cap_main}</span>\n<span>{cap_sub}</span>\n</div>\n</div>'
            ),
            content,
            count=1,
        )
    else:
        insert = re.compile(
            r'(<section id="energy"[^>]*>.*?<div class="energy-mix">.*?</ul>\s*</div>\s*)(<div class="card-grid">)',
            re.DOTALL,
        )
        if not insert.search(content):
            raise ValueError(f"Could not find #energy section insertion point in {file_path}")
        content = insert.sub(lambda m: m.group(1) + panel + m.group(2), content, count=1)

    sys.path.insert(0, str(ROOT / "scripts"))
    from build_pages import format_and_remove_empty_lines

    formatted = format_and_remove_empty_lines(content)
    file_path.write_text(formatted, encoding="utf-8")
    print(f"Updated and formatted {file_path.relative_to(ROOT)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating Commercial Hydrogen Fusion Power Complex and Intelligent Grid SVGs...")
    for lang in ("en", "hu"):
        svg = build_fusion_grid_svg(lang)
        svg = "\n".join(line for line in svg.splitlines() if line.strip())
        out_file = OUT_DIR / f"fusion-grid-{lang}.svg"
        out_file.write_text(svg + "\n", encoding="utf-8")
        print(f"  Saved {out_file.relative_to(ROOT)} ({len(svg) / 1024:.1f} KB)")

    update_infrastructure_energy_section(ROOT / "en" / "infrastructure.html", "en")
    update_infrastructure_energy_section(ROOT / "hu" / "infrastructure.html", "hu")
    print("Fusion Grid SVGs successfully generated and linked!")


if __name__ == "__main__":
    main()
