"""Validates a tutorial file (dict of section id -> pages) with validate.py, plus the sheet rules.
Usage: python -I -X utf8 vt.py tut_a.json"""
import json, os, re, subprocess, sys
f = sys.argv[1]; d = json.load(open(f, encoding='utf8'))
pages = [p for v in d.values() for p in v]
PAPERS = {'a4p': (210, 297), 'a4l': (297, 210), 'a3p': (297, 420), 'a3l': (420, 297)}
bad = 0
for p in pages:
    if p.get('sheet'):
        W, H = PAPERS.get(p.get('paper'), (0, 0))
        m = re.search(r'viewBox="([^"]+)"', p.get('visual', ''))
        if not W or not m or m.group(1).split() != ['0', '0', str(4 * W), str(4 * H)]:
            print('ERROR', p['id'], 'sheet visual needs paper and viewBox "0 0 %d %d"' % (4 * W, 4 * H)); bad += 1
tmp = os.path.splitext(f)[0] + '_vt.json'
json.dump({'section': {'id': 'tut', 'title': 'Tutorials', 'short': 'Tutorials', 'pages': pages}, 'derivations': []},
          open(tmp, 'w', encoding='utf8'), ensure_ascii=False)
r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'validate.py'), tmp], capture_output=True, text=True, encoding='utf8')
print(r.stdout + r.stderr); os.remove(tmp)
