"""Crops each question out of its original paper (tutorial sheets, homework, exams, slides) as a picture.
Every worked page may carry "qpic": [[code, page, top, bottom], ...] (code from prepare.py's manifest, page 1-based,
top/bottom as fractions of the page height). Writes <course>/author/qpics.json = {"pics": {key: data URI},
"pages": {page id: [keys]}} and the crops as PNGs in <course>/img/qpic/ for checking by eye.
Usage: python -I -X utf8 qpics.py <course folder> <work folder from prepare.py>"""
import base64, glob, io, json, os, sys
import pymupdf
from PIL import Image

HERE = os.path.join(os.path.abspath(sys.argv[1]), 'author')
SRC = os.path.abspath(sys.argv[2])

def crop(code, page, f0, f1):
    pdf = os.path.join(SRC, code + '.pdf')
    if os.path.exists(pdf):
        pg = pymupdf.open(pdf)[page - 1]
        R = pg.rect
        r = pymupdf.Rect(R.width * 0.03, R.height * max(0, f0), R.width * 0.97, R.height * min(1, f1))
        pix = pg.get_pixmap(dpi=140, clip=r)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    else:
        f = next(iter([g for g in glob.glob(os.path.join(SRC, code + '.*')) if os.path.splitext(g)[1].lower() in ('.jpg', '.jpeg', '.png')]))
        im = Image.open(f).convert('RGB')
        im = im.crop((0, int(im.height * max(0, f0)), im.width, int(im.height * min(1, f1))))
    im = im.convert('L')
    if im.width > 860:
        im = im.resize((860, round(im.height * 860 / im.width)), Image.LANCZOS)
    return im

def uri(im):
    b = io.BytesIO(); im.save(b, 'JPEG', quality=50, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

pics, pages = {}, {}
os.makedirs(os.path.join(HERE, '..', 'img', 'qpic'), exist_ok=True)
for f in sorted(glob.glob(os.path.join(HERE, '*.json'))):
    if os.path.basename(f) in ('qpics.json', 'examples.json'):
        continue
    d = json.load(open(f, encoding='utf8'))
    if not isinstance(d, dict) or 'section' not in d:
        continue
    for p in d['section']['pages'] + d.get('derivations', []):
        for c in p.get('qpic') or []:
            try:
                code, page, f0, f1 = c
                k = f'{code}-{page}-{round(f0 * 100)}-{round(f1 * 100)}'
                if k not in pics:
                    im = crop(code, int(page), float(f0), float(f1))
                    pics[k] = uri(im)
                    im.save(os.path.join(HERE, '..', 'img', 'qpic', k + '.png'))
                pages.setdefault(p['id'], []).append(k)
            except Exception as e:
                print('FAIL', p['id'], c, e)
json.dump({'pics': pics, 'pages': pages}, open(os.path.join(HERE, 'qpics.json'), 'w', encoding='utf8'))
print(len(pics), 'pictures,', sum(len(v) for v in pics.values()) // 1024, 'KB,', len(pages), 'pages')
