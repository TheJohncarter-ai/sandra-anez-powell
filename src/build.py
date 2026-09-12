"""Build Sandra Añez Powell's site.

  python build.py --artifact out.html                 single-file version, images inlined
  python build.py --deploy DIR --url https://.../     static site: index.html + img/ + sitemap
Options: --img DIR (source .webp folder, default ./img next to this script)
"""
import argparse, base64, json, html, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))

COLLS = {
    'all':     dict(name='All work', gloss='', intro='Every collection in one hang. Choose a collection to see it on its own; click any painting to step closer.', color=None),
    'sailing': dict(name='Sailing', gloss='Majesty of the Bay', intro='Regattas, harbor moons and boats at rest — the Chesapeake as Sandra sees it from Annapolis.', color='#2E5FA3'),
    'water':   dict(name='In the Water', gloss='Majesty of the Bay', intro='Below the surface: jellyfish drifting through the chop, painted the way they move.', color='#2A9D9A'),
    'jugando': dict(name='Jugando', gloss='“at play”', intro='Poured, flicked and dripped paint where color takes the wheel entirely.', color='#E29A1F'),
    'campo':   dict(name='Mi gente de campo', gloss='“my country people”', intro='Portraits in homage to country people — wide straw hats, warm ochres, steady eyes.', color='#8E5604'),
    'divina':  dict(name='Divina', gloss='“divine”', intro='Women painted as monuments: bold outlines, red dresses, stained-glass color.', color='#C0507F'),
    'floral':  dict(name='Floral', gloss='', intro='Blossoms at the scale of a window — poppy, hibiscus, orchid.', color='#3E8A5A'),
    'reflect': dict(name='Reflections', gloss='', intro='Quieter rooms and still lifes — canal light, a fireplace, a teapot in the mirror.', color='#7B5EA7'),
    'private': dict(name='In private collections', gloss='', intro='Originals that now live with collectors. Fine-art prints of each are still available.', color='#596172'),
}
# One track per part of the site. Files live in ./audio, re-encoded mono ~88kbps.
# Only shipped with the deployed site: the artifact viewer can't load audio files.
MUSIC = {
    'sail':      dict(file='sail.web.mp3',      title='Shores of Avalon',  by='Kevin MacLeod', lic='CC BY 4.0'),
    'portraits': dict(file='portraits.web.mp3', title='Nacional Joropo',   by='Lionel Belasco Orchestra', lic='public domain'),
    'workshops': dict(file='workshops.web.mp3', title='Lobby Time',        by='Kevin MacLeod', lic='CC BY 4.0'),
    'night':     dict(file='night.web.mp3',     title='Evening Fall (Harp)', by='Kevin MacLeod', lic='CC BY 4.0'),
}

PRINTS = ('prints', 'Prints available')
ASK = ('ask', 'Original available — ask Sandra')
SOLD = ('sold', 'Original sold · prints available')

