"""Renders a tutorial page's full-sheet visual on its graph paper, exactly as the board shows it, so it can be put
next to the homework photo. Usage: python -I -X utf8 sheetview.py <file.json> <page id> <out.png>
A sheet visual uses viewBox "0 0 4W 4H" (4 units per mm over the WHOLE sheet, W×H in mm from PAPERS)."""
import json, os, subprocess, sys

PAPERS = {'a4p': (210, 297, 1), 'a4l': (297, 210, 1), 'a3p': (297, 420, 0), 'a3l': (420, 297, 0)}

def grid(k):
    W, H, pad = PAPERS[k]
    if pad:
        x0, y0, x1, y1 = (13, 22, W - 10, H - 10) if W < H else (22, 12, W - 10, H - 11)
    else:
        x0, y0, x1, y1 = 10, 10, W - 10, H - 10
    return W, H, pad, x0, y0, x0 + int(x1 - x0), y0 + int(y1 - y0)

def paper_svg(k):
    W, H, pad, x0, y0, x1, y1 = grid(k)
    if pad:
        c = dict(page='#ffffff', m1='#f6cdb0', m5='#efad82', m10='#e6874c', edge='#e2803f')
        band = (f'<rect width="{W}" height="15" fill="#e8e7e4"/>' if W < H else f'<rect width="15" height="{H}" fill="#e8e7e4"/>')
    else:
        c = dict(page='#f1e5d8', m1='#e2c9b3', m5='#d6b294', m10='#c4977a', edge='#c08d6f'); band = ''
    pat = lambda i, s, col, sw: (f'<pattern id="{i}" x="{x0}" y="{y0}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">'
                                 f'<path d="M{s} 0H0V{s}" fill="none" stroke="{col}" stroke-width="{sw}"/></pattern>')
    g = (f'<svg class="bdpaper" viewBox="0 0 {W} {H}" preserveAspectRatio="none"><defs>{pat("pm1",1,c["m1"],.1)}'
         f'{pat("pm5",5,c["m5"],.2)}{pat("pm10",10,c["m10"],.33)}</defs><rect width="{W}" height="{H}" fill="{c["page"]}"/>{band}')
    for i in ('pm1', 'pm5', 'pm10'):
        g += f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="url(#{i})"/>'
    return g + '</svg>'

if __name__ == '__main__':
    src, pid, out = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
    d = json.load(open(src, encoding='utf8'))
    pages = [p for v in d.values() if isinstance(v, list) for p in v] if 'section' not in d else d['section']['pages']
    p = next(p for p in pages if p['id'] == pid)
    k = p['paper']; W, H = PAPERS[k][:2]; px = 4   # 4 px per mm
    css = ('body{margin:0}.st{position:relative;width:%dpx;height:%dpx;font-family:monospace;--fg:#1f2a2e;--muted:#55635e;'
           '--line:#9aa4a0;--tint:rgba(11,110,116,.12);--accent:#0b6e74}.st>svg,.v svg{position:absolute;inset:0;width:100%%;height:100%%}'
           '.v svg text{fill:var(--fg);font-size:13px}.v svg .m{fill:var(--muted)}.v svg .s{stroke:var(--fg);fill:none;stroke-width:1.6}'
           '.v svg .f{fill:var(--tint);stroke:var(--fg);stroke-width:1.6}.v svg .soft{stroke:var(--line);fill:none;stroke-width:1.2}'
           '.v svg .tag{font-weight:600}.v svg .a{fill:var(--fg)}') % (W * px, H * px)
    page = os.path.splitext(out)[0] + '.html'
    open(page, 'w', encoding='utf8').write(f'<!doctype html><meta charset="utf-8"><style>{css}</style><div class="st">{paper_svg(k)}<div class="v">{p["visual"]}</div></div>')
    subprocess.run([r'C:\Program Files\Google\Chrome\Application\chrome.exe', '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    f'--window-size={W*px},{H*px}', f'--screenshot={out}',
                    '--user-data-dir=' + os.path.join(os.path.dirname(out), 'sprof'), 'file:///' + page.replace('\\', '/')], capture_output=True)
    print(pid, k, '->', out)
