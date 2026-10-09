#!/usr/bin/env python3
"""Builds the Seiko Alpinist Archive from the research JSON files.

  research/*.json  ->  data/models.json (normalised), assets/js/data.js,
                       index.html, watches/<id>.html (one tailored page per reference)

Run:  python3 tools/build.py
Every value that the research could not verify stays None and renders as "Unknown".
"""
import json, re, html, os, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import time
V = str(int(time.time()))
R = ROOT / 'research'
def load(name, default=None):
    p = R / name
    return json.loads(p.read_text()) if p.exists() else (default if default is not None else {})

vintage, sarb, prospex = load('vintage.json'), load('sarb.json'), load('prospex.json')
context, images = load('context.json'), load('images.json', {'images': []})
for extra in ('images_official2.json', 'images_cc.json', 'images_owner.json'):          # later photo passes
    images['images'] += load(extra, {'images': []}).get('images', [])
curation = load('curation.json')          # editorial decisions (series text, story overrides, image picks)

E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
def num(x):
    if x is None: return None
    if isinstance(x, (int, float)): return x
    m = re.search(r'-?\d+(?:\.\d+)?', str(x))
    return float(m.group()) if m else None
def clean_num(x):
    n = num(x)
    if n is None: return None
    return int(n) if float(n).is_integer() else n

CC_PAGES = {'6R15', '6R35', '6R54', '6R55', '6L35'}
CC_LIST = 'https://calibercorner.com/list-of-seiko-watch-movements'
def cc_url(cal):
    """Caliber Corner page for a calibre; falls back to its Seiko movement list when no page exists."""
    m = re.search(r'\b(\d[A-Z]\d{2})\b', str(cal or '').upper())
    return f"https://calibercorner.com/seiko-caliber-{m.group(1).lower()}/" if m and m.group(1) in CC_PAGES else CC_LIST

# ---------------------------------------------------------------- images
IMG = {i['id']: i for i in images.get('images', [])}
def img_rec(i, alt=None):
    if not i: return None
    if i.get('hotlink') or (i.get('url') and not i.get('file')):
        return {'src': i['url'], 'thumb': i['url'], 'alt': alt or i.get('alt') or i.get('subject'),
                'credit': i.get('credit') or '© Seiko Watch Corporation', 'source': i.get('source_page') or i.get('source_url'),
                'license': 'Official image, linked from Seiko' if 'seiko' in (i.get('credit') or '© Seiko').lower() else ('Owner photo, linked with credit' if 'photo:' in (i.get('credit') or '').lower() else 'Linked from the publisher with credit'), 'hotlink': True, 'transparent': i.get('transparent', True), 'caption': i.get('caption')}
    f = i.get('file'); f9 = i.get('file_900') or f
    return {'src': f, 'thumb': f9, 'alt': alt or i.get('alt') or i.get('subject'),
            'credit': f"{i.get('author') or 'Unknown author'}", 'source': i.get('source_url'),
            'license': i.get('license'), 'license_url': i.get('license_url'), 'hotlink': False,
            'caption': i.get('caption') or i.get('subject')}
def _rank(i):
    """Prefer Seiko's cut-out product shots, then openly licensed local photos, then dealer/press
    photos; small archived (Wayback) catalogue thumbnails come last."""
    cr, url = (i.get('credit') or '').lower(), i.get('url') or ''
    if 'web.archive.org' in url: return 3
    if url and 'seiko' in cr and 'via' not in cr and i.get('transparent', True): return 0
    if i.get('file'): return 1
    return 2
def watch_image(ref, alts=()):
    ref = (ref or '').upper()
    if not ref: return None
    keys = [ref] + [re.split(r'[\s(]', a.upper())[0] for a in alts if a]
    base = lambda r: re.sub(r'J1?$', '', r)
    hits = [i for i in images.get('images', []) if i.get('ref') and (i.get('kind') in (None, 'watches', 'official'))
            and any(base(i['ref'].upper()) == base(k) for k in keys)]
    if hits: return img_rec(sorted(hits, key=_rank)[0])
    for k in curation.get('watch_images', {}).get(ref, []):
        if k in IMG: return img_rec(IMG[k])
    return None