# (img, w, h, collection, title, status, alt)
P = [
 ('s_regatta', 860, 822, 'sailing', 'Regatta at Golden Hour', PRINTS, 'Acrylic painting: six sailboats race beneath a blazing gold sun, orange sky over pink and violet water'),
 ('s_violet', 860, 650, 'sailing', 'Violet Fleet', PRINTS, 'Acrylic painting: purple-sailed boats scattered across speckled blue and yellow water'),
 ('s_fire', 649, 860, 'sailing', 'Fire on the Water', PRINTS, 'Acrylic painting: sailboats with red, pink and orange sails on speckled blue water'),
 ('s_emerald', 818, 860, 'sailing', 'Emerald Sails', PRINTS, 'Acrylic painting: green sails beneath swirling red, green and blue orbs in a yellow sky'),
 ('s_moonlight', 654, 860, 'sailing', 'Moonlight Sail', PRINTS, 'Acrylic painting: a lone sailboat on deep blue water beneath a huge swirling yellow moon'),
 ('d10_0', 769, 377, 'sailing', 'Majesty of the Bay No. 1', ASK, 'Acrylic painting: colorful waterfront cottages beside a blue bay under a golden full moon and red sky'),
 ('d10_2', 427, 325, 'sailing', 'Majesty of the Bay No. 2', ASK, 'Acrylic painting: a line of white sails on turquoise water, reflections streaked with gold'),
 ('d11_1', 707, 274, 'sailing', 'Majesty of the Bay No. 3', ASK, 'Acrylic painting: an orange-sailed and a gold-sailed boat cross a wide band of blue water'),
 ('d10_7', 589, 447, 'sailing', 'Majesty of the Bay No. 4', ASK, 'Acrylic painting: three rowboats drawn together on choppy blue water'),
 ('d11_0', 741, 533, 'sailing', 'Majesty of the Bay No. 5', ASK, 'Acrylic painting: a red-sailed boat off a wooded shore, white-capped waves rolling onto the beach'),
 ('d11_4', 651, 451, 'water', 'In the Water No. 1', ASK, 'Acrylic painting: a translucent jellyfish trailing flowered tendrils across a marigold ground'),
 ('d11_6', 451, 651, 'water', 'In the Water No. 2', ASK, 'Acrylic painting: pale jellyfish drifting through deep blue water lit from above'),
 ('s_orbit', 860, 651, 'jugando', 'In Orbit', PRINTS, 'Acrylic abstract: overlapping green, purple and blue circles over magenta, gold and turquoise bands'),
 ('d02_0', 905, 724, 'jugando', 'Jugando No. 1', ASK, 'Acrylic abstract: dense drips and flicks of green, pink, blue and white over a dark ground'),
 ('d02_1', 757, 1032, 'jugando', 'Jugando No. 2', ASK, 'Acrylic abstract: vertical pours of yellow, magenta and black paint'),
 ('d02_2', 605, 465, 'jugando', 'Jugando No. 3', ASK, 'Acrylic painting: a bouquet of red blossoms bursting among swirls of multicolored paint'),
 ('d02_3', 595, 453, 'jugando', 'Jugando No. 4', ASK, 'Acrylic abstract: diagonal strokes of violet, green and blue like wind across water'),
 ('d02_4', 487, 485, 'jugando', 'Jugando No. 5', ASK, 'Acrylic abstract: looping dark red and blue lines over a marigold ground'),
 ('d03_3', 720, 563, 'campo', 'Mi gente de campo No. 1', ASK, 'Acrylic portrait: a woman in a straw hat carries a child on her back against a dark ground'),
 ('d03_1', 441, 423, 'campo', 'Mi gente de campo No. 2', ASK, 'Acrylic portrait: a woman in a wide straw hat, her face in warm ochre shadow'),
 ('d03_2', 441, 428, 'campo', 'Mi gente de campo No. 3', ASK, 'Acrylic portrait: a young woman beneath a broad cream sombrero, dark eyes looking out'),
 ('d03_0', 592, 419, 'campo', 'Mi gente de campo No. 4', ASK, 'Acrylic portrait: a round-cheeked baby held close against a blue and yellow ground'),
 ('d06_0', 498, 1100, 'divina', 'Divina No. 1', ASK, 'Acrylic painting: a figure in a red dress and red hat, outlined in black against stained-glass color fields'),
 ('d07_2', 507, 463, 'divina', 'Divina No. 2', ASK, 'Acrylic painting: a mother and child cheek to cheek, wrapped in golden hair against orange stripes'),
 ('d07_1', 548, 552, 'divina', 'Divina No. 3', ASK, 'Acrylic painting: four women in brightly patterned dresses standing together'),
 ('d06_3', 474, 1100, 'divina', 'Divina No. 4', ASK, 'Acrylic painting: a tall figure with long braids in a pink and violet dress'),
 ('d06_1', 497, 1100, 'divina', 'Divina No. 5', ASK, 'Acrylic painting: a woman in a deep red dress, her form outlined in black against pink, green and coral'),
 ('d07_0', 485, 568, 'divina', 'Divina No. 6', ASK, 'Acrylic painting: a faceless woman in a rose-colored blouse before a patterned wall'),
 ('d07_4', 456, 779, 'divina', 'Divina No. 7', ASK, 'Acrylic painting: a woman in a green dress and head wrap, painted in soft teal'),
 ('d08_1', 759, 377, 'floral', 'Floral No. 1', ASK, 'Acrylic painting: a vast orange-red poppy fills the canvas, edged in green'),
 ('d08_4', 480, 360, 'floral', 'Floral No. 2', ASK, 'Acrylic painting: a crimson hibiscus with a jeweled stamen against green leaves'),
 ('d08_0', 666, 254, 'floral', 'Floral No. 3', ASK, 'Acrylic painting: a white orchid spread wide across a green ground'),
 ('d09_0', 806, 617, 'reflect', 'Reflections No. 1', ASK, 'Acrylic painting: autumn trees and old brick houses reflected in a golden canal'),
 ('d09_4', 591, 454, 'reflect', 'Reflections No. 2', ASK, 'Acrylic still life: a green teapot and rose-patterned teacup before an ornate mirror'),
 ('d09_1', 538, 720, 'reflect', 'Reflections No. 3', ASK, 'Acrylic painting: a warm living room with a red armchair beside a lit fireplace'),
 ('d09_2', 507, 614, 'reflect', 'Reflections No. 4', ASK, 'Acrylic painting: a red teardrop shape rising from a rose beneath a pale moon'),
 ('d04_3', 708, 543, 'private', 'Colección privada No. 1', SOLD, 'Acrylic painting: a hummingbird mid-flight, wings spread against marigold'),
 ('d04_2', 925, 633, 'private', 'Colección privada No. 2', SOLD, 'Acrylic still life: flowers, fruit and a patterned pitcher on a table against hot pink'),
 ('d04_0', 707, 563, 'private', 'Colección privada No. 3', SOLD, 'Acrylic painting: a pianist at the keys surrounded by flying musical notes and color'),
 ('d04_1', 705, 516, 'private', 'Colección privada No. 4', SOLD, 'Acrylic painting: a pine silhouetted against a streaked violet and peach sunset'),
 ('d04_4', 619, 516, 'private', 'Colección privada No. 5', SOLD, 'Acrylic painting: a woman in a green dress reclining among glowing golden lights'),
 ('d04_5', 471, 697, 'private', 'Colección privada No. 6', SOLD, 'Acrylic painting: a figure in red raises broken chains toward a yellow sun over the sea'),
]


