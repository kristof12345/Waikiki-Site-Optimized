#!/usr/bin/env python3
"""
Generate animated SVG illustrations for military.html.

Generates:
1. icons/military/missile-defense-en.svg & missile-defense-hu.svg (1160x520) - Transborder Missile Defense System

Shows the layered engagement architecture: space-based IR early warning satellites, early warning and
X-band radars, a command center data network, and three intercept tiers (midcourse exo-atmospheric,
terminal high endo-atmospheric and low-altitude point defense) engaging an ICBM, a short-range ballistic
missile and a cruise missile in a synchronized, looping SMIL animation.

Links standalone SVGs into en/military.html and hu/military.html (#doctrine section) via <img> tags.
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

OUT_DIR = ROOT / "icons" / "military"

W, H = 1160, 520
GROUND_Y = 410
KARMAN_Y = 140
ENDO_Y = 280
CYCLE = 12  # seconds per engagement loop

THREAT = "#ff6a4d"
THREAT_SOFT = "#e3735a"
INTERCEPTOR = "#8fd3ff"
GOLD = "#f5c46e"
BLUE = "#6BA4D9"
GREEN = "#2ecc71"
INK = "#04121a"


def n(val: float) -> str:
    if isinstance(val, int):
        return str(val)
    return f"{val:.1f}".rstrip("0").rstrip(".")


def lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def quad_split(p0, p1, p2, t):
    """Return the control points of a quadratic Bezier truncated at parameter t (de Casteljau)."""
    q1 = lerp(p0, p1, t)
    r1 = lerp(p1, p2, t)
    end = lerp(q1, r1, t)
    return p0, q1, end


def quad_d(p0, p1, p2) -> str:
    return f"M{n(p0[0])},{n(p0[1])} Q{n(p1[0])},{n(p1[1])} {n(p2[0])},{n(p2[1])}"


def wedge(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    """Pie wedge path between angles a0 and a1 (degrees, SVG orientation)."""
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy + r * math.sin(math.radians(a1))
    return f"M{n(cx)},{n(cy)} L{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 0 1 {n(x1)},{n(y1)} Z"


def tip(pivot: tuple[float, float], angle: float, length: float) -> tuple[float, float]:
    return (
        pivot[0] + length * math.cos(math.radians(angle)),
        pivot[1] + length * math.sin(math.radians(angle)),
    )


def kt(*vals: float) -> str:
    return ";".join(n(v) if not isinstance(v, str) else v for v in vals)


# ==============================================================================
# ENGAGEMENT (threat + interceptor + intercept flash), fully synchronized via SMIL
# ==============================================================================
def engagement(
    uid: str,
    threat_d: str,
    interceptor_d: str,
    hit: tuple[float, float],
    begin: float,
    t_launch: float,
    t_hit: float,
    label: str,
    threat_scale: float = 1.0,
    interceptor_scale: float = 1.0,
) -> str:
    dur = f"{CYCLE}s"
    beg = f"{n(begin)}s"
    fade = min(t_hit + 0.14, 0.98)
    common = f'dur="{dur}" begin="{beg}" repeatCount="indefinite"'
    return f"""<!-- Engagement: {uid} -->
    <g>
        <path id="{uid}-threat" d="{threat_d}" fill="none" stroke="none" />
        <path id="{uid}-int" d="{interceptor_d}" fill="none" stroke="none" />
        <!-- Threat exhaust trail -->
        <path d="{threat_d}" pathLength="1" fill="none" stroke="{THREAT}" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0.18">
            <animate attributeName="stroke-dashoffset" values="1;0;0" keyTimes="0;{n(t_hit)};1" {common} />
            <animate attributeName="opacity" values="0.18;0.18;0;0" keyTimes="0;{n(t_hit)};{n(fade)};1" {common} />
        </path>
        <path d="{threat_d}" pathLength="1" fill="none" stroke="{THREAT}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0.9">
            <animate attributeName="stroke-dashoffset" values="1;0;0" keyTimes="0;{n(t_hit)};1" {common} />
            <animate attributeName="opacity" values="0.9;0.9;0;0" keyTimes="0;{n(t_hit)};{n(fade)};1" {common} />
        </path>
        <!-- Interceptor smoke trail -->
        <path d="{interceptor_d}" pathLength="1" fill="none" stroke="#e8f6ff" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0.16">
            <animate attributeName="stroke-dashoffset" values="1;1;0;0" keyTimes="0;{n(t_launch)};{n(t_hit)};1" {common} />
            <animate attributeName="opacity" values="0.16;0.16;0;0" keyTimes="0;{n(t_hit)};{n(fade)};1" {common} />
        </path>
        <path d="{interceptor_d}" pathLength="1" fill="none" stroke="{INTERCEPTOR}" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0.95">
            <animate attributeName="stroke-dashoffset" values="1;1;0;0" keyTimes="0;{n(t_launch)};{n(t_hit)};1" {common} />
            <animate attributeName="opacity" values="0.95;0.95;0;0" keyTimes="0;{n(t_hit)};{n(fade)};1" {common} />
        </path>
        <!-- Hostile missile -->
        <g opacity="0">
            <g transform="scale({n(threat_scale)})">
                <path d="M-14,0 L-24,-3.2 L-21,0 L-24,3.2 Z" fill="#ffb347" class="flicker" />
                <path d="M-12,-2.6 L6,-2.6 L12,0 L6,2.6 L-12,2.6 Z" fill="#f2e6dc" stroke="#7a1d12" stroke-width="0.8" />
                <path d="M-12,-2.6 L-15,-5.5 L-9,-2.6 Z M-12,2.6 L-15,5.5 L-9,2.6 Z" fill="#c0392b" />
                <path d="M6,-2.6 L12,0 L6,2.6 Z" fill="{THREAT}" />
            </g>
            <animate attributeName="opacity" calcMode="discrete" values="1;0" keyTimes="0;{n(t_hit)}" {common} />
            <animateMotion calcMode="linear" keyPoints="0;1;1" keyTimes="0;{n(t_hit)};1" rotate="auto" {common}>
                <mpath href="#{uid}-threat" />
            </animateMotion>
        </g>
        <!-- Interceptor -->
        <g opacity="0">
            <g transform="scale({n(interceptor_scale)})">
                <path d="M-11,0 L-20,-2.6 L-17,0 L-20,2.6 Z" fill="#ffe08a" class="flicker" />
                <path d="M-10,-2 L5,-2 L10,0 L5,2 L-10,2 Z" fill="#ffffff" stroke="#1A528F" stroke-width="0.8" />
                <path d="M-10,-2 L-12.5,-4.5 L-7,-2 Z M-10,2 L-12.5,4.5 L-7,2 Z" fill="{BLUE}" />
            </g>
            <animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{n(t_launch)};{n(t_hit)}" {common} />
            <animateMotion calcMode="linear" keyPoints="0;0;1;1" keyTimes="0;{n(t_launch)};{n(t_hit)};1" rotate="auto" {common}>
                <mpath href="#{uid}-int" />
            </animateMotion>
        </g>
        <!-- Intercept flash -->
        <g transform="translate({n(hit[0])}, {n(hit[1])})">
            <circle r="0" fill="#fff4d6" opacity="0" filter="url(#md-glow)">
                <animate attributeName="r" values="0;0;14;20;20" keyTimes="0;{n(t_hit)};{n(t_hit + 0.02)};{n(t_hit + 0.08)};1" {common} />
                <animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{n(t_hit)};{n(t_hit + 0.01)};{n(t_hit + 0.08)};1" {common} />
            </circle>
            <circle r="0" fill="none" stroke="{GOLD}" stroke-width="2" opacity="0">
                <animate attributeName="r" values="0;0;38;38" keyTimes="0;{n(t_hit)};{n(t_hit + 0.1)};1" {common} />
                <animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{n(t_hit)};{n(t_hit + 0.005)};{n(t_hit + 0.1)};1" {common} />
            </circle>
            <circle r="0" fill="none" stroke="#ffffff" stroke-width="1" opacity="0">
                <animate attributeName="r" values="0;0;24;24" keyTimes="0;{n(t_hit)};{n(t_hit + 0.07)};1" {common} />
                <animate attributeName="opacity" values="0;0;0.9;0;0" keyTimes="0;{n(t_hit)};{n(t_hit + 0.005)};{n(t_hit + 0.07)};1" {common} />
            </circle>
            <text x="0" y="-26" fill="{GOLD}" font-size="10" font-weight="800" letter-spacing="1.4" text-anchor="middle" opacity="0">{label}
                <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{n(t_hit)};{n(t_hit + 0.01)};{n(t_hit + 0.12)};{n(t_hit + 0.16)};1" {common} />
            </text>
        </g>
    </g>"""


# ==============================================================================
# TRANSBORDER MISSILE DEFENSE SVG (1160 x 520)
# ==============================================================================
def build_missile_defense_svg(lang: str = "en") -> str:
    is_hu = lang == "hu"
    pfx = "md-hu" if is_hu else "md"

    if is_hu:
        hud_title = "HATÁRON ÁTÍVELŐ RAKÉTAVÉDELEM · 132 MRD ₩"
        hud_status = "MINDEN RÉTEG AKTÍV"
        karman = "KÁRMÁN-VONAL · 100 KM"
        endo = "40 KM"
        tiers = [
            ("FELSŐ RÉTEG · PÁLYAKÖZÉPI", "LÉGKÖRÖN KÍVÜL · ICBM", INTERCEPTOR),
            ("KÖZÉPSŐ RÉTEG · ZÁRÓFÁZIS", "MAGAS LÉGKÖR · SRBM", GOLD),
            ("ALSÓ RÉTEG · PONTVÉDELEM", "ALACSONY MAGASSÁG · CIRKÁLÓRAKÉTA", GREEN),
        ]
        sat_label = "IR ELŐREJELZŐ MŰHOLD"
        dome_text = "HATÁRON ÁTÍVELŐ VÉDŐERNYŐ"
        intercept = "ELFOGÁS"
        lbl_launch = "ELLENSÉGES|INDÍTÓHELYEK"
        lbl_border = "HATÁR"
        lbl_xband = "X-SÁVÚ|RADAR"
        lbl_point = "PONTVÉDELMI|INDÍTÓ"
        lbl_terminal = "ZÁRÓFÁZISÚ|ÜTEG"
        lbl_c2 = "PARANCSNOKI|KÖZPONT"
        lbl_silo = "ELFOGÓ|SILÓK"
        lbl_city = "VÉDETT|VÁROS"
        lbl_ewr = "KORAI ELŐREJELZŐ|RADAR"
        legend = [("FENYEGETÉS", "threat"), ("ELFOGÓ RAKÉTA", "int"), ("ADATKAPCSOLAT", "link")]
        badge_l1 = "TÖBBRÉTEGŰ ELFOGÁS"
        badge_l2 = "SRBM-TŐL ICBM-IG · 3 RÉTEG"
        badge_r1 = "INTEGRÁLT ÉRZÉKELŐHÁLÓZAT"
        badge_r2 = "RADAROK · ŰRALAPÚ IR SZENZOROK"
    else:
        hud_title = "TRANSBORDER MISSILE DEFENSE · ₩132 BILLION"
        hud_status = "ALL LAYERS ACTIVE"
        karman = "KÁRMÁN LINE · 100 KM"
        endo = "40 KM"
        tiers = [
            ("UPPER TIER · MIDCOURSE", "EXO-ATMOSPHERIC · ICBM", INTERCEPTOR),
            ("MIDDLE TIER · TERMINAL", "HIGH ATMOSPHERE · SRBM", GOLD),
            ("LOWER TIER · POINT DEFENSE", "LOW ALTITUDE · CRUISE MISSILE", GREEN),
        ]
        sat_label = "IR EARLY WARNING SATELLITE"
        dome_text = "TRANSBORDER DEFENSE UMBRELLA"
        intercept = "INTERCEPT"
        lbl_launch = "HOSTILE|LAUNCH SITES"
        lbl_border = "BORDER"
        lbl_xband = "X-BAND|RADAR"
        lbl_point = "POINT DEFENSE|LAUNCHER"
        lbl_terminal = "TERMINAL|BATTERY"
        lbl_c2 = "COMMAND|CENTER"
        lbl_silo = "INTERCEPTOR|SILOS"
        lbl_city = "PROTECTED|CITY"
        lbl_ewr = "EARLY WARNING|RADAR"
        legend = [("THREAT", "threat"), ("INTERCEPTOR", "int"), ("DATA LINK", "link")]
        badge_l1 = "MULTI-LAYER INTERCEPT"
        badge_l2 = "SRBM TO ICBM · 3 TIERS"
        badge_r1 = "INTEGRATED SENSOR NETWORK"
        badge_r2 = "RADARS · SPACE-BASED IR SENSORS"

    rng = random.Random(132)
    clip_id = f"{pfx}-clip"

    # Key geometry
    icbm_tel_x, srbm_tel_x = 78, 196
    border_x = 330
    xband_x, point_x, terminal_x, c2_x, silo_x, city_x, ewr_x = 410, 515, 640, 762, 884, 990, 1092
    sat1, sat2 = (250, 74), (872, 70)

    icbm_p0, icbm_p1, icbm_p2 = (icbm_tel_x, 368), (560, -200), (1000, 384)
    srbm_p0, srbm_p1, srbm_p2 = (srbm_tel_x, 384), (470, 70), (c2_x, 392)
    icbm_t, srbm_t = 0.6, 0.62

    icbm_cut = quad_split(icbm_p0, icbm_p1, icbm_p2, icbm_t)
    srbm_cut = quad_split(srbm_p0, srbm_p1, srbm_p2, srbm_t)
    icbm_hit, srbm_hit = icbm_cut[2], srbm_cut[2]

    terminal_pivot = (terminal_x + 10, GROUND_Y - 16)
    terminal_angle, terminal_len = -125, 34
    terminal_tip = tip(terminal_pivot, terminal_angle, terminal_len)
    point_pivot = (point_x + 8, GROUND_Y - 15)
    point_angle, point_len = -145, 24
    point_tip = tip(point_pivot, point_angle, point_len)
    silo_launch = (silo_x, GROUND_Y - 4)

    cruise_hit = (452, 366)
    cruise_d = f"M-30,348 C90,346 260,364 {n(cruise_hit[0])},{n(cruise_hit[1])}"
    gbi_d = (
        f"M{n(silo_launch[0])},{n(silo_launch[1])} C{n(silo_launch[0])},250 "
        f"{n(icbm_hit[0] + 120)},{n(icbm_hit[1] + 40)} {n(icbm_hit[0])},{n(icbm_hit[1])}"
    )
    terminal_d = (
        f"M{n(terminal_tip[0])},{n(terminal_tip[1])} C{n(terminal_tip[0] - 22)},{n(terminal_tip[1] - 46)} "
        f"{n(srbm_hit[0] + 40)},{n(srbm_hit[1] + 34)} {n(srbm_hit[0])},{n(srbm_hit[1])}"
    )
    point_d = (
        f"M{n(point_tip[0])},{n(point_tip[1])} C{n(point_tip[0] - 20)},{n(point_tip[1] - 16)} "
        f"{n(cruise_hit[0] + 26)},{n(cruise_hit[1] - 6)} {n(cruise_hit[0])},{n(cruise_hit[1])}"
    )

    defs = f"""    <defs>
        <clipPath id="{clip_id}">
            <rect width="{W}" height="{H}" />
        </clipPath>
        <style>
            @keyframes twinkle {{ 0%, 100% {{ opacity: 0.25; }} 50% {{ opacity: 1; }} }}
            @keyframes dash {{ to {{ stroke-dashoffset: -40; }} }}
            @keyframes dashSlow {{ to {{ stroke-dashoffset: -60; }} }}
            @keyframes pulse {{ 0% {{ transform: scale(0.6); opacity: 0.9; }} 70% {{ transform: scale(1.8); opacity: 0; }} 100% {{ opacity: 0; }} }}
            @keyframes coneScan {{ 0%, 100% {{ opacity: 0.55; }} 50% {{ opacity: 1; }} }}
            @keyframes flicker {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.55; }} }}
            @keyframes blink {{ 0%, 60%, 100% {{ opacity: 1; }} 70%, 90% {{ opacity: 0.2; }} }}
            .twinkle {{ animation: twinkle 3.2s ease-in-out infinite; }}
            .twinkle:nth-of-type(2n) {{ animation-duration: 4.5s; animation-delay: 0.8s; }}
            .twinkle:nth-of-type(3n) {{ animation-duration: 2.8s; animation-delay: 1.5s; }}
            .dash {{ animation: dash 2.5s linear infinite; }}
            .dash-slow {{ animation: dashSlow 6s linear infinite; }}
            .pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 2.6s ease-out infinite; }}
            .cone {{ animation: coneScan 3.6s ease-in-out infinite; }}
            .flicker {{ animation: flicker 0.18s linear infinite; }}
            .blink {{ animation: blink 2.2s linear infinite; }}
            text {{ font-family: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        </style>
        <linearGradient id="{pfx}-sky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#01050b" />
            <stop offset="26%" stop-color="#030c18" />
            <stop offset="52%" stop-color="#071a2c" />
            <stop offset="72%" stop-color="#0b2639" />
            <stop offset="88%" stop-color="#123447" />
            <stop offset="100%" stop-color="#1b4458" />
        </linearGradient>
        <linearGradient id="{pfx}-airglow" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="{BLUE}" stop-opacity="0" />
            <stop offset="70%" stop-color="{BLUE}" stop-opacity="0.08" />
            <stop offset="100%" stop-color="#9fd8ff" stop-opacity="0.2" />
        </linearGradient>
        <linearGradient id="{pfx}-hostile-ground" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#2a1a1a" />
            <stop offset="100%" stop-color="#0c0808" />
        </linearGradient>
        <linearGradient id="{pfx}-home-ground" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#11332e" />
            <stop offset="100%" stop-color="#04110f" />
        </linearGradient>
        <linearGradient id="{pfx}-cone" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="{GOLD}" stop-opacity="0.38" />
            <stop offset="55%" stop-color="{GOLD}" stop-opacity="0.08" />
            <stop offset="100%" stop-color="{GOLD}" stop-opacity="0.02" />
        </linearGradient>
        <linearGradient id="{pfx}-dome" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="{BLUE}" stop-opacity="0.12" />
            <stop offset="100%" stop-color="{BLUE}" stop-opacity="0.02" />
        </linearGradient>
        <linearGradient id="{pfx}-panel" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#2b5a9a" />
            <stop offset="50%" stop-color="#16325e" />
            <stop offset="100%" stop-color="#0a1a36" />
        </linearGradient>
        <linearGradient id="{pfx}-foil" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffd57a" />
            <stop offset="45%" stop-color="#dfa438" />
            <stop offset="100%" stop-color="#7a4f12" />
        </linearGradient>
        <linearGradient id="{pfx}-concrete" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#9fb4ba" />
            <stop offset="100%" stop-color="#4b6168" />
        </linearGradient>
        <linearGradient id="{pfx}-olive" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#5f6f52" />
            <stop offset="100%" stop-color="#2f3a29" />
        </linearGradient>
        <radialGradient id="{pfx}-ewr-beam" cx="{ewr_x - 18}" cy="{GROUND_Y - 44}" r="600" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="{BLUE}" stop-opacity="0.42" />
            <stop offset="60%" stop-color="{BLUE}" stop-opacity="0.1" />
            <stop offset="100%" stop-color="{BLUE}" stop-opacity="0" />
        </radialGradient>
        <radialGradient id="{pfx}-xband-beam" cx="{xband_x - 4}" cy="{GROUND_Y - 30}" r="320" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#9fe0ff" stop-opacity="0.45" />
            <stop offset="100%" stop-color="#9fe0ff" stop-opacity="0" />
        </radialGradient>
        <radialGradient id="{pfx}-launch-glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#ffcf70" stop-opacity="0.9" />
            <stop offset="100%" stop-color="#ff6a4d" stop-opacity="0" />
        </radialGradient>
        <filter id="md-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
    </defs>"""

    body: list[str] = []

    # 1. Sky, airglow and starfield
    body.append(f'<rect width="{W}" height="{H}" fill="url(#{pfx}-sky)" />')
    body.append(f'<rect x="0" y="{KARMAN_Y}" width="{W}" height="{GROUND_Y - KARMAN_Y}" fill="url(#{pfx}-airglow)" />')
    faint = []
    for _ in range(110):
        fx, fy = rng.uniform(8, W - 8), rng.uniform(8, KARMAN_Y + 20)
        faint.append(f'<circle cx="{n(fx)}" cy="{n(fy)}" r="{n(rng.uniform(0.5, 1.0))}" />')
    body.append('<g fill="#ffffff" opacity="0.55">\n' + "\n".join(faint) + "\n</g>")
    bright = []
    for _ in range(22):
        bx, by = rng.uniform(20, W - 20), rng.uniform(14, KARMAN_Y)
        col = rng.choice(["#ffffff", "#aed8f2", "#ffe8b8"])
        bright.append(f'<circle class="twinkle" cx="{n(bx)}" cy="{n(by)}" r="{n(rng.uniform(1.1, 1.8))}" fill="{col}" />')
    body.append("<g>\n" + "\n".join(bright) + "\n</g>")

    # 2. Altitude reference lines
    body.append(f"""<!-- Altitude Reference Lines -->
    <g font-size="9.5" font-weight="700" letter-spacing="1.2">
        <line x1="0" y1="{KARMAN_Y}" x2="{W}" y2="{KARMAN_Y}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="3 7" opacity="0.5" />
        <text x="22" y="{KARMAN_Y - 7}" fill="{BLUE}" opacity="0.9">{karman}</text>
        <line x1="0" y1="{ENDO_Y}" x2="{W}" y2="{ENDO_Y}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="3 7" opacity="0.32" />
        <text x="22" y="{ENDO_Y - 7}" fill="{BLUE}" opacity="0.8">{endo}</text>
    </g>""")

    # 3. Tier labels (right side, one per altitude band)
    tier_y = [104, KARMAN_Y + 30, ENDO_Y + 30]
    tier_els = []
    for (title, sub, col), ty in zip(tiers, tier_y):
        tier_els.append(f"""<g transform="translate(1136, {ty})">
            <rect x="-4" y="-10" width="4" height="26" rx="2" fill="{col}" />
            <text x="-12" y="0" fill="#fbf7f0" font-size="11" font-weight="800" letter-spacing="1.2" text-anchor="end">{title}</text>
            <text x="-12" y="14" fill="{col}" font-size="9.5" font-weight="700" letter-spacing="1" text-anchor="end">{sub}</text>
        </g>""")
    body.append("<!-- Engagement Tier Labels -->\n<g>\n" + "\n".join(tier_els) + "\n</g>")

    # 4. Transborder defense umbrella (extends past the border to cover allied airspace)
    dome_id = f"{pfx}-dome-arc"
    dome_d = f"M215,{GROUND_Y} A575,300 0 0 1 1365,{GROUND_Y}"
    body.append(f"""<!-- Transborder Defense Umbrella -->
    <path d="{dome_d} Z" fill="url(#{pfx}-dome)" />
    <path id="{dome_id}" d="{dome_d}" fill="none" stroke="{BLUE}" stroke-width="1.6" stroke-dasharray="10 8" opacity="0.6" class="dash-slow" />
    <path d="{dome_d}" fill="none" stroke="{BLUE}" stroke-width="7" opacity="0.07" />
    <text font-size="10" font-weight="800" letter-spacing="2.2" fill="{BLUE}" dy="-6">
        <textPath href="#{dome_id}" startOffset="8%">{dome_text}</textPath>
    </text>""")

    # 5. Satellite IR sensor cone over the launch area and orbital crosslinks
    body.append(f"""<!-- Space-Based Infrared Sensor Coverage -->
    <polygon points="{sat1[0] - 6},{sat1[1] + 14} {sat1[0] + 6},{sat1[1] + 14} 312,{GROUND_Y} 30,{GROUND_Y}" fill="url(#{pfx}-cone)" class="cone" />
    <polygon points="{sat2[0] - 5},{sat2[1] + 14} {sat2[0] + 5},{sat2[1] + 14} 700,{KARMAN_Y + 20} 590,{KARMAN_Y + 8}" fill="url(#{pfx}-cone)" opacity="0.7" class="cone" />
    <path d="M{sat1[0] + 30},{sat1[1] - 2} Q{(sat1[0] + sat2[0]) // 2},{sat1[1] - 34} {sat2[0] - 30},{sat2[1] - 2}" fill="none" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="4 6" opacity="0.55" class="dash" />""")

    def satellite(cx: float, cy: float, flip: bool = False) -> str:
        return f"""<g transform="translate({cx}, {cy})">
        <line x1="-48" y1="0" x2="48" y2="0" stroke="#90a4ae" stroke-width="1.4" />
        <rect x="-50" y="-7" width="32" height="14" rx="1" fill="url(#{pfx}-panel)" stroke="#6BA4D9" stroke-width="0.8" />
        <rect x="18" y="-7" width="32" height="14" rx="1" fill="url(#{pfx}-panel)" stroke="#6BA4D9" stroke-width="0.8" />
        <path d="M-42,-7 V7 M-34,-7 V7 M-26,-7 V7 M26,-7 V7 M34,-7 V7 M42,-7 V7 M-50,0 H-18 M18,0 H50" stroke="#4f7fb8" stroke-width="0.6" />
        <rect x="-11" y="-10" width="22" height="20" rx="2" fill="url(#{pfx}-foil)" stroke="#5a3a0a" stroke-width="0.8" />
        <path d="M-11,-3 H11 M-11,4 H11" stroke="#8a5c16" stroke-width="0.6" opacity="0.8" />
        <rect x="-5" y="10" width="10" height="7" fill="#cfd8dc" stroke="#37474f" stroke-width="0.7" />
        <ellipse cx="0" cy="17" rx="5" ry="1.6" fill="#0b1730" stroke="{GOLD}" stroke-width="0.6" />
        <path d="M{'-' if flip else ''}8,-10 L{'-' if flip else ''}14,-18" stroke="#cfd8dc" stroke-width="1" />
        <path d="M{'-' if flip else ''}10,-21 Q{'-' if flip else ''}16,-22 {'-' if flip else ''}18,-16" fill="none" stroke="#cfd8dc" stroke-width="1.6" />
        <circle cx="0" cy="0" r="2" fill="{GREEN}" class="blink" />
    </g>"""

    body.append("<!-- IR Early Warning Satellites -->")
    body.append(satellite(*sat1))
    body.append(satellite(*sat2, flip=True))
    body.append(f'<text x="{sat1[0] + 58}" y="{sat1[1] + 4}" fill="{GOLD}" font-size="9" font-weight="700" letter-spacing="1.1">{sat_label}</text>')

    # 6. Radar beams (behind ground assets)
    ewr_origin = (ewr_x - 18, GROUND_Y - 44)
    xband_origin = (xband_x - 4, GROUND_Y - 30)
    body.append(f"""<!-- Early Warning Radar Sweep -->
    <g>
        <path d="{wedge(ewr_origin[0], ewr_origin[1], 600, -172, -150)}" fill="url(#{pfx}-ewr-beam)" />
        <animateTransform attributeName="transform" type="rotate" values="0 {n(ewr_origin[0])} {n(ewr_origin[1])}; 32 {n(ewr_origin[0])} {n(ewr_origin[1])}; 0 {n(ewr_origin[0])} {n(ewr_origin[1])}" dur="9s" repeatCount="indefinite" />
    </g>
    <!-- Forward X-Band Radar Beam -->
    <g>
        <path d="{wedge(xband_origin[0], xband_origin[1], 320, -128, -116)}" fill="url(#{pfx}-xband-beam)" />
        <animateTransform attributeName="transform" type="rotate" values="0 {n(xband_origin[0])} {n(xband_origin[1])}; -22 {n(xband_origin[0])} {n(xband_origin[1])}; 0 {n(xband_origin[0])} {n(xband_origin[1])}" dur="5s" repeatCount="indefinite" />
    </g>""")

    # 7. Predicted (averted) threat trajectories
    body.append(f"""<!-- Predicted Threat Trajectories -->
    <g fill="none" stroke="{THREAT_SOFT}" stroke-width="1.1" stroke-dasharray="2 6" opacity="0.45">
        <path d="{quad_d(icbm_p0, icbm_p1, icbm_p2)}" />
        <path d="{quad_d(srbm_p0, srbm_p1, srbm_p2)}" />
        <path d="M{n(cruise_hit[0])},{n(cruise_hit[1])} C560,358 680,372 {c2_x - 10},388" />
    </g>
    <g transform="translate({icbm_p2[0]}, {icbm_p2[1]})" fill="none" stroke="{THREAT_SOFT}" stroke-width="1.2" opacity="0.8">
        <circle r="9" />
        <path d="M-14,0 H-5 M5,0 H14 M0,-14 V-5 M0,5 V14" />
        <circle r="9" class="pulse" />
    </g>""")

    # 8. Ground: hostile side and Waikiki territory
    body.append(f"""<!-- Terrain -->
    <path d="M0,{GROUND_Y + 2} C60,{GROUND_Y - 6} 140,{GROUND_Y - 2} 210,{GROUND_Y - 5} C260,{GROUND_Y - 7} 300,{GROUND_Y - 1} {border_x},{GROUND_Y} L{border_x},{H} L0,{H} Z" fill="url(#{pfx}-hostile-ground)" />
    <path d="M{border_x},{GROUND_Y} C420,{GROUND_Y - 4} 560,{GROUND_Y + 2} 700,{GROUND_Y - 2} C840,{GROUND_Y - 5} 960,{GROUND_Y + 1} {W},{GROUND_Y - 3} L{W},{H} L{border_x},{H} Z" fill="url(#{pfx}-home-ground)" />
    <path d="M0,{GROUND_Y + 2} C60,{GROUND_Y - 6} 140,{GROUND_Y - 2} 210,{GROUND_Y - 5} C260,{GROUND_Y - 7} 300,{GROUND_Y - 1} {border_x},{GROUND_Y} C420,{GROUND_Y - 4} 560,{GROUND_Y + 2} 700,{GROUND_Y - 2} C840,{GROUND_Y - 5} 960,{GROUND_Y + 1} {W},{GROUND_Y - 3}" fill="none" stroke="#5e8f86" stroke-width="1.2" opacity="0.55" />
    <!-- Border -->
    <g>
        <line x1="{border_x}" y1="300" x2="{border_x}" y2="{GROUND_Y + 34}" stroke="{THREAT_SOFT}" stroke-width="1.4" stroke-dasharray="6 5" opacity="0.8" />
        <rect x="{border_x - 3}" y="{GROUND_Y - 14}" width="6" height="14" fill="#e8e1d6" />
        <rect x="{border_x - 3}" y="{GROUND_Y - 14}" width="6" height="4" fill="{THREAT_SOFT}" />
        <rect x="{border_x - 3}" y="{GROUND_Y - 6}" width="6" height="3" fill="{THREAT_SOFT}" />
    </g>""")

    # 9. Hostile launchers
    body.append(f"""<!-- Hostile Road-Mobile ICBM Launcher -->
    <g transform="translate({icbm_tel_x}, {GROUND_Y - 4})">
        <rect x="-30" y="-12" width="54" height="8" rx="1.5" fill="#4a3f36" stroke="#1d1712" stroke-width="0.8" />
        <rect x="24" y="-18" width="12" height="14" rx="2" fill="#5a4c40" stroke="#1d1712" stroke-width="0.8" />
        <rect x="27" y="-15" width="6" height="4" fill="#9fb4ba" opacity="0.7" />
        <rect x="-5" y="-40" width="10" height="28" rx="1.5" fill="#6b5c4e" stroke="#1d1712" stroke-width="0.8" />
        <path d="M-5,-12 L-20,-12 L-5,-30 Z" fill="#3b322a" />
        <g fill="#141414"><circle cx="-22" cy="-3" r="4" /><circle cx="-10" cy="-3" r="4" /><circle cx="6" cy="-3" r="4" /><circle cx="18" cy="-3" r="4" /><circle cx="30" cy="-3" r="4" /></g>
    </g>
    <!-- Hostile Short-Range Ballistic Missile Launcher -->
    <g transform="translate({srbm_tel_x}, {GROUND_Y - 5})">
        <rect x="-22" y="-10" width="40" height="7" rx="1.5" fill="#4a3f36" stroke="#1d1712" stroke-width="0.8" />
        <rect x="18" y="-16" width="10" height="13" rx="2" fill="#5a4c40" stroke="#1d1712" stroke-width="0.8" />
        <rect x="-4" y="-22" width="8" height="12" rx="1" fill="#6b5c4e" stroke="#1d1712" stroke-width="0.8" />
        <g fill="#141414"><circle cx="-14" cy="-2" r="3.5" /><circle cx="-2" cy="-2" r="3.5" /><circle cx="10" cy="-2" r="3.5" /><circle cx="22" cy="-2" r="3.5" /></g>
    </g>""")

    # Launch flashes synced with each engagement
    def launch_flash(x: float, y: float, begin: float) -> str:
        common = f'dur="{CYCLE}s" begin="{n(begin)}s" repeatCount="indefinite"'
        return f"""<circle cx="{n(x)}" cy="{n(y)}" r="16" fill="url(#{pfx}-launch-glow)" opacity="0">
        <animate attributeName="opacity" values="0;1;0;0" keyTimes="0;0.01;0.08;1" {common} />
        <animate attributeName="r" values="6;18;26;26" keyTimes="0;0.02;0.08;1" {common} />
    </circle>"""

    body.append("<!-- Launch Flashes -->")
    body.append(launch_flash(icbm_p0[0], icbm_p0[1], 0))
    body.append(launch_flash(srbm_p0[0], srbm_p0[1], 4))

    # 10. Waikiki defensive assets
    body.append(f"""<!-- Forward-Based X-Band Radar -->
    <g transform="translate({xband_x}, {GROUND_Y - 3})">
        <rect x="-24" y="-10" width="46" height="7" rx="1.5" fill="url(#{pfx}-olive)" stroke="#1c2418" stroke-width="0.8" />
        <g transform="translate(-4, -22) rotate(-35)">
            <rect x="-14" y="-3" width="28" height="22" rx="1.5" fill="#3a4a3a" stroke="#9fe0ff" stroke-width="1" />
            <path d="M-10,1 H10 M-10,5 H10 M-10,9 H10 M-10,13 H10 M-6,-3 V19 M0,-3 V19 M6,-3 V19" stroke="#9fe0ff" stroke-width="0.5" opacity="0.7" />
        </g>
        <path d="M-4,-14 L4,-10 L8,-10" stroke="#2f3a29" stroke-width="2" fill="none" />
        <g fill="#141414"><circle cx="-14" cy="-2" r="3.5" /><circle cx="-4" cy="-2" r="3.5" /><circle cx="14" cy="-2" r="3.5" /></g>
    </g>
    <!-- Lower Tier Point Defense Launcher -->
    <g transform="translate({point_x}, {GROUND_Y - 3})">
        <rect x="-22" y="-10" width="44" height="7" rx="1.5" fill="url(#{pfx}-olive)" stroke="#1c2418" stroke-width="0.8" />
        <rect x="14" y="-18" width="11" height="10" rx="2" fill="#5f6f52" stroke="#1c2418" stroke-width="0.8" />
        <g transform="translate(8, -12) rotate({point_angle})">
            <rect x="0" y="-5" width="{point_len}" height="10" rx="1" fill="#4e5c43" stroke="#1c2418" stroke-width="0.8" />
            <path d="M{point_len},-5 V5 M0,0 H{point_len}" stroke="#1c2418" stroke-width="0.6" />
            <circle cx="{point_len}" cy="-2.5" r="1.4" fill="{GREEN}" />
            <circle cx="{point_len}" cy="2.5" r="1.4" fill="{GREEN}" />
        </g>
        <g fill="#141414"><circle cx="-14" cy="-2" r="3.5" /><circle cx="-2" cy="-2" r="3.5" /><circle cx="14" cy="-2" r="3.5" /></g>
    </g>
    <!-- Middle Tier Terminal Interceptor Battery -->
    <g transform="translate({terminal_x}, {GROUND_Y - 3})">
        <rect x="-28" y="-11" width="58" height="8" rx="1.5" fill="url(#{pfx}-olive)" stroke="#1c2418" stroke-width="0.8" />
        <rect x="22" y="-21" width="13" height="12" rx="2" fill="#5f6f52" stroke="#1c2418" stroke-width="0.8" />
        <rect x="25" y="-18" width="7" height="4" fill="#9fb4ba" opacity="0.7" />
        <g transform="translate(10, -13) rotate({terminal_angle})">
            <rect x="0" y="-7" width="{terminal_len}" height="14" rx="1.2" fill="#56664a" stroke="#1c2418" stroke-width="0.8" />
            <path d="M0,-2.3 H{terminal_len} M0,2.3 H{terminal_len}" stroke="#1c2418" stroke-width="0.6" />
            <rect x="{terminal_len - 3}" y="-7" width="3" height="14" fill="{GOLD}" opacity="0.85" />
        </g>
        <path d="M-6,-11 L4,-24 L10,-13" stroke="#2f3a29" stroke-width="2" fill="none" />
        <g fill="#141414"><circle cx="-20" cy="-2" r="3.8" /><circle cx="-8" cy="-2" r="3.8" /><circle cx="12" cy="-2" r="3.8" /><circle cx="24" cy="-2" r="3.8" /></g>
    </g>
    <!-- Hardened Command and Control Center -->
    <g transform="translate({c2_x}, {GROUND_Y})">
        <path d="M-40,0 L-30,-24 L30,-24 L40,0 Z" fill="url(#{pfx}-concrete)" stroke="#2c3e44" stroke-width="1" />
        <path d="M-30,-24 L30,-24" stroke="#d5ede9" stroke-width="1" opacity="0.6" />
        <rect x="-8" y="-12" width="16" height="12" fill="#1c2a30" stroke="#2c3e44" stroke-width="0.8" />
        <path d="M-24,-24 A12,12 0 0 1 0,-24 Z" fill="#e8eef0" stroke="#5f7a82" stroke-width="0.8" />
        <line x1="18" y1="-24" x2="18" y2="-48" stroke="#b0bec5" stroke-width="1.6" />
        <path d="M10,-42 L26,-42 M12,-36 L24,-36" stroke="#b0bec5" stroke-width="1.2" />
        <circle cx="18" cy="-49" r="2" fill="{THREAT}" class="blink" />
        <g fill="#ffcf70" opacity="0.9"><rect x="-26" y="-18" width="5" height="3" /><rect x="-18" y="-18" width="5" height="3" /><rect x="14" y="-18" width="5" height="3" /><rect x="22" y="-18" width="5" height="3" /></g>
        <circle cx="-12" cy="-36" r="4" fill="none" stroke="{GOLD}" stroke-width="1.4" class="pulse" />
    </g>
    <!-- Midcourse Interceptor Silos -->
    <g transform="translate({silo_x}, {GROUND_Y})">
        <rect x="-44" y="-4" width="88" height="6" rx="1" fill="#3d5257" stroke="#22343a" stroke-width="0.8" />
        <g fill="#0b1214" stroke="#9fb4ba" stroke-width="0.8">
            <ellipse cx="-24" cy="-3" rx="8" ry="2.4" />
            <ellipse cx="0" cy="-3" rx="8" ry="2.4" />
            <ellipse cx="24" cy="-3" rx="8" ry="2.4" />
        </g>
        <g fill="#7f959b" stroke="#22343a" stroke-width="0.8">
            <rect x="-34" y="-8" width="10" height="3" rx="1" />
            <rect x="8" y="-14" width="3" height="11" rx="1" />
            <rect x="32" y="-8" width="10" height="3" rx="1" />
        </g>
    </g>""")

    # Protected city skyline
    buildings = [(-48, 18, 26), (-28, 14, 44), (-12, 16, 62), (6, 12, 38), (20, 18, 52), (40, 14, 30)]
    bld = []
    windows = []
    for bx, bw, bh in buildings:
        bld.append(f'<rect x="{bx}" y="{-bh}" width="{bw}" height="{bh}" fill="#16313a" stroke="#2c5560" stroke-width="0.8" />')
        for wy in range(-bh + 5, -3, 7):
            for wx in range(bx + 3, bx + bw - 3, 5):
                if rng.random() < 0.55:
                    windows.append(f'<rect x="{wx}" y="{wy}" width="2" height="3" />')
    body.append(f"""<!-- Protected City -->
    <g transform="translate({city_x}, {GROUND_Y})">
        {"".join(bld)}
        <g fill="#ffcf70" opacity="0.85">{"".join(windows)}</g>
        <line x1="-6" y1="-62" x2="-6" y2="-74" stroke="#9fb4ba" stroke-width="1" />
        <circle cx="-6" cy="-75" r="1.6" fill="{THREAT}" class="blink" />
    </g>""")

    # Early warning phased-array radar
    body.append(f"""<!-- Early Warning Phased-Array Radar -->
    <g transform="translate({ewr_x}, {GROUND_Y})">
        <path d="M-40,0 L-22,-76 L26,-76 L44,0 Z" fill="url(#{pfx}-concrete)" stroke="#2c3e44" stroke-width="1" />
        <path d="M-22,-76 L26,-76" stroke="#e8eef0" stroke-width="1.2" />
        <path d="M2,0 L2,-76" stroke="#5f7a82" stroke-width="0.8" opacity="0.7" />
        <g transform="translate(-18, -40) rotate(13)">
            <polygon points="-6,-17 6,-17 15,-8 15,8 6,17 -6,17 -15,8 -15,-8" fill="#1c3550" stroke="{BLUE}" stroke-width="1.2" />
            <path d="M-12,-8 H12 M-12,-3 H12 M-12,2 H12 M-12,7 H12 M-8,-14 V14 M-3,-15 V15 M2,-15 V15 M7,-14 V14" stroke="{BLUE}" stroke-width="0.5" opacity="0.7" />
            <circle r="3" fill="#9fe0ff" class="blink" />
        </g>
        <rect x="10" y="-30" width="22" height="30" fill="#5f7a82" opacity="0.35" />
    </g>""")

    # 11. Command data links (C2 hub)
    hub = (c2_x - 12, GROUND_Y - 36)
    links = [
        ((xband_x, GROUND_Y - 30), (580, 316)),
        ((point_x + 8, GROUND_Y - 22), (640, 340)),
        ((terminal_x + 10, GROUND_Y - 28), (700, 350)),
        ((silo_x, GROUND_Y - 12), (830, 350)),
        ((ewr_origin[0], ewr_origin[1]), (930, 318)),
    ]
    link_els = [
        f'<path d="M{n(hub[0])},{n(hub[1])} Q{n(c[0])},{n(c[1])} {n(p[0])},{n(p[1])}" />' for p, c in links
    ]
    link_els.append(f'<path d="M{n(hub[0])},{n(hub[1])} L{sat2[0]},{sat2[1] + 20}" />')
    body.append(
        f'<!-- Battle Management Data Links -->\n<g fill="none" stroke="{GOLD}" stroke-width="1.1" stroke-dasharray="4 6" opacity="0.5" class="dash">\n'
        + "\n".join(link_els)
        + "\n</g>"
    )

    # 12. Synchronized engagements
    body.append(
        engagement(
            f"{pfx}-icbm",
            quad_d(*icbm_cut),
            gbi_d,
            icbm_hit,
            begin=0,
            t_launch=0.32,
            t_hit=0.6,
            label=intercept,
            threat_scale=1.15,
        )
    )
    body.append(
        engagement(
            f"{pfx}-srbm",
            quad_d(*srbm_cut),
            terminal_d,
            srbm_hit,
            begin=4,
            t_launch=0.3,
            t_hit=0.5,
            label=intercept,
        )
    )
    body.append(
        engagement(
            f"{pfx}-cruise",
            cruise_d,
            point_d,
            cruise_hit,
            begin=8,
            t_launch=0.34,
            t_hit=0.44,
            label=intercept,
            threat_scale=0.85,
            interceptor_scale=0.8,
        )
    )

    # 13. Ground asset labels
    asset_labels = [
        ((icbm_tel_x + srbm_tel_x) / 2, lbl_launch, THREAT_SOFT, "middle"),
        (border_x, lbl_border, THREAT_SOFT, "middle"),
        (xband_x, lbl_xband, "#9fe0ff", "middle"),
        (point_x, lbl_point, GREEN, "middle"),
        (terminal_x, lbl_terminal, GOLD, "middle"),
        (c2_x, lbl_c2, "#d5ede9", "middle"),
        (silo_x, lbl_silo, INTERCEPTOR, "middle"),
        (city_x, lbl_city, "#ffcf70", "middle"),
        (ewr_x, lbl_ewr, BLUE, "middle"),
    ]
    label_els = []
    for x, t, c, a in asset_labels:
        spans = "".join(
            f'<tspan x="{n(x)}" dy="{0 if i == 0 else 10}">{part}</tspan>' for i, part in enumerate(t.split("|"))
        )
        label_els.append(f'<text y="{GROUND_Y + 17}" fill="{c}" text-anchor="{a}">{spans}</text>')
    body.append(
        '<!-- Asset Labels -->\n<g font-size="8" font-weight="800" letter-spacing="0.8">\n'
        + "\n".join(label_els)
        + "\n</g>"
    )

    # 14. HUD overlays
    body.append(f"""<!-- TOP HUD STATUS BAR -->
    <g font-size="11" font-weight="700" letter-spacing="1.5">
        <rect x="290" y="18" width="580" height="32" rx="16" fill="{INK}" stroke="{THREAT_SOFT}" stroke-width="1.2" opacity="0.95" />
        <text x="314" y="38" fill="#fbf7f0">{hud_title}</text>
        <circle cx="{n(846 - len(hud_status) * 8.4 - 12)}" cy="34" r="4" fill="{GREEN}" class="pulse" />
        <circle cx="{n(846 - len(hud_status) * 8.4 - 12)}" cy="34" r="3" fill="{GREEN}" />
        <text x="846" y="38" fill="{GREEN}" text-anchor="end">{hud_status}</text>
    </g>""")

    legend_x0 = 400
    legend_els = []
    lx = legend_x0
    for text, kind in legend:
        if kind == "threat":
            legend_els.append(f'<line x1="{lx}" y1="{H - 37}" x2="{lx + 22}" y2="{H - 37}" stroke="{THREAT}" stroke-width="2" />')
        elif kind == "int":
            legend_els.append(f'<line x1="{lx}" y1="{H - 37}" x2="{lx + 22}" y2="{H - 37}" stroke="{INTERCEPTOR}" stroke-width="2" />')
        else:
            legend_els.append(f'<line x1="{lx}" y1="{H - 37}" x2="{lx + 22}" y2="{H - 37}" stroke="{GOLD}" stroke-width="1.4" stroke-dasharray="4 4" class="dash" />')
        legend_els.append(f'<text x="{lx + 30}" y="{H - 33}" fill="#bedbd6">{text}</text>')
        lx += 30 + len(text) * 7.6 + 34
    legend_w = lx - legend_x0 - 34 + 40
    legend_cx = W / 2
    shift = legend_cx - (legend_x0 - 20 + legend_w / 2)
    body.append(f"""<!-- Legend -->
    <g transform="translate({n(shift)}, 0)" font-size="10" font-weight="700" letter-spacing="1">
        <rect x="{legend_x0 - 20}" y="{H - 55}" width="{n(legend_w)}" height="36" rx="18" fill="{INK}" stroke="rgba(107, 164, 217, 0.45)" stroke-width="1" opacity="0.95" />
        {"".join(legend_els)}
    </g>""")

    body.append(f"""<!-- Bottom-left corner badge -->
    <g font-size="10" font-weight="600" letter-spacing="1">
        <rect x="30" y="{H - 70}" width="250" height="50" rx="8" fill="{INK}" stroke="rgba(107, 164, 217, 0.45)" stroke-width="1" opacity="0.95" />
        <text x="44" y="{H - 47}" fill="{GOLD}">{badge_l1}</text>
        <text x="44" y="{H - 31}" fill="#bedbd6">{badge_l2}</text>
    </g>
    <!-- Bottom-right corner badge -->
    <g font-size="10" font-weight="600" letter-spacing="1" text-anchor="end">
        <rect x="{W - 280}" y="{H - 70}" width="250" height="50" rx="8" fill="{INK}" stroke="rgba(107, 164, 217, 0.45)" stroke-width="1" opacity="0.95" />
        <text x="{W - 44}" y="{H - 47}" fill="{BLUE}">{badge_r1}</text>
        <text x="{W - 44}" y="{H - 31}" fill="#bedbd6">{badge_r2}</text>
    </g>""")

    inner_content = "\n".join(body)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 {W} {H}">
{defs}
    <g clip-path="url(#{clip_id})">
{inner_content}
    </g>
</svg>"""


# ==============================================================================
# INJECTION AND LINKING INTO HTML
# ==============================================================================
def update_military_page(file_path: Path, lang: str = "en") -> None:
    content = file_path.read_text(encoding="utf-8")

    if lang == "hu":
        alt = "Határon átívelő rakétavédelmi rendszer többrétegű elfogási diagramja"
        cap_main = "A Határon Átívelő Rakétavédelmi Rendszer többrétegű elfogási architektúrája."
        cap_sub = "Űrszenzorok · Korai előrejelző radarok · Három elfogási réteg"
    else:
        alt = "Transborder Missile Defense System Layered Intercept Diagram"
        cap_main = "Layered engagement architecture of the Transborder Missile Defense System."
        cap_sub = "Space Sensors · Early Warning Radars · Three Intercept Tiers"

    img = f'<img class="ill" src="../icons/military/missile-defense-{lang}.svg" alt="{alt}" width="{W}" height="{H}" />'
    panel = (
        f'<div class="ill-panel">\n{img}\n<div class="ill-caption">\n'
        f"<span>{cap_main}</span>\n<span>{cap_sub}</span>\n</div>\n</div>\n"
    )

    existing = re.compile(
        r'(<section id="doctrine"[^>]*>.*?<div class="ill-panel">\s*)(?:<svg.*?</svg>|<img[^>]*class="ill"[^>]*>)(\s*<div class="ill-caption">)',
        re.DOTALL,
    )
    if existing.search(content):
        content = existing.sub(lambda m: m.group(1) + img + m.group(2), content, count=1)
    else:
        insert = re.compile(r'(<section id="doctrine"[^>]*>.*?<p class="section-intro">.*?</p>\s*)(<div class="card-grid">)', re.DOTALL)
        if not insert.search(content):
            raise ValueError(f"Could not find #doctrine section in {file_path}")
        content = insert.sub(lambda m: m.group(1) + panel + m.group(2), content, count=1)

    sys.path.insert(0, str(ROOT / "scripts"))
    from build_pages import format_and_remove_empty_lines

    formatted = format_and_remove_empty_lines(content)
    file_path.write_text(formatted, encoding="utf-8")
    print(f"Updated and formatted {file_path.relative_to(ROOT)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating standalone Military SVGs...")
    for lang in ("en", "hu"):
        svg = build_missile_defense_svg(lang)
        svg = "\n".join(line for line in svg.splitlines() if line.strip())
        out_file = OUT_DIR / f"missile-defense-{lang}.svg"
        out_file.write_text(svg + "\n", encoding="utf-8")
        print(f"  Saved {out_file.relative_to(ROOT)} ({len(svg) / 1024:.1f} KB)")

    update_military_page(ROOT / "en" / "military.html", "en")
    update_military_page(ROOT / "hu" / "military.html", "hu")
    print("Military SVGs successfully generated and linked!")


if __name__ == "__main__":
    main()