# ---------------------------------------------------------------- normalise models
def norm_model(m, era):
    mv, cs = m.get('movement') or {}, m.get('case') or {}
    ref = m.get('ref_primary') or m.get('id')
    t = (mv.get('type') or '').lower()
    mtype = 'quartz' if 'quartz' in t else 'automatic' if 'auto' in t else 'manual' if ('manual' in t or 'hand' in t or 'mechanical' in t) else None
    crystal = cs.get('crystal')
    ck = 'sapphire' if crystal and 'sapph' in crystal.lower() and 'sapphlex' not in crystal.lower() else 'acrylic' if crystal and 'acryl' in crystal.lower() else 'hardlex'
    dials = [d for d in (m.get('dial_colors') or []) if d]
    story = m.get('dial_story')
    if isinstance(story, str): story = {'text': story}
    lim = m.get('limited') or {}
    market = m.get('market')
    mk = (market or '').lower()
    jp_only = True if ('japan' in mk and ('only' in mk or 'domestic' in mk or 'jdm' in mk)) or mk.strip() in ('japan', 'japan (domestic)') else (False if mk and ('global' in mk or 'international' in mk or 'worldwide' in mk) else None)
    if jp_only is None and mk and ('us' in mk.split() or 'united states' in mk or 'usa' in mk): jp_only = False
    status = (m.get('status') or 'discontinued').split()[0].lower()
    if status not in ('current', 'limited', 'discontinued'): status = 'discontinued'
    if lim.get('is_limited') and status != 'current': status = 'limited' if status != 'discontinued' else 'discontinued'
    year = clean_num(m.get('year_intro'))
    msrp = m.get('msrp') or None
    msrp_label = None
    if msrp and msrp.get('amount'):
        cur = msrp.get('currency') or ''
        amt = msrp['amount']
        sym = {'USD': '$', 'JPY': '¥', 'EUR': '€', 'GBP': '£'}.get(cur, cur + ' ')
        msrp_label = f"{sym}{amt:,.0f}" if isinstance(amt, (int, float)) else f"{sym}{amt}"
        if msrp.get('year'): msrp_label += f" ({msrp['year']})"
        if msrp.get('note') and 'excl' in str(msrp.get('note')).lower(): msrp_label += ' excl. tax'
    return {
        'id': re.sub(r'[^a-z0-9-]', '', (m.get('id') or ref).lower().replace(' ', '-')),
        'name': m.get('name') or ref, 'nickname': clean_nick(m.get('nickname')), 'rawSeries': m.get('series'),
        'year': year, 'period': m.get('production_period'), 'era': era,
        'refs': {'primary': ref, 'jp': m.get('ref_jp'), 'intl': m.get('ref_intl'), 'us': m.get('ref_us')},
        'mv': {'cal': mv.get('caliber'), 'type': mtype, 'typeLabel': {'quartz': 'Quartz', 'automatic': 'Automatic', 'manual': 'Manual-wind'}.get(mtype, mv.get('type')),
               'jewels': clean_num(mv.get('jewels')), 'bph': clean_num(mv.get('bph')), 'pr': clean_num(mv.get('power_reserve_h')),
               'hack': mv.get('hacking'), 'wind': mv.get('hand_winding'), 'acc': mv.get('accuracy'), 'gmt': mv.get('gmt'), 'notes': mv.get('notes')},
        'cs': {'dia': clean_num(cs.get('diameter_mm')), 'thick': clean_num(cs.get('thickness_mm')), 'l2l': clean_num(cs.get('lug_to_lug_mm')),
               'lug': clean_num(cs.get('lug_width_mm')), 'mat': cs.get('material'), 'crystal': crystal, 'crystalKind': ck,
               'wr': cs.get('water_resistance'), 'back': cs.get('caseback'), 'crown': cs.get('crown')},
        'dials': dials, 'story': story, 'compass': m.get('compass') or {'has': False, 'type': None}, 'gmt': bool(m.get('gmt')),
        'strap': m.get('strap_bracelet'), 'market': market, 'jpOnly': jp_only,
        'msrp': msrp, 'msrpLabel': msrp_label, 'status': status,
        'limited': {'is': bool(lim.get('is_limited')), 'qty': clean_num(lim.get('quantity'))},
        'url': m.get('official_url'), 'design': m.get('design_notes') or [], 'notes': m.get('notes'),
        'sources': m.get('sources') or [], 'unc': m.get('uncertain_fields') or [],
    }

def clean_nick(n):
    if not n: return None
    n = re.sub(r'\s*\(.*?\)', '', str(n)).strip().strip("'\"‘’“”")
    return n if n and n[0].isupper() and len(n) < 32 else None

models = []
for era, src in (('vintage', vintage), ('sarb', sarb), ('prospex', prospex)):
    for m in src.get('models', []):
        models.append(norm_model(m, era))
seen = {}
for m in models:                      # de-duplicate by primary reference (later research wins)
    seen[m['refs']['primary'].upper()] = m
models = list(seen.values())
for k, ov in curation.get('model_overrides', {}).items():
    for m in models:
        if m['id'] == k or m['refs']['primary'].upper() == k.upper():
            for f, val in ov.items():
                if isinstance(val, dict) and isinstance(m.get(f), dict): m[f].update(val)
                else: m[f] = val

# ---------------------------------------------------------------- series
SERIES_RULES = curation.get('series', [])
def assign_series(m):
    ref = m['refs']['primary'].upper()
    for s in SERIES_RULES:
        if ref in [r.upper() for r in s.get('refs', [])]: return s['id']
        if s.get('match') and re.search(s['match'], ' '.join(str(x) for x in (ref, m['name'], m['rawSeries'] or '')), re.I): return s['id']
    return 'other'
series = {s['id']: dict(s, members=[]) for s in SERIES_RULES}
series.setdefault('other', {'id': 'other', 'name': 'Other Alpinist references', 'members': [], 'year': None})
for m in models:
    sid = assign_series(m)
    m['seriesId'] = sid
    m['seriesName'] = series[sid]['name']
    series[sid]['members'].append(m['id'])
for s in series.values():
    s['members'].sort(key=lambda i: next((m['year'] or 9999, m['refs']['primary']) for m in models if m['id'] == i))
    if s.get('year') is None and s['members']:
        s['year'] = min((m['year'] for m in models if m['id'] in s['members'] and m['year']), default=None)