COLORS = {  # hue ranges in degrees
    'marigold':  dict(name='Marigold',  hex='#E29A1F', hues=[(32, 62)]),
    'scarlet':   dict(name='Scarlet',   hex='#C8372D', hues=[(348, 360), (0, 18)]),
    'coral':     dict(name='Coral',     hex='#E0703A', hues=[(18, 32)]),
    'magenta':   dict(name='Magenta',   hex='#C0507F', hues=[(290, 348)]),
    'violet':    dict(name='Violet',    hex='#7B5EA7', hues=[(252, 290)]),
    'cobalt':    dict(name='Cobalt',    hex='#2E5FA3', hues=[(200, 252)]),
    'turquoise': dict(name='Turquoise', hex='#2A9D9A', hues=[(160, 200)]),
    'leaf':      dict(name='Leaf',      hex='#3E8A5A', hues=[(70, 160)]),
}


def color_tags(path):
    """The painting's strongest color families, measured from its saturated pixels."""
    from PIL import Image
    im = Image.open(path).convert('RGB').resize((72, 72)).convert('HSV')
    counts = {k: 0 for k in COLORS}
    total = 0
    for h, s, v in im.getdata():
        total += 1
        if s < 90 or v < 60:
            continue
        deg = h * 360 / 255
        for k, c in COLORS.items():
            if any(a <= deg < b for a, b in c['hues']):
                counts[k] += 1
                break
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    return [k for k, n in ranked[:3] if n / total >= 0.07]


def music_bits(with_music):
    """Sound toggle, track map and footer credit — empty when music isn't shipped."""
    if not with_music:
        return '', 'null', ''
    btn = ('<button type="button" id="sound" class="soundbtn" aria-pressed="false">'
           '<span class="note" aria-hidden="true">&#9834;</span><span id="sound-label">Sound on</span></button>')
    tracks = json.dumps({k: dict(src='audio/' + v['file']) for k, v in MUSIC.items()})
    km = [v['title'] for v in MUSIC.values() if v['by'] == 'Kevin MacLeod']
    credit = ('<span class="credit">Music: ' + ', '.join('&ldquo;%s&rdquo;' % t for t in km) +
              ' by Kevin MacLeod (incompetech.com), licensed under '
              '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. '
              '&ldquo;Nacional Joropo&rdquo; &mdash; Lionel Belasco Orchestra, public domain.</span>')
    return btn, tracks, credit


