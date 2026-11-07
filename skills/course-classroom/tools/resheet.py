"""Moves and rescales a graph-paper sheet drawing so it sits on the printed grid: every coordinate is changed
(x' = sx·x + tx, y' = sy·y + ty), so the board's step-by-step dots, curves and staircases stay exact. Text sizes,
dot radii and stroke widths are kept. Used to put the packed-column x–y plots (drawn 20 cm wide, wider than the
A4 pad's grid) on a 15 cm square with the origin on a whole-cm line, and to snap plots that sat half a cm off.
Usage: python -I -X utf8 resheet.py   (edits the author files in place; backups in bak_grid/)"""
import glob, json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = r'-?\d*\.?\d+(?:e-?\d+)?'

def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def xform_d(d, f):
    sx, tx, sy, ty = f
    out, i = [], 0
    for c, args in re.findall(r'([MLHVCSQTAZmlhvcsqtaz])([^MLHVCSQTAZmlhvcsqtaz]*)', d):
        n = [float(v) for v in re.findall(NUM, args)]
        o = []
        if c in 'MLCSQT':
            for k in range(0, len(n) - 1, 2): o += [sx * n[k] + tx, sy * n[k + 1] + ty]
        elif c in 'mlcsqt':
            for k in range(0, len(n) - 1, 2): o += [sx * n[k], sy * n[k + 1]]
        elif c == 'H': o = [sx * v + tx for v in n]
        elif c == 'h': o = [sx * v for v in n]
        elif c == 'V': o = [sy * v + ty for v in n]
        elif c == 'v': o = [sy * v for v in n]
        elif c in 'Aa':
            for k in range(0, len(n) - 6, 7):
                rx, ry, rot, la, sw, x, y = n[k:k + 7]
                o += [abs(sx) * rx, abs(sy) * ry, rot, la, sw] + ([sx * x + tx, sy * y + ty] if c == 'A' else [sx * x, sy * y])
        out.append(c + ' '.join(fmt(v) for v in o))
    return ''.join(out)

def xform_svg(svg, f):
    sx, tx, sy, ty = f
    X = lambda v: fmt(sx * float(v) + tx)
    Y = lambda v: fmt(sy * float(v) + ty)
    def tag(m):
        t = m.group(0)
        if t.startswith('<image'):
            return t                                  # a pasted picture keeps its place
        t = re.sub(r' d="([^"]*)"', lambda a: ' d="' + xform_d(a.group(1), f) + '"', t)
        for k in ('x', 'cx', 'x1', 'x2'):
            t = re.sub(rf' {k}="({NUM})"', lambda a, k=k: f' {k}="{X(a.group(1))}"', t)
        for k in ('y', 'cy', 'y1', 'y2'):
            t = re.sub(rf' {k}="({NUM})"', lambda a, k=k: f' {k}="{Y(a.group(1))}"', t)
        t = re.sub(rf' width="({NUM})"', lambda a: f' width="{fmt(abs(sx) * float(a.group(1)))}"', t) if not t.startswith('<svg') else t
        t = re.sub(rf' height="({NUM})"', lambda a: f' height="{fmt(abs(sy) * float(a.group(1)))}"', t) if not t.startswith('<svg') else t
        t = re.sub(r' points="([^"]*)"', lambda a: ' points="' + ' '.join(
            f'{X(p)},{Y(q)}' for p, q in re.findall(rf'({NUM})[ ,]+({NUM})', a.group(1))) + '"', t)
        t = re.sub(rf'rotate\(({NUM})[ ,]+({NUM})[ ,]+({NUM})\)', lambda a: f'rotate({a.group(1)} {X(a.group(2))} {Y(a.group(3))})', t)
        return t
    # arrowhead and pattern shapes in <defs> are in their own coordinates: leave them alone
    parts = re.split(r'(<defs>.*?</defs>)', svg, flags=re.S)
    return ''.join(pt if pt.startswith('<defs>') else re.sub(r'<(?!/)(?!svg)[a-zA-Z][^>]*>', tag, pt) for pt in parts)

def axes(svg):
    """The plot's axes path: up the y axis, then along the x axis: (x0, ytop, ybottom, xend)."""
    m = re.search(rf'<path[^>]* d="M({NUM}) ({NUM})V({NUM})H({NUM})"', svg)
    return tuple(float(v) for v in m.groups()) if m else None

GRID0 = {'a4p': (52, 88), 'a4l': (88, 48), 'a3p': (40, 40), 'a3l': (40, 40)}

def plan(p):
    """The transform for one page, or None when it is already on the grid."""
    ax = axes(p['visual'])
    if not ax:
        return None
    x0, ytop, ybot, xend = ax
    gx, gy = GRID0[p['paper']]
    w = xend - x0
    if p['paper'] == 'a4p' and w > 700:          # wider than the A4 pad's grid (18.7 cm): 0–1 over 15 cm
        s = 600 / w
        nx0, nybot = gx + 80, gy + 800           # origin 2 cm in from the grid's left edge, 20 cm down
        return (s, nx0 - s * x0, s, nybot - s * ybot)
    dx = -((x0 - gx) % 40) if (x0 - gx) % 40 <= 20 else 40 - (x0 - gx) % 40
    dy = -((ybot - gy) % 40) if (ybot - gy) % 40 <= 20 else 40 - (ybot - gy) % 40
    if abs(dx) < 1 and abs(dy) < 1:
        return None
    return (1, dx, 1, dy)

if __name__ == '__main__':
    os.makedirs(os.path.join(HERE, 'bak_grid'), exist_ok=True)
    TARGET = {'tut6-q1', 'tut6-q1c', 'tut6b-q1', 'nt6-q1-a', 'nt6-q1-b', 'tut1b-q1', 'tut1b-q2', 'tut2b-q2', 'nt1-q1'}
    done = set()
    for f in sorted(glob.glob(os.path.join(HERE, '*.json'))):
        if os.path.basename(f) in ('qpics.json', 'examples.json', 'titles.json', 'titles_in.json', 'inventory.json'):
            continue
        d = json.load(open(f, encoding='utf8'))
        lists = []
        if isinstance(d, dict) and 'section' in d:
            lists = [d['section']['pages'], d.get('derivations', [])]
        elif isinstance(d, dict):
            lists = [v for v in d.values() if isinstance(v, list)]
        changed = False
        for pages in lists:
            for p in pages:
                if not isinstance(p, dict) or p.get('id') not in TARGET or not p.get('sheet'):
                    continue
                t = plan(p)
                if t:
                    p['visual'] = xform_svg(p['visual'], t)
                    changed = True
                    done.add(p['id'])
                    print(f"{os.path.basename(f):14s} {p['id']:12s} scale {t[0]:.3f}  move x {t[1]:+.1f} y {t[3]:+.1f}  axes now {axes(p['visual'])}")
        if changed:
            shutil.copy(f, os.path.join(HERE, 'bak_grid', os.path.basename(f)))
            json.dump(d, open(f, 'w', encoding='utf8'), ensure_ascii=False)
    print('fixed', sorted(done), '| not found:', sorted(TARGET - done))