series_list = sorted([s for s in series.values() if s['members']], key=lambda s: (s.get('year') or 9999, s.get('order', 0)))

# ---------------------------------------------------------------- colour themes & derived fields
PALETTES = curation.get('palettes', {})
def color_key(m):
    if m.get('colorKey'): return m['colorKey']
    d = ' '.join(m['dials']).lower()
    for k in ['purple', 'teal', 'green', 'blue', 'brown', 'black', 'cream', 'white', 'grey', 'gray', 'silver', 'red', 'beige', 'ivory']:
        if k in d: return {'gray': 'grey', 'ivory': 'cream', 'beige': 'cream', 'white': 'cream'}.get(k, k)
    return 'unknown'
for m in models:
    m['colorKey'] = color_key(m)
    m['decade'] = f"{(m['year'] // 10) * 10}s" if m['year'] else 'Unknown'
    d = m['cs']['dia']
    m['sizeBand'] = 'Unknown' if not d else ('< 38 mm' if d < 38 else '38–39 mm' if d < 39.5 else '39.5–40 mm' if d <= 40 else '> 40 mm')
    m['prospex'] = bool(re.search('prospex', ' '.join([m['name'], m['rawSeries'] or '', m['seriesName']]), re.I)) and m['era'] == 'prospex'
    m['historical'] = m['era'] == 'vintage'
    m['statusLabel'] = {'current': 'Current production', 'limited': 'Limited edition', 'discontinued': 'Discontinued'}[m['status']]
    m['img'] = m.get('img') or watch_image(m['refs']['primary'], [m['refs'].get('jp'), m['refs'].get('intl'), m['refs'].get('us')])
    m['theme'] = PALETTES.get(m['colorKey'], PALETTES.get('green', {}))
    m['schem'] = dict(curation.get('schematics', {}).get(m['seriesId'], {}), **({'dial': m['theme'].get('dial')} if m['theme'].get('dial') else {}))

# ---------------------------------------------------------------- landscapes
def landscape_for(m):
    over = curation.get('landscape_by_ref', {}).get(m['refs']['primary'].upper())
    if over: return over
    story = m.get('story') or {}
    kind = (story.get('landscape_kind') or '').lower()
    for k, v in curation.get('landscape_by_kind', {}).items():
        if k in kind: return dict(v, stated=True)
    v = curation.get('landscape_by_color', {}).get(m['colorKey']) or curation.get('landscape_default')
    return dict(v, stated=False) if v else None

# ---------------------------------------------------------------- mountains
mountains = []
for mt in context.get('mountains', []):
    key = curation.get('mountain_images', {}).get(mt['name_en'])
    mountains.append({
        'name': mt['name_en'], 'short': curation.get('mountain_short', {}).get(mt['name_en'], mt['name_en'].replace('Mount ', 'Mt ')),
        'jp': mt.get('name_jp'), 'romaji': mt.get('romaji'), 'elev': clean_num(mt.get('elevation_m')),
        'lat': mt['lat'], 'lon': mt['lon'], 'pref': mt.get('prefecture'), 'range': mt.get('range'),
        'labelDx': curation.get('mountain_labels', {}).get(mt['name_en'], [8, 3])[0], 'labelDy': curation.get('mountain_labels', {}).get(mt['name_en'], [8, 3])[1],
        'facts': [{'text': f['text'], 'src': f.get('source'), 'seiko': f.get('category') == 'seiko-documented'} for f in mt.get('facts', []) if f.get('verified', True)],
        'img': (lambda r: r and {'src': r['thumb'], 'alt': r['alt'], 'credit': r['credit'], 'license': r['license'], 'source': r['source']})(img_rec(IMG.get(key))) if key else None,
    })

# ---------------------------------------------------------------- movements (chain)
mv_chain = curation.get('movement_chain', [])
mv_index = {}
for src in (vintage, sarb, prospex):
    for c in src.get('movements', []):
        mv_index[str(c.get('caliber'))] = c
for c in mv_chain:
    c['cc'] = cc_url(c['key'])
    r = mv_index.get(c['key'], {})
    c.setdefault('type', r.get('type'))
    for a, b in (('jewels', 'jewels'), ('bph', 'bph'), ('pr', 'power_reserve_h'), ('hack', 'hacking'), ('wind', 'hand_winding'), ('acc', 'accuracy')):
        if c.get(a) is None: c[a] = r.get(b)
    if not c.get('src'):
        s = r.get('sources') or []
        c['src'] = (s[0] if isinstance(s[0], str) else s[0].get('url')) if s else r.get('source')
    if c.get('img') in IMG:
        ir = img_rec(IMG[c['img']]); c['img'] = {'src': ir['src'], 'alt': ir['alt'], 'credit': ir['credit']}
    else: c.pop('img', None)

# ---------------------------------------------------------------- archive
archive = []
for a in curation.get('archive', []):
    i = IMG.get(a['img'])
    if not i: continue
    r = img_rec(i)
    archive.append({'title': a['title'], 'kind': a['kind'], 'date': a.get('date'), 'src': r['src'], 'alt': r['alt'], 'caption': a.get('caption') or r['caption'],
                    'credit': r['credit'], 'source': r['source'], 'license': r['license'], 'hotlink': r['hotlink']})