def render(site_url=None, img_dir=os.path.join(HERE, 'img'), with_music=False):
    tags = {p[0]: color_tags(os.path.join(img_dir, p[0] + '.webp')) for p in P}
    ccount = {k: sum(1 for t in tags.values() if k in t) for k in COLORS}
    swatches = ''.join(
        f'<button type="button" class="sw" data-color="{k}" aria-pressed="false"><span class="paint" style="background:{c["hex"]}"></span>{c["name"]}</button>'
        for k, c in COLORS.items() if ccount[k] >= 3)
    counts = {k: sum(1 for p in P if p[3] == k) for k in COLLS}
    counts['all'] = len(P)
    chips = []
    for k, c in COLLS.items():
        dot = f'<span class="blob" style="background:{c["color"]}"></span>' if c['color'] else ''
        chips.append(f'<button type="button" class="chip" data-coll="{k}" aria-pressed="false">{dot}{html.escape(c["name"])} <span class="n">{counts[k]}</span></button>')

    figs = []
    for img, w, h, coll, title, (scls, stxt), alt in P:
        pid = re.sub(r'[^a-z0-9]+', '-', title.lower().replace('ó', 'o')).strip('-')
        figs.append(
            f'<figure class="piece" data-id="{pid}" data-coll="{coll}" data-colors="{" ".join(tags[img])}" data-title="{html.escape(title)}" data-status="{html.escape(stxt)}">'
            f'<button type="button" class="frame" aria-label="View {html.escape(title)} larger"><img src="{{{{img:{img}}}}}" alt="{html.escape(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></button>'
            f'<figcaption><span class="t">{html.escape(title)}</span><span class="m">Acrylic on canvas &middot; {html.escape(COLLS[coll]["name"])}</span>'
            f'<span class="status {scls}">{html.escape(stxt)}</span></figcaption></figure>')

    person = {'@type': 'Person', '@id': '#artist', 'name': 'Sandra Añez Powell',
              'alternateName': ['Sandra Anez Powell', 'Sandra Powell', 'S. Añez Powell'],
              'jobTitle': 'Painter', 'birthPlace': {'@type': 'Country', 'name': 'Venezuela'},
              'homeLocation': {'@type': 'Place', 'name': 'Annapolis, Maryland'},
              'knowsLanguage': ['en', 'es'],
              'description': 'Venezuelan-born acrylic painter in Annapolis, Maryland: Chesapeake regattas, harbor moons, portraits, florals and abstracts.',
              'sameAs': ['https://newvillageacademy.org/member/sandra-anez-powell-m-p-a/']}
    works = []
    for i, p in enumerate(P):
        art = {'@type': 'VisualArtwork', 'name': p[4], 'artform': 'Painting', 'artMedium': 'Acrylic',
               'artworkSurface': 'Canvas', 'creator': {'@id': '#artist'}, 'description': p[6]}
        if site_url:
            art['image'] = f'{site_url}img/{p[0]}.webp'
        works.append({'@type': 'ListItem', 'position': i + 1, 'item': art})
    if site_url:
        person['@id'] = site_url + '#artist'
        person['url'] = site_url
        person['image'] = site_url + 'img/d01_5.webp'
        for w in works:
            w['item']['creator'] = {'@id': site_url + '#artist'}
    ld = {'@context': 'https://schema.org', '@graph': [person, {'@type': 'ItemList', 'name': 'Paintings by Sandra Añez Powell', 'itemListElement': works}]}

    t = open(os.path.join(HERE, 'site.tpl.html'), encoding='utf8').read()
    t = t.replace('<!--CHIPS-->', ''.join(chips)).replace('<!--PIECES-->', '\n'.join(figs))
    t = t.replace('<!--JSONLD-->', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')
    btn, tracks, credit = music_bits(with_music)
    t = t.replace('<!--SOUNDBTN-->', btn).replace('/*MUSIC*/', tracks).replace('<!--MUSICCREDIT-->', credit)
    t = t.replace('<!--SWATCHES-->', swatches)
    t = t.replace('/*COLORS*/', json.dumps({k: dict(name=c['name'], hex=c['hex'], hues=c['hues']) for k, c in COLORS.items()}))
    return t.replace('/*COLLS*/', json.dumps({k: dict(name=v['name'], gloss=v['gloss'], intro=v['intro']) for k, v in COLLS.items()}, ensure_ascii=False))


def xmp_for(title, url):
    """IPTC-style creator, credit and rights, as XMP, for one image."""
    esc = lambda s: html.escape(s, quote=False)
    return (
        '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/"'
        ' xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/" xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/">'
        '<dc:creator><rdf:Seq><rdf:li>Sandra Añez Powell</rdf:li></rdf:Seq></dc:creator>'
        f'<dc:title><rdf:Alt><rdf:li xml:lang="x-default">{esc(title)}</rdf:li></rdf:Alt></dc:title>'
        '<dc:rights><rdf:Alt><rdf:li xml:lang="x-default">© 2026 Sandra Añez Powell. All rights reserved.</rdf:li></rdf:Alt></dc:rights>'
        '<photoshop:Credit>Sandra Añez Powell</photoshop:Credit>'
        '<xmpRights:Marked>True</xmpRights:Marked>'
        f'<xmpRights:WebStatement>{url}</xmpRights:WebStatement>'
        '</rdf:Description></rdf:RDF></x:xmpmeta><?xpacket end="w"?>')


IMG_RE = re.compile(r'\{\{img:([a-z0-9_]+)\}\}')


def build_artifact(out, img_dir):
    t = IMG_RE.sub(lambda m: 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(img_dir, m.group(1) + '.webp'), 'rb').read()).decode(), render(img_dir=img_dir))
    open(out, 'w', encoding='utf8').write(t)
    print('artifact', out, len(t.encode('utf8')), 'bytes')


