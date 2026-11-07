"""Checks every graph-paper sheet page: is the drawing inside the printed grid, and are the axes on whole-cm grid lines?
Usage: python -I -X utf8 gridcheck.py <built classroom .html>"""
import json, re, sys
h = open(sys.argv[1], encoding='utf8').read()
L = json.loads(re.search(r'<script[^>]*id="lesson-data"[^>]*>(.*?)</script>', h, re.S).group(1).replace('<\\/', '</'))
GRID = {'a4p': (52, 88, 800, 1148), 'a4l': (88, 48, 1148, 796), 'a3p': (40, 40, 1148, 1640), 'a3l': (40, 40, 1640, 1148)}

def path_points(d):
    pts, x, y = [], 0.0, 0.0
    for c, args in re.findall(r'([MLHVZmlhvz])([^MLHVZmlhvz]*)', d):
        n = [float(v) for v in re.findall(r'-?\d*\.?\d+(?:e-?\d+)?', args)]
        if c in 'ML':
            for i in range(0, len(n) - 1, 2): x, y = n[i], n[i + 1]; pts.append((x, y))
        elif c in 'ml':
            for i in range(0, len(n) - 1, 2): x, y = x + n[i], y + n[i + 1]; pts.append((x, y))
        elif c == 'H': x = n[-1]; pts.append((x, y))
        elif c == 'h': x += sum(n); pts.append((x, y))
        elif c == 'V': y = n[-1]; pts.append((x, y))
        elif c == 'v': y += sum(n); pts.append((x, y))
    return pts

bad = 0
for s in L['sections']:
    for p in s['pages']:
        if not p.get('sheet') or p.get('paper') not in GRID:
            continue
        v = p['visual']; gx0, gy0, gx1, gy1 = GRID[p['paper']]
        v2 = re.sub(r'<defs>.*?</defs>', '', re.sub(r'<image[^>]*>', '', v), flags=re.S)   # pictures and arrowhead shapes are not drawn on the grid
        pts = [q for d in re.findall(r'<path[^>]* d="([^"]+)"', v2) for q in path_points(d)]
        pts += [(float(a), float(b)) for a, b in re.findall(r'<circle[^>]*cx="([-\d.]+)"[^>]*cy="([-\d.]+)"', v2)]
        if not pts:
            continue
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        out = min(xs) < gx0 - 2 or max(xs) > gx1 + 2 or min(ys) < gy0 - 2 or max(ys) > gy1 + 2
        ax = re.search(r'<path[^>]* d="M([\d.]+) ([\d.]+)V([\d.]+)H([\d.]+)"', v2)   # the axes: up the y axis, along the x axis
        offgrid = ax and ((float(ax.group(1)) - gx0) % 40 > 1 and (float(ax.group(1)) - gx0) % 40 < 39 or (float(ax.group(3)) - gy0) % 40 > 1 and (float(ax.group(3)) - gy0) % 40 < 39)
        if out or offgrid:
            bad += 1
            print(f"{p['id']:16s} {p['paper']}  drawing x {min(xs):.0f}–{max(xs):.0f} y {min(ys):.0f}–{max(ys):.0f}  grid x {gx0}–{gx1} y {gy0}–{gy1}"
                  + ('  OUTSIDE' if out else '') + ('  AXES OFF THE CM LINES' if offgrid else ''))
print(bad, 'sheet pages to fix')