# ---------------------------------------------------------------- tree
tree = curation.get('tree', {'nodes': [], 'edges': [], 'eras': [], 'cols': 1, 'rows': 1})
for n in tree['nodes']:
    if n.get('series') and n['series'] in series and series[n['series']]['members']:
        n['href'] = f"#tl-{n['series']}"
    n.setdefault('href', '#timeline')

DATA = {'models': models, 'series': [{k: s.get(k) for k in ('id', 'name', 'year', 'era', 'kicker', 'blurb', 'dispute', 'lead', 'members')} for s in series_list],
        'mountains': mountains, 'movements': mv_chain, 'evolution': curation.get('evolution', []), 'tree': tree, 'archive': archive,
        'compareDefault': curation.get('compare_default', [])}
(ROOT / 'data').mkdir(exist_ok=True)
(ROOT / 'data' / 'models.json').write_text(json.dumps(models, ensure_ascii=False, indent=1))
SEARCH = [{'id': m['id'], 'ref': m['refs']['primary'], 'nick': m['nickname'], 'series': m['seriesName'], 'year': m['year'], 'cal': m['mv']['cal'],
           'status': m['status'], 'dialHex': (PALETTES.get(m['colorKey']) or {}).get('dial', '#333'),
           'hay': ' '.join(str(x) for x in [m['refs']['primary'], m['refs'].get('jp'), m['refs'].get('us'), m['nickname'], m['seriesName'], m['year'], m['mv']['cal'], m['colorKey'], ' '.join(m['dials']), m['market'], 'gmt' if m['gmt'] else '', 'limited' if m['limited']['is'] else '', m['name']] if x).lower()}
          for m in models]
(ROOT / 'assets' / 'js' / 'search-index.js').write_text('window.ALP_SEARCH=' + json.dumps(SEARCH, ensure_ascii=False, separators=(',', ':')) + ';')
(ROOT / 'assets' / 'js' / 'data.js').write_text('window.ALP=' + json.dumps(DATA, ensure_ascii=False, separators=(',', ':')) + ';')

# ================================================================ HTML
HEAD_FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Shippori+Mincho:wght@400;500;600&family=Zen+Kaku+Gothic+New:wght@400;500&display=swap" rel="stylesheet">'
SITE = 'https://retrocherry.github.io/seiko-alpinist-archive/'
def head(title, desc, base='', extra='', path=''):
    og = f'''<link rel="canonical" href="{SITE}{path}"><meta property="og:type" content="website"><meta property="og:site_name" content="Seiko Alpinist Archive">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}assets/img/brand/og-card.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Alpinist wordmark and the words Built for the Mountains beside an Alpinist watch in a compass ring, over Mount Yari">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{SITE}assets/img/brand/og-card.jpg">'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta name="theme-color" content="#0f211a">{og}
<link rel="icon" href="{base}favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="32x32" href="{base}assets/img/brand/favicon-32.png"><link rel="icon" type="image/png" sizes="512x512" href="{base}assets/img/brand/favicon-512.png"><link rel="apple-touch-icon" href="{base}assets/img/brand/apple-touch-icon.png">
{HEAD_FONTS}<link rel="stylesheet" href="{base}assets/css/style.css?v={V}">{extra}</head>'''

ALP_LOGO = (ROOT / 'assets/img/brand/alpinist-logo.svg').read_text()
PROSPEX_LOGO = (ROOT / 'assets/img/brand/prospex-logo.svg').read_text()
def nav(base='', links=True):
    items = [('origins', 'Origins'), ('map', 'Map'), ('timeline', 'Timeline'), ('family', 'Lineage'), ('models', 'Models'), ('compare', 'Compare'), ('compass', 'Compass'), ('sources', 'Sources')]
    lis = ''.join(f'<li><a href="{base}index.html#{a}" >{b}</a></li>' if base else f'<li><a href="#{a}">{b}</a></li>' for a, b in items)
    return f'''<header class="nav" role="banner"><a class="logo" href="{base}index.html" aria-label="Alpinist Archive — home">
<span class="alp-logo">{ALP_LOGO}</span></a>
<nav aria-label="Primary"><ul>{lis}</ul></nav>
<div style="display:flex;gap:10px;align-items:center"><button class="sound" data-search type="button" aria-label="Search the archive" title="Search ( / )"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg><span class="lbl">Search</span><kbd>/</kbd></button>
<button class="menu-btn" aria-expanded="false" aria-controls="primary-menu">Menu</button></div></header>'''