def build_deploy(out, url, img_dir):
    from PIL import Image
    url = url.rstrip('/') + '/'
    t = render(url, img_dir, with_music=True)
    os.makedirs(os.path.join(out, 'audio'), exist_ok=True)
    for v in MUSIC.values():
        audio_dir = os.path.join(os.path.dirname(os.path.abspath(img_dir)), 'audio')
        src, dst = os.path.join(audio_dir, v['file']), os.path.join(out, 'audio', v['file'])
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copyfile(src, dst)
    used = sorted(set(IMG_RE.findall(t)))
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    titles = {p[0]: p[4] for p in P}
    titles['d01_5'] = 'Sandra Añez Powell in her studio'
    for n in used:
        src, dst = os.path.join(img_dir, n + '.webp'), os.path.join(out, 'img', n + '.webp')
        # Creator/credit/rights ride inside the file: Google Images shows them,
        # and they travel with the image when someone else re-posts it.
        Image.open(src).save(dst, 'WEBP', quality=78, method=6, xmp=xmp_for(titles.get(n, 'Painting'), url))
    og = Image.open(os.path.join(img_dir, 's_regatta.webp')).convert('RGB')
    og.save(os.path.join(out, 'img', 'og-regatta.jpg'), 'JPEG', quality=85)
    t = IMG_RE.sub(lambda m: f'img/{m.group(1)}.webp', t)
    # hero paintings are the first thing seen: load them eagerly
    split = t.index('</style>') + len('</style>')
    head_extra = (f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                  f'<link rel="canonical" href="{url}">\n'
                  f'<link rel="alternate" hreflang="en" href="{url}">\n'
                  f'<meta property="og:url" content="{url}">\n'
                  f'<meta property="og:image" content="{url}img/og-regatta.jpg">\n'
                  f'<meta property="og:image:alt" content="Regatta at Golden Hour, acrylic painting by Sandra Añez Powell">\n'
                  f'<meta name="twitter:card" content="summary_large_image">\n'
                  f'<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 40 34%22%3E%3Cpath d=%22M19 7 L19 24 L8 24 Z%22 fill=%22%23C0507F%22/%3E%3Cpath d=%22M21 4 L21 24 L33 24 Z%22 fill=%22%23E2971B%22/%3E%3Cpath d=%22M6 26 L34 26 L29 32 L11 32 Z%22 fill=%22%234A2E17%22/%3E%3C/svg%3E">\n')
    page = ('<!doctype html>\n<html lang="en">\n<head>\n' + head_extra + t[:split] +
            '\n</head>\n<body>\n' + t[split:] + '\n</body>\n</html>\n')
    open(os.path.join(out, 'index.html'), 'w', encoding='utf8').write(page)
    imgs = ''.join(f'\n    <image:image><image:loc>{url}img/{p[0]}.webp</image:loc><image:title>{html.escape(p[4])}</image:title></image:image>' for p in P)
    open(os.path.join(out, 'sitemap.xml'), 'w', encoding='utf8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n  <url>\n    <loc>' + url + '</loc>' + imgs + '\n  </url>\n</urlset>\n')
    open(os.path.join(out, 'robots.txt'), 'w', encoding='utf8').write(f'User-agent: *\nAllow: /\n\nSitemap: {url}sitemap.xml\n')
    open(os.path.join(out, '.nojekyll'), 'w').close()
    print('deploy', out, len(page.encode('utf8')), 'bytes html,', len(used), 'images')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--img', default=os.path.join(HERE, 'img'))
    ap.add_argument('--artifact')
    ap.add_argument('--deploy')
    ap.add_argument('--url')
    a = ap.parse_args()
    if a.artifact:
        build_artifact(a.artifact, a.img)
    if a.deploy:
        build_deploy(a.deploy, a.url, a.img)
