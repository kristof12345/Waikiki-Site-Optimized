#!/usr/bin/env python3
"""Generate Nova Aurelia's four inline, pure-vector district illustrations.

Run directly to update both locales. Large standalone city illustrations are untouched.
"""
import math
import random
import re
from pathlib import Path
from xml.dom import minidom

ROOT = Path(__file__).resolve().parents[2]


def path(d, fill, extra=''):
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def rect(x, y, w, h, fill, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def ellipse(x, y, rx, ry, fill, extra=''):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


def palm(x, y, s=1, color='#153f43'):
    o = [f'<g transform="translate({x} {y}) scale({s})">', path('M-3 0 Q5 -43 0 -86 L5 -86 Q13 -40 4 0Z', '#786545')]
    for frond in [
        'M2 -85 Q-28 -113 -58 -88 Q-24 -99 2 -85Z',
        'M2 -85 Q-35 -94 -53 -57 Q-25 -79 2 -85Z',
        'M2 -85 Q-14 -88 -21 -45 Q-5 -69 2 -85Z',
        'M2 -85 Q-18 -118 -38 -119 Q-13 -99 2 -85Z',
        'M2 -85 Q14 -118 36 -116 Q15 -102 2 -85Z',
        'M2 -85 Q37 -112 61 -85 Q31 -97 2 -85Z',
        'M2 -85 Q42 -88 48 -52 Q27 -78 2 -85Z',
        'M2 -85 Q25 -80 21 -45 Q11 -68 2 -85Z',
    ]:
        o.append(path(frond, color))
    return ''.join(o) + '</g>'


def tower(x, y, w, h, color='#53828a'):
    o = [rect(x, y-h, w, h, color), path(f'M{x+w} {y-h} l12 9 v{h-9} h-12Z', '#244754'), path(f'M{x} {y-h} l12 -8 h{w-12} v8Z', '#bad3c9')]
    for yy in range(int(y-h+8), int(y-5), 9):
        o.append(path(f'M{x+3} {yy} h{w-6}', 'none', 'stroke="#cee4d9" stroke-width="1" opacity=".45"'))
    for xx in range(int(x+6), int(x+w), 9):
        o.append(path(f'M{xx} {y-h} V{y}', 'none', 'stroke="#183e4c" opacity=".35"'))
    return ''.join(o)


def yacht(x, y, s=1):
    return f'<g transform="translate({x} {y}) scale({s})">' + ellipse(0, 10, 65, 5, '#072e43', 'opacity=".25"') + path('M-63 0 Q0 9 65 -6 L48 10 Q-12 22 -51 9Z', '#fff6df') + path('M-44 -3 L-27 -19 H21 L40 -3Z', '#dce8df') + path('M-20 -17 H17 L28 -5 H-31Z', '#234d60') + path('M-9 -20 L-4 -32 H0 V-20Z', '#e8d9bd') + path('M-48 7 Q0 16 51 3', 'none', 'stroke="#b08a58" stroke-width="2"') + '</g>'


def scene(kind):
    p = 'na-' + kind + '-'
    night = kind == 'night-lagoon'
    sky = ['#07182f', '#244966', '#786c83'] if night else (['#4c8a9d', '#b5d5cd', '#f5dbb4'] if kind == 'aerotropolis' else ['#6f9da4', '#e6c9ae', '#ffdfaa'])
    o = ['<svg class="illustration" viewBox="0 0 800 560" aria-hidden="true" focusable="false">', '<defs>']
    for name, colors in [('sky', sky), ('water', ['#347e87', '#125362', '#072f43'] if not night else ['#16394e', '#08606a', '#071d36']), ('stone', ['#fff1d2', '#d5b585', '#8e7254']), ('glass', ['#c9ded7', '#659aa2', '#244a62'])]:
        o.append(f'<linearGradient id="{p}{name}" x2="0" y2="1">' + ''.join(f'<stop offset="{i/(len(colors)-1)}" stop-color="{c}"/>' for i,c in enumerate(colors)) + '</linearGradient>')
    o += [f'<radialGradient id="{p}haze"><stop stop-color="#ffdca2" stop-opacity=".65"/><stop offset="1" stop-color="#ffdca2" stop-opacity="0"/></radialGradient>', f'<radialGradient id="{p}glow"><stop stop-color="#70fff0" stop-opacity=".55"/><stop offset="1" stop-color="#23d5da" stop-opacity="0"/></radialGradient>', '</defs>', rect(0,0,800,560,f'url(#{p}sky)')]
    rng = random.Random(28)
    if night:
        for _ in range(85):
            o.append(ellipse(rng.randrange(800),rng.randrange(215),.8,.8,'#d9f4ed',f'opacity="{rng.uniform(.2,.8):.2f}"'))
        o += [ellipse(620,90,29,29,'#e4e6d3'), ellipse(610,83,27,27,'#203950')]
    else:
        o += [ellipse(580,174,220,165,f'url(#{p}haze)'), ellipse(580,174,34,34,'#fff1ce')]
        for x,y,w in [(100,75,170),(415,49,130),(690,115,145)]:
            o.append(path(f'M{x-w} {y} Q{x-40} {y-9} {x+25} {y} T{x+w} {y+2} Q{x+30} {y+10} {x-w} {y}Z', '#fff5df', 'opacity=".28"'))
    o.append(path('M0 258 Q95 202 175 240 T350 234 T560 247 T800 226 V350 H0Z', '#466774' if night else '#759896', 'opacity=".35"'))
    for i in range(24):
        x=i*36-20; h=rng.randrange(24,90)
        o.append(rect(x,278-h, rng.randrange(14,29),h,'#365868' if night else '#6b8e8e','opacity=".40"'))
    if kind == 'marina':
        o += [rect(0,300,800,260,f'url(#{p}water)')]
        for x,w,h in [(370,32,124),(420,42,172),(480,28,108),(530,45,140),(600,35,95),(665,40,164),(725,30,105)]:
            o.append(tower(x,298,w,h))
        o += [path('M0 303 Q125 275 300 302 T800 300 L800 319 Q520 330 300 320 T0 330Z','#d5c7a2'), ellipse(213,321,100,16,'#0a3a49','opacity=".4"'), ellipse(213,305,75,14,'#b7996d'),rect(169,284,88,20,'#ecd5a8'),path('M185 286 L200 111 H225 L242 286Z',f'url(#{p}glass)'),path('M190 286 L202 111 H210 L204 286Z','#f8e6ba')]
        for y in range(131,281,28):
            o.append(path(f'M195 {y} Q247 {y-27} 229 {y-36} M191 {y+7} Q248 {y-18} 231 {y-28}', 'none', 'stroke="#f2d393" stroke-width="6"'))
        o += [ellipse(214,110,27,8,'#d7b77c'),rect(196,88,36,23,'#466670'),rect(206,91,15,16,'#fff4ba'),path('M187 88 L214 65 L241 88Z','#e8cb91'),path('M214 65 V48','none','stroke="#f8e8c9" stroke-width="2"')]
        for x in [33,92,312,760]: o.append(palm(x,310,.55))
        for x,y,s in [(420,354,.55),(590,375,.70),(263,418,.85),(560,477,1.30),(80,370,.45)]: o.append(yacht(x,y,s))
        o += [path('M0 457 L183 395 L198 404 L0 480Z','#c6b58f'),path('M0 473 L198 405 V414 L0 488Z','#4d5250')]
        for x,y in [(35,459),(95,439),(159,419)]: o.append(rect(x,y-20,4,24,'#ede0b8'))
        o.append(palm(56,559,1.6,'#113b3b'))
    elif kind == 'boulevard':
        o += [path('M0 300 H800 V560 H0Z','#c4aa83'),path('M335 292 H465 L690 560 H110Z','#ead4ae'),path('M383 300 H417 L483 560 H317Z','#377c80')]
        for y in [320,348,388,446,524]: o.append(path(f'M0 {y} H800','none','stroke="#806f58" opacity=".23"'))
        for x in [60,155,245,555,645,740]: o.append(path(f'M400 290 L{x} 560','none','stroke="#947e60" opacity=".4"'))
        o += [rect(347,215,106,91,f'url(#{p}stone)'),path('M369 306 V260 a31 31 0 0 1 62 0 V306Z','#526b69'),rect(337,205,126,14,'#f6dfaf'),path('M333 205 L400 172 L467 205Z','#eed5a4'),path('M350 201 L400 179 L450 201Z','#b99a67')]
        for side in [False,True]:
            o.append(f'<g transform="{"translate(800 0) scale(-1 1)" if side else "translate(0 0)"}">')
            o += [path('M-20 118 L319 247 V265 L-20 168Z','#e6cca0'),path('M-20 118 L319 247 V253 L-20 132Z','#fff0cb'),path('M-20 168 L319 265 V274 L-20 183Z','#8e7655')]
            for x,y,h,w in [(26,172,276,32),(103,194,215,25),(166,214,166,20),(216,230,129,15),(258,244,98,12),(290,254,74,9)]:
                o += [rect(x,y,w,h,f'url(#{p}stone)'),rect(x-5,y-5,w+10,10,'#f6e1b7'),rect(x-6,y+h,w+12,9,'#e5c999')]
                for dx in [5,11,17,23]:
                    if dx<w: o.append(path(f'M{x+dx} {y+10} V{y+h-4}','none','stroke="#a78a62" opacity=".45"'))
                o += [ellipse(x,y+4,6,5,'#c1a274'),ellipse(x+w,y+4,6,5,'#c1a274')]
            for x,y,s in [(115,504,1.3),(214,420,.85),(280,361,.5),(321,329,.3)]: o.append(palm(x,y,s))
            o.append('</g>')
        for x,y,s in [(400,340,.3),(400,388,.6),(400,472,1)]:
            o += [ellipse(x,y,30*s,9*s,'#a4d9ce'),path(f'M{x-24*s} {y} Q{x} {y-76*s} {x+24*s} {y} M{x} {y} v{-55*s}', 'none',f'stroke="#eff9df" stroke-width="{2*s}"'),ellipse(x,y+4*s,33*s,5*s,'#d6c199')]
        o += [path('M523 439 Q523 416 545 413 H565 Q583 414 587 439 L581 449 H527Z','#fcf0d1'),path('M530 432 Q531 420 546 419 H564 Q575 419 579 432Z','#315765'),ellipse(534,450,5,5,'#354b4a'),ellipse(575,450,5,5,'#354b4a')]
    elif kind == 'aerotropolis':
        o += [rect(0,280,800,280,'#98b9b5'),path('M0 400 L800 306 V560 H0Z','#526e76'),path('M70 560 L800 360 V387 L182 560Z','#d5cfb1')]
        for i in range(9):
            x=210+i*75; y=552-i*21
            o.append(path(f'M{x} {y} l35 -10', 'none','stroke="#fff1ca" stroke-width="3"'))
        o += [path('M40 342 Q310 190 657 297 L657 351 L40 390Z',f'url(#{p}glass)'),path('M20 340 Q190 154 680 292 Q410 252 20 355Z','#eef0db'),path('M20 350 Q369 267 680 292','none','stroke="#fff8dc" stroke-width="5"')]
        for x in range(60,650,24):
            yy=335-46*math.sin((x-40)/620*math.pi)
            o.append(path(f'M{x} {yy:.1f} V{386-(x-40)*.055:.1f}', 'none','stroke="#d1e0cd" stroke-width="2"'))
        for i in range(1,10):
            x=40+i*61
            o.append(path(f'M{x} {350-58*math.sin(i/10*math.pi):.1f} Q{160+i*37} {206+i*4} 680 292','none','stroke="#739a9e" stroke-width="1.5" opacity=".6"'))
        o += [path('M689 308 L697 159 H714 L729 308Z','#c4d5c8'),path('M683 158 H729 L738 137 H674Z','#24485b'),path('M671 134 H740 L727 122 H685Z','#f0e7c9'),path('M705 122 V98','none','stroke="#e9e6c8" stroke-width="2"')]
        for x,y,s in [(410,403,1.2),(615,351,.52)]:
            o.append(f'<g transform="translate({x} {y}) scale({s}) rotate(-12)">' + ellipse(0,18,95,10,'#223f4c','opacity=".25"') + path('M-95 0 Q-65 -7 -20 -5 L10 -58 H24 L9 -4 L81 -2 Q112 1 81 7 L7 9 L-22 46 H-36 L-22 8 L-75 7 L-91 22 H-102 L-91 5Z','#f5edda') + path('M-77 0 H82','none','stroke="#799fa5" stroke-width="2"') + path('M69 0 L79 -2 L86 1 L77 3Z','#24475d') + '</g>')
        o += [ellipse(252,111,95,23,'#e9ead8'),path('M157 111 Q252 137 347 111 Q270 148 190 128Z','#a1bbb6'),path('M164 105 L145 88 L181 94 M169 120 L153 139 L192 129','#cbd8c9'),rect(240,133,29,5,'#547880'),path('M180 107 Q250 93 326 109','none','stroke="#fff7de" stroke-width="2"')]
        o.append(path('M0 520 L180 478 L230 560 H0Z','#224e50'))
        for x in [10,45,80,115]: o.append(palm(x,550-x*.2,.55))
    else:
        for x,w,h in [(25,40,97),(83,28,143),(132,43,112),(194,29,176),(247,40,126),(313,34,95),(670,36,124),(728,40,161)]:
            o.append(tower(x,287,w,h,'#284b65'))
            for yy in range(290-h,279,14): o.append(rect(x+5,yy,w-10,2,'#edca8b','opacity=".6"'))
        o += [rect(0,290,800,270,f'url(#{p}water)'),ellipse(430,415,325,120,f'url(#{p}glow)'),path('M0 301 Q170 271 290 314 T585 310 T800 288','none','stroke="#6de0d1" stroke-width="3"'),path('M-20 560 Q0 402 244 374 Q482 351 625 279 L673 283 Q518 384 264 405 Q72 429 111 560Z','#132e3c'),path('M-20 560 Q0 402 244 374 Q482 351 625 279','none','stroke="#63eee3" stroke-width="4"'),path('M111 560 Q72 429 264 405 Q518 384 673 283','none','stroke="#cebb95" stroke-width="3"')]
        for x,y,s in [(160,399,.85),(298,375,.65),(438,347,.48),(548,311,.32)]:
            o += [path(f'M{x} {y} v{-38*s}','none',f'stroke="#d1c6a8" stroke-width="{2*s}"'),ellipse(x,y-38*s,4*s,3*s,'#ffe5a3'),ellipse(x,y-38*s,18*s,18*s,f'url(#{p}haze)')]
        o += [path('M482 277 V234 Q526 198 570 234 V277Z','#244656'),path('M467 236 Q525 154 585 236 Q525 214 467 236Z','#a8b8b3'),path('M482 236 H570','none','stroke="#efd59a" stroke-width="3"')]
        for x in [489,514,539,564]: o.append(rect(x,237,4,39,'#d1c6a6'))
        for i in range(180):
            x=rng.uniform(120,800); y=rng.uniform(319,560)
            o.append(ellipse(round(x,1),round(y,1),rng.choice([1,1.5,2.4]),.7,'#70ffe3',f'opacity="{rng.uniform(.2,.8):.2f}"'))
        o += [path('M421 458 Q518 479 581 440 M441 466 Q515 492 565 465','none','stroke="#4cebdc" stroke-width="2" opacity=".7"'),yacht(516,442,.50),palm(43,430,1.55,'#0b2935'),palm(755,364,1.35,'#0b2935')]
    if kind in ('marina','night-lagoon'):
        for i in range(80):
            x=rng.randrange(800); y=rng.randrange(330,560); w=rng.randrange(5,37)
            o.append(path(f'M{x} {y} h{w}', 'none',f'stroke="{"#83e7cf" if night else "#add6bf"}" stroke-width=".8" opacity=".2"'))
    o.append('</svg>')
    return '\n'.join('                        ' + line for line in minidom.parseString('\n'.join(o)).documentElement.toprettyxml(indent='    ').splitlines() if line.strip())


def main():
    artworks = {key: scene(key) for key in ('marina','boulevard','aerotropolis','night-lagoon')}
    for locale in ('en','hu'):
        file = ROOT / locale / 'nova-aurelia.html'
        html = file.read_text()
        for key, svg in artworks.items():
            pattern = rf'(<div class="city-district-media" data-city-svg="{key}">)\s*<svg\b.*?</svg>'
            html, count = re.subn(pattern, lambda m: m[1]+'\n'+svg, html, count=1, flags=re.S)
            if count != 1:
                raise ValueError(f'{file}: expected one {key} illustration')
        file.write_text(html)
        print(f'Updated {file.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