_lg = (ROOT / 'assets/img/brand/seiko-logo.svg').read_text()
SEIKO_LOGO = re.sub(r'<\?xml.*?\?>|<!--.*?-->', '', _lg, flags=re.S).strip()
SEIKO_LOGO = re.sub(r'<svg[^>]*>', '<svg viewBox="0 0 500 98.4" xmlns="http://www.w3.org/2000/svg" fill="currentColor" aria-hidden="true">', SEIKO_LOGO, count=1)
def footer(base=''):
    return f'''<footer class="foot" role="contentinfo"><div class="wrap">
<div class="disc"><figure class="wordmark"><div class="marks"><span class="mk seiko" role="img" aria-label="SEIKO logo">{SEIKO_LOGO}</span><span class="mk prospex" role="img" aria-label="Prospex logo">{PROSPEX_LOGO}</span><span class="mk alp" role="img" aria-label="Alpinist logo">{ALP_LOGO}</span></div><figcaption>SEIKO, PROSPEX and ALPINIST are trademarks of Seiko Group Corporation. SEIKO logo via <a href="https://commons.wikimedia.org/wiki/File:Seiko_logo.svg" target="_blank" rel="noopener">Wikimedia Commons</a>; Prospex and Alpinist logos from Seiko’s Alpinist page.</figcaption></figure>
<div><p class="mono" style="color:var(--gold);margin-bottom:8px">Independent fan archive · Not affiliated with Seiko</p>
<p>This is an independent, non-commercial educational archive. It is <strong>not affiliated with, endorsed by, sponsored by or connected to Seiko Group Corporation, Seiko Watch Corporation</strong> or any of their subsidiaries or retailers. SEIKO, PROSPEX, ALPINIST and related names are trademarks of Seiko Group Corporation, used here only to identify the products discussed. Official product photographs are © Seiko Watch Corporation and are linked from Seiko’s own website with credit; all other photographs are credited to their authors under the licences shown. Specifications were researched from Seiko and reputable published sources; where sources disagree or a fact could not be verified it is marked <em>Unknown</em> or <em>Unconfirmed</em>. Nothing here is an offer to sell.</p></div></div>
<p class="mono" style="margin-top:26px;font-size:.6rem;opacity:.7">Map contours are a stylised illustration, not survey data · <a href="{base}index.html#sources">Sources &amp; further reading</a></p>
<div class="byline"><span>Website by <a href="https://gabesilverstein.com" target="_blank" rel="noopener">Gabe Silverstein</a></span>
<a class="kofi" href="https://ko-fi.com/gabesilverstein" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h13v6.5A4.5 4.5 0 0 1 12.5 19h-4A4.5 4.5 0 0 1 4 14.5z" fill="currentColor"/><path d="M17 9.5h1.6a2.4 2.4 0 0 1 0 4.8H17" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10.5 15.6l-2.2-2.1a1.3 1.3 0 0 1 1.9-1.8l.3.3.3-.3a1.3 1.3 0 0 1 1.9 1.8z" fill="#b3302b"/></svg>Support on Ko-fi</a></div>
</div></footer>'''

SCRIPTS = lambda base, extra='': (f'<script src="{base}assets/js/icons.js"></script><script src="{base}assets/js/watchsvg.js"></script><script src="{base}assets/js/search-index.js"></script><script src="{base}assets/js/search.js" defer></script>{extra}').replace('.js"', '.js?v=' + V + '"')

def spec_rows(m):
    """Case, dial and market facts only. Movement facts live in the movement panel; status and
    limited quantity live in the hero — each fact appears once on the page."""
    cs = m['cs']
    rows = [
        ('watch', 'Official name', m['name']),
        ('dia', 'Case diameter', f"{cs['dia']} mm" if cs['dia'] else None), ('thick', 'Thickness', f"{cs['thick']} mm" if cs['thick'] else None),
        ('lug', 'Lug-to-lug', f"{cs['l2l']} mm" if cs['l2l'] else None), ('strap', 'Lug width', f"{cs['lug']} mm" if cs['lug'] else None),
        ('watch', 'Case material', cs['mat']), (cs['crystalKind'], 'Crystal', cs['crystal']), ('water', 'Water resistance', cs['wr']),
        ('screwdown', 'Crown', cs['crown']), ('caseback', 'Caseback', cs['back']),
        ('compassbezel', 'Compass', (m['compass'].get('type') or 'Yes') if m['compass'].get('has') else 'None'),
        ('date', 'Dial', ', '.join(m['dials']) or None), ('strap', 'Strap / bracelet', m['strap']),
        ('global' if m['jpOnly'] is False else 'jp', 'Market', m['market']), ('date', 'Production period', m['period']),
        ('date', 'Launch price', m['msrpLabel']),
    ]
    return rows

def mv_rows(m):
    mv = m['mv']
    yn = lambda x: 'Yes' if x is True else 'No' if x is False else None
    return [('Type', mv['typeLabel']), ('Jewels', mv['jewels']), ('Frequency', f"{mv['bph']:,} vph" if mv['bph'] else None),
            ('Power reserve', f"{mv['pr']} h" if mv['pr'] else None), ('Hacking', yn(mv['hack'])), ('Hand-winding', yn(mv['wind'])),
            ('GMT', 'Yes' if m['gmt'] else 'No'), ('Accuracy', mv['acc'])]
UNK = '<span class="unk">Unknown</span>'
def val(x): return UNK if x in (None, '', []) else E(x)

