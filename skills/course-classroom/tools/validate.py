"""Checks one subject file against the authoring guide. Usage: python -I -X utf8 validate.py <section>.json"""
import json, re, sys
import xml.etree.ElementTree as ET

errs, warns = [], []
def E(where, msg): errs.append(f'{where}: {msg}')
def W(where, msg): warns.append(f'{where}: {msg}')

def need_ar(o, k, where, plain=False):
    if o.get(k) and not o.get(k + '_ar'):
        E(where, f'missing {k}_ar')
    v = o.get(k + '_ar')
    if v and not re.search('[؀-ۿ]', v):
        E(where, f'{k}_ar has no Arabic text')

def tex_ok(s, where):
    depth = 0
    for ch in s.replace('\\{', '').replace('\\}', ''):
        depth += ch == '{'
        depth -= ch == '}'
        if depth < 0:
            break
    if depth != 0:
        E(where, f'unbalanced braces in KaTeX: {s[:60]}')

def svg_ok(s, where):
    try:
        ET.fromstring(s)
    except ET.ParseError as e:
        E(where, f'SVG not well-formed: {e}')

def check_q(q, where, on_idea):
    k = q.get('kind')
    if on_idea and k not in ('mc', 'tf', 'num', 'match'):
        E(where, f'idea questions must be mc/tf/num/match, got {k}')
    if k == 'match':
        if len(q.get('pairs', [])) < 2:
            E(where, 'match needs at least 2 pairs')
        need_ar(q, 'explain', where)
        return
    if not q.get('q'):
        E(where, 'question text q missing')
    if k == 'mc':
        if not isinstance(q.get('answer'), int) or not 0 <= q['answer'] < len(q.get('options', [])):
            E(where, 'mc answer index out of range')
        need_ar(q, 'explain', where)
    elif k == 'tf':
        if not isinstance(q.get('answer'), bool):
            E(where, 'tf answer must be true/false')
        need_ar(q, 'explain', where)
    elif k == 'num':
        if not isinstance(q.get('answer'), (int, float)):
            E(where, 'num answer must be a number')
    elif k == 'tftable':
        for i, r in enumerate(q.get('rows', [])):
            if not isinstance(r[1], bool):
                E(where, f'row {i} truth value must be bool')
            if len(r) > 2 and (len(r) < 4 or not re.search('[؀-ۿ]', r[3] or '')):
                E(where, f'row {i} has a note but no Arabic note as 4th element')
    elif k == 'numbered':
        n = len(q.get('t1', []))
        for r in q.get('t2', []):
            if not 1 <= r[1] <= n:
                E(where, 'numbered answer out of range')
    elif k == 'written':
        if not q.get('model'):
            E(where, 'written question needs a model answer')
        need_ar(q, 'model', where)
        if not q.get('rubric'):
            E(where, 'written question needs a rubric')
    elif k == 'table':
        for c in q.get('cells', []):
            if not isinstance(c.get('answer'), (int, float)):
                E(where, f'table cell {c.get("label")} answer must be a number')
        for u in q.get('useful', []):
            tex_ok(u, where)
    else:
        E(where, f'unknown question kind {k}')
    if k in ('tftable', 'numbered', 'written', 'table') and not q.get('source'):
        W(where, 'no source citation')

def check_page(p, ids):
    pid = p.get('id', '?')
    if pid in ids:
        E(pid, 'duplicate id')
    ids.add(pid)
    t = p.get('type')
    if t not in ('idea', 'worked', 'quiz'):
        E(pid, f'bad type {t}')
    if t != 'quiz':
        need_ar(p, 'title', pid)
    if p.get('visual'):
        svg_ok(p['visual'], pid)
    if t == 'worked':
        if not p.get('question'):
            E(pid, 'worked page needs a question')
        if not p.get('source'):
            W(pid, 'worked page has no source')
    for n, s in enumerate(p.get('steps', [])):
        w = f'{pid} step {n + 1}'
        for k in ('title', 'say', 'warn', 'check'):
            need_ar(s, k, w)
        if s.get('classmate'):
            for k in ('q', 'a'):
                if not s['classmate'].get(k + '_ar'):
                    E(w, f'classmate {k}_ar missing')
        for ln in s.get('lines', []):
            tex_ok(ln if isinstance(ln, str) else (ln.get('ans') or ln.get('tex') or ''), w)
        if s.get('hi') and p.get('visual'):
            for key in s['hi']:
                if f'data-k="{key}"' not in p['visual'] and f"data-k='{key}'" not in p['visual'] and not re.search(rf'data-k="[^"]*\b{re.escape(key)}\b', p['visual']):
                    W(w, f'hi key "{key}" not found in the visual')
    for n, q in enumerate(p.get('questions', [])):
        check_q(q, f'{pid} question {n + 1}', t == 'idea')
    if t == 'quiz' and not p.get('questions'):
        E(pid, 'quiz without questions')

d = json.load(open(sys.argv[1], encoding='utf8'))
sec = d.get('section') or {}
for k in ('id', 'title', 'short', 'pages'):
    if not sec.get(k):
        E('section', f'missing {k}')
ids = set()
for p in sec.get('pages', []):
    check_page(p, ids)
for p in d.get('derivations', []):
    check_page(p, ids)
types = {}
for p in sec.get('pages', []) + d.get('derivations', []):
    types[p.get('type')] = types.get(p.get('type'), 0) + 1
print('pages by type:', types, '| derivations:', len(d.get('derivations', [])))
print('\n'.join('ERROR ' + e for e in errs) or 'no errors')
print('\n'.join('warn  ' + w for w in warns[:40]))
sys.exit(1 if errs else 0)