def feature_icons(m):
    f = []
    t = m['mv']['type']
    if t == 'automatic': f.append(('automatic', 'Automatic'))
    if t == 'quartz': f.append(('quartz', 'Quartz'))
    if m['mv']['wind']: f.append(('manual', 'Hand-winding'))
    if m['mv']['hack']: f.append(('hacking', 'Hacking seconds'))
    if m['gmt']: f.append(('gmt', 'GMT'))
    if m['compass'].get('has'): f.append(('compassbezel', 'Compass ring' if 'inner' in str(m['compass'].get('type', '')).lower() or 'internal' in str(m['compass'].get('type', '')).lower() else 'Compass bezel'))
    ck = m['cs']['crystalKind']
    if m['cs']['crystal']: f.append((ck, {'sapphire': 'Sapphire crystal', 'acrylic': 'Acrylic crystal', 'hardlex': 'Hardlex / mineral'}[ck]))
    if m['cs']['crown'] and 'screw' in m['cs']['crown'].lower(): f.append(('screwdown', 'Screw-down crown'))
    if m['cs']['back'] and ('see-through' in m['cs']['back'].lower() or 'exhibition' in m['cs']['back'].lower() or 'display' in m['cs']['back'].lower()): f.append(('caseback', 'Exhibition caseback'))
    if any('lumibrite' in str(x).lower() for x in m['design'] + [m['notes'] or '']): f.append(('lume', 'LumiBrite'))
    wr = m['cs']['wr'] or ''
    if re.search(r'\d+\s*(m|bar)', wr): f.append(('water', re.split(r'[;(（]', wr)[0].strip()[:26]))
    if any('date' in str(x).lower() for x in m['design']) or (m['cs'].get('crystal') and 'cyclops' in str(m['design']).lower()): f.append(('date', 'Date'))
    if 'cyclops' in json.dumps(m['design']).lower() or 'magnif' in json.dumps(m['design']).lower(): f.append(('cyclops', 'Date magnifier'))
    if m['limited']['is']: f.append(('limited', 'Limited edition'))
    if m['jpOnly']: f.append(('jp', 'Japan market'))
    elif m['jpOnly'] is False: f.append(('global', 'International'))
    return f

def link_out(m):
    if m['status'] == 'current' and m.get('url'):
        return f'<a class="btn fill" href="{E(m["url"])}" target="_blank" rel="noopener">View on Seiko →</a>'
    s = next((x for x in m['sources'] if isinstance(x, dict) and x.get('tier') == 'official'), None) or (m['sources'][0] if m['sources'] else None)
    if s:
        u = s['url'] if isinstance(s, dict) else s
        return f'<a class="btn" href="{E(u)}" target="_blank" rel="noopener">Find reference information →</a>'
    return ''

# ---------------------------------------------------------------- watch pages
by_id = {m['id']: m for m in models}
chron = sorted(models, key=lambda m: (m['year'] or 9999, m['refs']['primary']))
(ROOT / 'watches').mkdir(exist_ok=True)
for m in models:
    th = m['theme'] or {}
    land = landscape_for(m)
    limg = img_rec(IMG.get(land['img'])) if land and land.get('img') in IMG else None
    s = series[m['seriesId']]
    sib = [by_id[i] for i in s['members'] if i != m['id']]
    idx = chron.index(m)
    prev, nxt = (chron[idx - 1] if idx > 0 else None), (chron[idx + 1] if idx < len(chron) - 1 else None)
    refs = m['refs']; primary = refs['primary']
    alt_refs = [(k, refs[k]) for k in ('jp', 'intl', 'us') if refs.get(k) and refs[k].upper() != primary.upper()]
    ref_dl = ''.join(f'<dt>{ {"jp": "Japan", "intl": "International", "us": "USA"}[k]}</dt><dd>{E(r)}</dd>' for k, r in alt_refs)
    status_html = {'current': '<span class="status-big cur">● CURRENT PRODUCTION</span>', 'discontinued': '<span class="status-big dis">○ DISCONTINUED</span>',
                   'limited': '<span class="status-big lim">◆ LIMITED EDITION</span>'}[m['status']]
    if m['limited']['is'] and m['status'] != 'limited': status_html += ' <span class="status-big lim">◆ LIMITED EDITION</span>'
    qty = f'<p class="mono" style="color:var(--gold)">1 of {m["limited"]["qty"]:,} produced</p>' if m['limited']['qty'] else ('<p class="mono" style="color:var(--gold)">Limited — quantity unconfirmed</p>' if m['limited']['is'] else '')
    story = m.get('story') or {}
    if story.get('text'):
        su = (story.get('source_url') or story.get('url') or '').lower()
        official = story.get('verified_official') is not False and 'seiko' in su.split('/')[2 if su.startswith('http') else 0] if su else False
        official = official or ('web.archive.org' in su and 'seikowatches.com' in su)
        label = 'Seiko’s description' if official else 'Published description from the watch press or retailers — not found on a Seiko-hosted page'
        story_html = f'''<p class="lead-q">{E(story["text"])}</p><p class="mono src-line">{label}{(" · <a href='" + E(story.get("source_url") or story.get("url") or "") + "' target='_blank' rel='noopener'>source ↗</a>") if (story.get("source_url") or story.get("url")) else ""}</p>'''
    else:
        story_html = '<p class="lead-q muted">Seiko has not published a colour or landscape story for this reference. The landscape above is an atmosphere image of the Japanese mountains, not a stated inspiration.</p>'
    if limg:
        su0 = ((m.get('story') or {}).get('source_url') or '').lower()
        unoff = (m.get('story') or {}).get('verified_official') is False or not ('seikowatches.com' in su0 or 'seiko-watch' in su0)
        honesty = ('Representative landscape matching the published description' if unoff else 'Representative landscape matching Seiko’s description') if land.get('stated') and not land.get('named') else ('A place named in Seiko’s description' if land.get('named') else 'Atmosphere image — not a Seiko-stated inspiration')
        land_cap = f'{E(limg["caption"])} · <em>{honesty}</em> · Photo: {E(limg["credit"])} · <a href="{E(limg["source"])}" target="_blank" rel="noopener">{E(limg["license"])}</a>'
    else:
        land_cap = ''
    wimg = m['img']
    if wimg:
        wsrc = wimg["src"] if wimg.get("hotlink") else "../" + wimg["src"]
        watch_html = f'<img class="{'cut' if wimg.get('hotlink') and wimg.get('transparent', True) else 'ph'}" src="{E(wsrc)}" alt="{E(wimg["alt"] or m["name"])}" fetchpriority="high" {"referrerpolicy=" + chr(34) + "no-referrer" + chr(34) if wimg.get("hotlink") else ""} onerror="this.outerHTML=window.renderWatch(window.SCHEM)+\'<p class=&quot;credit&quot;>Schematic illustration — official image unavailable</p>\'">'
        watch_cap = f'<p class="credit">{E(wimg["credit"])}{" · " + E(wimg["license"]) if wimg.get("license") else ""}{" · <a href=" + chr(34) + E(wimg["source"]) + chr(34) + " target=_blank rel=noopener>source ↗</a>" if wimg.get("source") else ""}</p>'
    else:
        watch_html = '<div class="schem-host" data-schem></div>'
        watch_cap = '<p class="credit">Schematic illustration — no licensed photograph of this reference located. Not a photograph.</p>'
    css_vars = ';'.join(f'--t-{k}:{v}' for k, v in th.items())
    feats = feature_icons(m)
    page = head(f"{primary}{' “' + m['nickname'] + '”' if m['nickname'] else ''} · Seiko Alpinist Archive",
                f"{m['name']} ({primary}) — history, specifications, movement and sources. Independent archive, not affiliated with Seiko.", '../',
                f'<link rel="preload" as="image" href="../{E(limg["src"])}">' if limg else '', f"watches/{m['id']}.html")
    page += f'''<body class="watch-page" data-base="../" style="{css_vars}"><a class="skip" href="#main">Skip to content</a>{nav("../")}
<main id="main">
<section class="w-hero" aria-labelledby="w-title">
  {f'<div class="w-land"><img src="../{E(limg["src"])}" alt="{E(limg["alt"])}"></div>' if limg else '<div class="w-land none"></div>'}
  <div class="w-veil"></div>
  <div class="wrap w-hero-in">
    <div class="w-text">
      <h1 id="w-title">{E(m['nickname']) if m['nickname'] else E(primary)}</h1>
      {f'<p class="w-ref">{E(primary)}</p>' if m['nickname'] else ''}
      <p class="mono kick"><a href="../index.html#tl-{E(s['id'])}">{E(s['name'])}</a> · {m['year'] or 'Year unknown'}</p>
      {f'<dl class="refs">{ref_dl}</dl>' if ref_dl else ''}
      <div class="w-status">{status_html}</div>{qty}
    </div>
    <figure class="w-watch">{watch_html}<figcaption>{watch_cap}</figcaption></figure>
  </div>
  {f'<p class="w-landcap">{land_cap}</p>' if land_cap else ''}
</section>
<section class="w-story wrap"><div class="w-story-in">{story_html}
</div></div></section>
<section class="w-body"><div class="wrap mp-cols">
<div>
<h2 class="sub-h">Specifications</h2>
<table class="spec-table"><caption class="vh">Specifications of {E(primary)}</caption><tbody>
{''.join(f'<tr><th scope="row">{{ICO:{i}}}{E(l)}</th><td>{val(v)}</td></tr>' for i, l, v in spec_rows(m))}
</tbody></table>
{('<h2 class="sub-h">Design notes</h2><ul class="dn">' + ''.join(f'<li>{E(d)}</li>' for d in m['design']) + '</ul>') if m['design'] else ''}
{('<div class="note-box"><strong>Unverified or disputed:</strong> ' + E(', '.join(str(u) for u in m['unc'])) + '</div>') if m['unc'] else ''}
</div>
<aside>
<h2 class="sub-h">Movement</h2>
<div class="mvbox" data-cal="{E(m['mv']['cal'] or '')}"><div class="mv-mini" aria-hidden="true"></div>
<div><p class="mono" style="color:var(--gold)">Calibre</p><p class="mvcal">{f'<a href="{cc_url(m["mv"]["cal"])}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none">{E(m["mv"]["cal"])}</a>' if m['mv']['cal'] else UNK}</p>
<dl class="mvdl">{''.join(f'<dt>{k}</dt><dd>{val(v)}</dd>' for k, v in mv_rows(m))}</dl>
<a class="mono small" href="{cc_url(m['mv']['cal'])}" target="_blank" rel="noopener">{'Calibre ' + E(m['mv']['cal']) + ' on Caliber Corner' if cc_url(m['mv']['cal']) != CC_LIST else 'Seiko calibres on Caliber Corner'} ↗</a></div></div>
<div class="out">{link_out(m)}</div>
<h2 class="sub-h">Sources</h2><ul class="src-list">{''.join(f'<li><span class="t">{E(x.get("tier", "") if isinstance(x, dict) else "")}</span><a href="{E(x["url"] if isinstance(x, dict) else x)}" target="_blank" rel="noopener">{E(x.get("title") or x["url"] if isinstance(x, dict) else x)}</a></li>' for x in m['sources']) or '<li>No sources recorded.</li>'}</ul>
</aside></div></section>
{f"""<section class="w-family"><div class="wrap"><h2 class="sub-h">Also in the {E(s['name'])}</h2>
<div class="sib">{''.join(f'<a class="sibc" href="{o["id"]}.html" style="--sw:{(o["theme"] or {}).get("dial", "#333")}"><span class="sw"></span><span class="mono">{E(o["refs"]["primary"])}</span><span>{E(o["nickname"] or ", ".join(o["dials"][:1]) or "")}</span><span class="small muted">{o["year"] or ""}</span></a>' for o in sib)}</div></div></section>""" if sib else ''}
<nav class="w-pn wrap" aria-label="Chronological navigation">{f'<a href="{prev["id"]}.html">← {E(prev["refs"]["primary"])}<small>{prev["year"] or ""}</small></a>' if prev else '<span></span>'}<a href="../index.html#models" class="mono">All models</a>{f'<a href="{nxt["id"]}.html" style="text-align:right">{E(nxt["refs"]["primary"])} →<small>{nxt["year"] or ""}</small></a>' if nxt else '<span></span>'}</nav>
</main>{footer("../")}
<script>window.SCHEM={json.dumps(m["schem"])};</script>{SCRIPTS("../", '<script src="../assets/js/watch.js"></script>')}
</body></html>'''
    (ROOT / 'watches' / f"{m['id']}.html").write_text(re.sub(r'\{ICO:([a-z]+)\}', r'<i class="i" data-ico="\1"></i>', page))

# ---------------------------------------------------------------- index
tmpl = (ROOT / 'tools' / 'index.template.html').read_text()
ctx_facts = context.get('context_facts', [])
def fact_li(f):
    cat = f.get('category')
    badge = '<span class="badge sk">Seiko-documented</span>' if cat == 'seiko-documented' else '<span class="badge ctx">Japanese context</span>' if cat == 'japanese-context' else '<span class="badge ctx">Third-party</span>'
    src = (f.get('sources') or [None])[0]
    return f'<li><span class="y">{E(curation.get("context_years", {}).get(f.get("id"), ""))}</span><div>{badge}{E(f.get("claim") or f.get("text"))}{f"<small><a href={chr(34)}{E(src)}{chr(34)} target=_blank rel=noopener>source ↗</a></small>" if src else ""}</div></li>'
order = curation.get('context_order') or [f.get('id') for f in ctx_facts]
facts_html = ''.join(fact_li(f) for k in order for f in ctx_facts if f.get('id') == k and f.get('verified', True))
srcs = []
seenu = set()
for f in context.get('further_reading', []) + curation.get('extra_sources', []):
    if f['url'] not in seenu: seenu.add(f['url']); srcs.append(f)
for m in models:
    for x in m['sources']:
        if isinstance(x, dict) and x['url'] not in seenu: seenu.add(x['url']); srcs.append({'title': x.get('title') or x['url'], 'url': x['url'], 'tier': x.get('tier')})
tiers = {'official': 'Seiko official', 'press': 'Watch press', 'database': 'Databases & references', 'forum': 'Collector sources', None: 'Further reading'}
src_html = ''
for t, label in tiers.items():
    items = [s for s in srcs if s.get('tier') == t]
    if items:
        src_html += f'<h3 class="sub-h">{label}</h3><ul class="src-list src-cols">' + ''.join(f'<li><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["title"])}</a></li>' for s in items) + '</ul>'
link = context.get('alpinist_mountain_link', {})
repl = {
    '{{NAV}}': nav(), '{{FOOTER}}': footer(), '{{HEAD}}': head('Seiko Alpinist Archive — Built for the Mountains', 'An independent interactive museum and field guide to the Seiko Alpinist, 1959 to today.', '', '<link rel="preload" as="image" href="' + E(curation.get('hero', {}).get('bg', '')) + '">'),
    '{{FACTS}}': facts_html, '{{SOURCES}}': src_html, '{{LINK_NOTE}}': E(link.get('summary', '')),
    '{{COUNT}}': str(len(models)), '{{SERIES_COUNT}}': str(len(series_list)), '{{SCRIPTS}}': SCRIPTS('', '<script src="assets/js/mapdata.js"></script><script src="assets/js/data.js"></script><script src="assets/js/app.js" defer></script><script src="assets/js/compass.js" defer></script>'),
}
for k, v in curation.get('hero', {}).items():
    repl['{{HERO_' + k.upper() + '}}'] = E(v)
for k, v in repl.items(): tmpl = tmpl.replace(k, v)
(ROOT / 'index.html').write_text(tmpl)
print(f'Built {len(models)} watch pages, {len(series_list)} series, {len(mountains)} mountains, {len(archive)} archive items.')
for s in series_list: print('  ', s['id'], s['year'], [by_id[i]['refs']['primary'] for i in s['members']])
