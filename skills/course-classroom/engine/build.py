"""Builds a course classroom (one HTML page) from a course folder.
Usage: python -I -X utf8 build.py <course folder> [out.html]

The course folder holds:
  course.json        the course settings (see examples/course.example.json)
  facts.txt          a paragraph of course facts for the AI (professor, topics, grading, textbooks)
  author/<sid>.json  one file per subject: {"section": {...pages...}, "derivations": [...]}
  author/<sid>_x*.json  extra question pages for a subject, written separately (same format)
  author/qpics.json  question pictures cropped from the original sheets (tools/qpics.py)
The player, the boards and the AI live next to this script (engine/)."""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
COURSE = os.path.abspath(sys.argv[1])
C = json.load(open(os.path.join(COURSE, 'course.json'), encoding='utf8'))
AUTH = os.path.join(COURSE, 'author')
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(COURSE, C['id'] + '.html')
WB = C.get('paper', 'graph') == 'whiteboard'      # 'whiteboard': adaptive board, plots on plain white; 'graph': real graph paper
lines = open(os.path.join(HERE, 'template.html'), encoding='utf8').read().split('\n')

# ---------- course data ----------
ORDER = [s['id'] for s in C['sections']]
home = C.get('home_page') or json.load(open(os.path.join(HERE, 'home.default.json'), encoding='utf8'))
home = json.loads(json.dumps(home, ensure_ascii=False).replace('{TITLE}', C['title']).replace('{CODE}', C.get('code', ''))
                  .replace('{PROFESSOR}', C.get('professor', 'the professor')).replace('{AI}', C.get('teacher_name', 'Course AI')))
sections, derivs = [home], []
for meta in C['sections']:
    sid = meta['id']
    f = os.path.join(AUTH, sid + '.json')
    if not os.path.exists(f):
        print('missing section', sid)
        continue
    d = json.load(open(f, encoding='utf8'))
    s = d['section']
    s['title'], s['short'] = meta.get('title', s.get('title')), meta.get('short', s.get('short'))
    s.pop('title_ar', None); s.pop('short_ar', None)   # subject names stay English
    sections.append(s)
    # extra question pages for a subject written separately go before the quizzes
    for xf in sorted(glob.glob(os.path.join(AUTH, sid + '_x*.json'))):
        x = json.load(open(xf, encoding='utf8'))
        if 'section' in x:
            x['pages'] = x['section']['pages']
        at = next((n for n, p in enumerate(s['pages']) if p.get('type') == 'quiz'), len(s['pages']))
        s['pages'][at:at] = x.get('pages', [])
        d.setdefault('derivations', []).extend(x.get('derivations', []))
        print('extra', os.path.basename(xf), len(x.get('pages', [])), 'pages')
    for p in d.get('derivations', []):
        p['_from'] = s['short']
        derivs.append(p)
if derivs:
    for n, p in enumerate(derivs, 1):
        p['chip'] = 'D' + str(n)
        p['level'] = p.pop('_from')
        p.setdefault('type', 'worked')
    sections.append({'id': 'deriv', 'title': 'Derivations', 'title_ar': 'الاشتقاقات', 'short': 'Derivations', 'short_ar': 'الاشتقاقات', 'pages': derivs})
# More: questions students upload (PDF, Word, photos) are solved into pages here at run time
if C.get('more', True):
    sections.append({'id': 'more', 'title': 'More: your own questions', 'short': 'More', 'pages': [
        {'id': 'more-upload', 'type': 'more', 'chip': 'Upload', 'title': 'Upload your questions', 'steps': [{'title': 'Upload'}]}]})

facts = C.get('facts', '')
if os.path.exists(os.path.join(COURSE, 'facts.txt')):
    facts = open(os.path.join(COURSE, 'facts.txt'), encoding='utf8').read()
L = {'format': 'course', 'id': C['id'], 'title': C['title'], 'subtitle': C.get('subtitle', ''), 'lang': 'en',
     'theme': C.get('theme', {'accent': '#3b5bdb', 'accentDark': '#91a7ff'}),
     'teacher': {'name': C.get('teacher_name', 'Course AI'), 'initials': 'AI', 'persona': 'Patient and plain-spoken. Explains why a line is there, and points out where students usually slip.'},
     'classmate': {'name': C.get('classmate_name', 'Faisal'), 'initials': C.get('classmate_name', 'Faisal')[0], 'persona': 'Quick to guess and honest when unsure. Often right about the pattern, and works things out aloud.'},
     'facts': facts, 'solve': C.get('solve_style', ''),
     'widgets': {}, 'dir': 'ltr', 'sections': sections}

TITLES = {}
if os.path.exists(os.path.join(AUTH, 'titles.json')):
    TITLES = json.load(open(os.path.join(AUTH, 'titles.json'), encoding='utf8'))
for s in sections:
    for p in s['pages']:
        if p['id'] in TITLES:
            p['title'] = TITLES[p['id']]
        if p.get('type') in ('worked', 'idea') and C.get('titles_english', True):
            p.pop('title_ar', None)
# Each subject runs: ideas (interactive) -> the professor's own questions (tutorials, homework, his examples)
# -> other questions of the same type (past exams, textbook) -> quizzes.
PROF = tuple(C.get('professor_chips', ['Tut', 'HW', 'Example', 'Ex.', 'Exercise', 'New Tut', 'Slide']))
def rank(p):
    if p.get('type') == 'idea':
        return 0
    if p.get('type') == 'quiz':
        return 3
    return 1 if str(p.get('chip', '')).startswith(PROF) or p.get('prof') else 2
for s in sections:
    if s['id'] not in ('start', 'deriv', 'more'):
        s['pages'].sort(key=rank)   # stable: keeps the order inside each group
# Paper. Whiteboard mode: every sheet is plain white, graphs are real plots. Graph mode: ideas on plain A4, worked
# pages on the paper the page names (homework sheets carry their own), else the subject's paper, else the default.
PAPER_BY = C.get('paper_by_section', {})
for s in sections:
    for p in s['pages']:
        if p.get('type') not in ('idea', 'worked'):
            continue
        if WB or p.get('type') == 'idea':
            p['paper'] = 'a4n'
            if WB:
                p.pop('sheet', None)
        else:
            sid = s['id'] if s['id'] != 'deriv' else next((m['id'] for m in C['sections'] if m.get('short') == p.get('level')), 'deriv')
            p['paper'] = p.get('paper') or (PAPER_BY.get(sid) if p.get('visual') else None) or (C.get('default_paper', 'a4p') if p.get('visual') else 'a4p')
# Questions are shown as the picture cropped from the original sheet; the typed text stays underneath, folded.
QP = json.load(open(os.path.join(AUTH, 'qpics.json'), encoding='utf8')) if os.path.exists(os.path.join(AUTH, 'qpics.json')) else {'pics': {}, 'pages': {}}
used = set()
ALT = C.get('qpic_alt', 'The question as printed on the original sheet').replace('"', '&quot;')
for s in sections:
    for p in s['pages']:
        keys = [k for k in QP['pages'].get(p['id'], []) if k in QP['pics']]
        if keys and p.get('question'):
            used.update(keys)
            imgs = ''.join(f'<img class="qpic" data-qpic="{k}" alt="{ALT}">' for k in keys)
            p['question'] = imgs + '<details class="qtyped"><summary>Typed text of the question</summary>' + p['question'] + '</details>'
import re
for s in sections:   # pictures already placed in a question (data-qpic) are kept too
    for p in s['pages']:
        used.update(re.findall(r'data-qpic="([^"]+)"', p.get('question') or ''))
QPICS = {k: v for k, v in QP['pics'].items() if k in used}
print('question pictures', len(QPICS), sum(map(len, QPICS.values())) // 1024, 'KB')

def fix_tex(o):
    """KaTeX rejects a superscript on a spacing command (\\,^\\circ): give it an empty base."""
    if isinstance(o, dict):
        return {k: fix_tex(v) for k, v in o.items()}
    if isinstance(o, list):
        return [fix_tex(v) for v in o]
    if isinstance(o, str):
        return o.replace('\\,^\\circ', '\\,{}^\\circ').replace('\\ ^\\circ', '\\ {}^\\circ').replace('\\;^\\circ', '\\;{}^\\circ').replace("\\,'", "'")   # a prime cannot follow a thin space
    return o
L['sections'] = fix_tex(L['sections'])

i = next(n for n, t in enumerate(lines) if 'id="lesson-data"' in t)
t = lines[i]
head = t[:t.index('>') + 1]
lines[i] = head + json.dumps(L, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'
boot = next(n for n, t in enumerate(lines) if t.strip() == '<script>Course.boot();</script>')
del lines[i + 1:boot]          # drop the template's own widgets
lines.insert(i + 1, '<script>var QPICS=' + json.dumps(QPICS) + ';</script>')
html = '\n'.join(lines)

# ---------- player changes ----------
PAPER_JS = r'''
/* Whiteboard paper: real millimetre graph paper. A4 is a white pad with an orange mm grid and a grey binding strip;
   A3 is a warm loose sheet with a softer brown-orange grid. Sizes are in mm; the board keeps 1000 units across. */
var PAPERS={a4p:{w:210,h:297,pad:1},a4l:{w:297,h:210,pad:1},a3p:{w:297,h:420,pad:0},a3l:{w:420,h:297,pad:0},a4n:{w:210,h:297,plain:1},wb:{w:210,h:297,plain:1,wb:1}};
var PAPER_NAMES={a4p:'A4 portrait',a4l:'A4 landscape',a3p:'A3 portrait',a3l:'A3 landscape',a4n:'A4 plain'};
function setPaper(k){if(!PAPERS[k])k='a4p';if(B)B.paper=k;BH=Math.round(BW*PAPERS[k].h/PAPERS[k].w);}
function paperEl(k){
  var P=PAPERS[k]||PAPERS.a4p,W=P.w,H=P.h,g,c,x0,y0,x1,y1,band='';
  if(P.plain){var dp=document.createElement('div');dp.innerHTML='<svg class="bdpaper" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" aria-hidden="true"><rect width="'+W+'" height="'+H+'" fill="#ffffff"/></svg>';return dp.firstChild;}
  if(P.pad){
    c={page:'#ffffff',m1:'#f6cdb0',m5:'#efad82',m10:'#e6874c',edge:'#e2803f'};
    if(W<H){band='<rect x="0" y="0" width="'+W+'" height="15" fill="#e8e7e4"/><path d="M0 15H'+W+'" stroke="#c9c6c0" stroke-width=".4"/>';x0=13;y0=22;x1=W-10;y1=H-10;}
    else{band='<rect x="0" y="0" width="15" height="'+H+'" fill="#e8e7e4"/><path d="M15 0V'+H+'" stroke="#c9c6c0" stroke-width=".4"/>';x0=22;y0=12;x1=W-10;y1=H-11;}
  }else{c={page:'#f1e5d8',m1:'#e2c9b3',m5:'#d6b294',m10:'#c4977a',edge:'#c08d6f'};x0=10;y0=10;x1=W-10;y1=H-10;}
  x1=x0+Math.floor(x1-x0);y1=y0+Math.floor(y1-y0);
  function pat(id,s,col,sw){return '<pattern id="'+id+'" x="'+x0+'" y="'+y0+'" width="'+s+'" height="'+s+'" patternUnits="userSpaceOnUse"><path d="M'+s+' 0H0V'+s+'" fill="none" stroke="'+col+'" stroke-width="'+sw+'"/></pattern>';}
  g='<svg class="bdpaper" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" aria-hidden="true"><defs>'+pat('pm1',1,c.m1,.1)+pat('pm5',5,c.m5,.2)+pat('pm10',10,c.m10,.33)+'</defs>'
   +'<rect width="'+W+'" height="'+H+'" fill="'+c.page+'"/>'+band;
  ['pm1','pm5','pm10'].forEach(function(id){g+='<rect x="'+x0+'" y="'+y0+'" width="'+(x1-x0)+'" height="'+(y1-y0)+'" fill="url(#'+id+')"/>';});
  g+='<rect x="'+x0+'" y="'+y0+'" width="'+(x1-x0)+'" height="'+(y1-y0)+'" fill="none" stroke="'+c.edge+'" stroke-width=".35"/></svg>';
  var d=document.createElement('div');d.innerHTML=g;return d.firstChild;
}
/* The grid area of a paper, in mm, matching paperEl. */
function paperBox(k){
  var P=PAPERS[k]||PAPERS.a4p,W=P.w,H=P.h,x0,y0,x1,y1;
  if(P.wb)return {W:100,H:100,x0:2.5,y0:2.5,x1:97.5,y1:97.5};
  if(P.plain){x0=15;y0=15;x1=W-15;y1=H-15;}else if(P.pad){if(W<H){x0=13;y0=22;x1=W-10;y1=H-10;}else{x0=22;y0=12;x1=W-10;y1=H-11;}}else{x0=10;y0=10;x1=W-10;y1=H-10;}
  return {W:W,H:H,x0:x0,y0:y0,x1:x0+Math.floor(x1-x0),y1:y0+Math.floor(y1-y0)};
}
'''
PAPER_JS += open(os.path.join(HERE, 'board-whiteboard.js' if WB else 'board-paper.js'), encoding='utf8').read()
PAPER_JS += open(os.path.join(HERE, 'ai.js'), encoding='utf8').read()
PATCH = [
 ('<title>CHE 423 Classroom</title>', '<title>' + C['title'] + '</title>', 1),
 ('&family=JetBrains+Mono:wght@400;600', '&family=Patrick+Hand&family=JetBrains+Mono:wght@400;600', 1),   # handwriting for the sheets
 ('show me how to find the LMTD', C.get('ask_example', 'show me the next step'), 1),
 # a homework-sheet visual covers the whole paper; in the lesson panel show only the drawn part
 ("  if(p.visual)box.innerHTML=p.visual;\n", "  if(p.visual)box.innerHTML=p.visual;\n  if(p.sheet&&p.visual){var sb=fullBox(p),sv0=box.querySelector('svg');if(sb&&sv0)sv0.setAttribute('viewBox',sb);}\n", 1),
 # paper helpers live next to the board code
 ('var B=null;', 'var B=null;' + PAPER_JS, 1),
 ("function boardLoad(p){if(B&&B.id===p.id)return B;", "function boardLoad(p){if(B&&B.id===p.id){setPaper(B.paper);return B;}", 1),
 ("turns:[],color:'ink',erase:false,penSeen:false};return B;}", "turns:[],color:'ink',erase:false,penSeen:false,paper:(d&&d.paperSet&&d.paper)||p.paper||'a4p',paperSet:!!(d&&d.paperSet)};setPaper(B.paper);return B;}", 1),
 # the board is the default view on graph pages; closing it by hand keeps it closed for that page,
 # and opening it again starts from a blank sheet
 ("function toggleBoard(){boardOpen=!boardOpen;",
  "function toggleBoard(){boardOpen=!boardOpen;autoOn=false;var tp=pg();if(boardOpen){delete userClosed[tp.id];microReset(tp);}else userClosed[tp.id]=true;", 1),
 ("function render(){\n  ladder();", "function render(){\n  autoBoard();ladder();", 1),
 # choosing a page from the lesson bar starts its drawing from a blank sheet
 ("function go(p,st){stopVoice();stopAI();", "function go(p,st){stopVoice();stopAI();MS.pid=null;HL.pid=null;", 1),
 # the footer buttons walk the drawing one move at a time before leaving the page
 ("function move(d){\n  stopVoice();stopAI();",
  "function move(d){\n  stopVoice();stopAI();\n  if(boardOpen&&boardHasPhases(pg())&&!(steps(pg())[S.st]||{}).kind&&MS.pid===pg().id&&microGo(pg(),d)){render();return;}", 1),
 # the solution layer sits between the paper and the pen canvas; its controls head the right panel
 ("  var rp=right;\n", "  var rp=right;var sc=solutionCard(p,it);if(sc)rp.append(sc);\n", 1),
 # from a lesson step, one button opens the board on this step
 ("  tex(right);\n  right.append(askBox(p,s));", "  tex(right);\n  if(st.length&&p.type!=='idea')right.append(el('div',{class:'tools'},el('button',{class:'btn',type:'button',text:u('Step through it on paper'),onclick:toggleBoard})));\n  right.append(askBox(p,s));", 1),
 ("JSON.stringify({strokes:B.strokes,items:B.items})", "JSON.stringify({strokes:B.strokes,items:B.items,paper:B.paper,paperSet:B.paperSet})", 1),
 ("  bar.append(clr);\n",
  "  bar.append(clr);\n"
  "  if(p.visual&&!(it&&it.kind))[['work','Working'],['graph','Graph']].forEach(function(v){bar.append(el('button',{class:'btn tiny',type:'button','aria-pressed':VW===v[0]?'true':'false',text:u(v[1]),onclick:function(){MS.view=v[0];MS.pid=p.id;renderBoard(p,it);}}));});\n"
  "  bar.append(el('span',{class:'bdpn',id:'bdPageNo'}));bar.append(zoomCtl());bar.append(notesButton(p));\n", 1),
 # the whiteboard takes all the room the panel has; its height in board units follows the panel's shape
 ("w=Math.min(availW,availH*BW/BH),h=w*BH/BW;", "w=availW,h=availH;BH=WBH=Math.round(BW*h/w);var ik=document.querySelector('#bdOver svg');if(ik)ik.setAttribute('viewBox','0 0 '+BW+' '+BH);", 1),
 # zoom: the stage grows by BZ inside a scrolling window the size of the fitted sheet
 ("st.style.width=w+'px';st.style.height=h+'px';\n  var dpr=Math.min(window.devicePixelRatio||1,2);",
  "f.style.height=h+'px';f.style.overflow=BZ>1?'auto':'hidden';w*=BZ;h*=BZ;st.style.width=w+'px';st.style.height=h+'px';\n  var dpr=Math.min(window.devicePixelRatio||1,2,4096/Math.max(w,h));", 1),
 ("  fitBoard();paintItems();paintAI();\n}", "  fitBoard();wireZoom();paintItems();paintAI();paintNotes(p);\n}", 1),
 # Control AI: the board's AI is replaced by the one in control415.js (highlights, sticky notes, fixes)
 ("function askBoard(mode,text,p,it){", "function askBoard(mode,text,p,it){return askBoardAI(mode,text,p,it);}\nfunction askBoardOld(mode,text,p,it){", 1),
 # the More subject has its own page; the shared store starts after the first render
 ("  else if(p.type==='home')renderHome(p);", "  else if(p.type==='home')renderHome(p);\n  else if(p.type==='more')renderMore(p);", 1),
 ("  voiceLabel();tabs();render();\n", "  voiceLabel();tabs();render();dbStart();\n", 1),
 # the sheet shown: the working sheet (plain A4) or the graph paper, by the current move
 ("function renderBoard(p,it){\n  boardLoad(p);", "function renderBoard(p,it){\n  boardLoad(p);var VW=sheetView(p,it),PK='wb';BH=WBH||BH;", 1),
 ("cv.style.height=h+'px';\n  paintStrokes();", "cv.style.height=h+'px';\n  paintStrokes();paginateWork();", 1),
 ("stage.append(cv,over);", "stage.append(paperEl(PK),VW==='work'?workLayer(p,it):solutionLayer(p,it),cv,over);", 1),
 ("function cssInk(c){return getComputedStyle(document.documentElement)", "function cssInk(c){return getComputedStyle($('bdStage')||document.documentElement)", 1),
 ("'\\nThe board is '+BW+' wide by '+BH+' high, origin at the top left.",
  "'\\nThe board is a sheet of '+PAPER_NAMES[B.paper]+' paper (plain white, no grid), '+BW+' units wide by '+BH+' high, origin at the top left; 1 mm = '+(BW/PAPERS[B.paper].w).toFixed(2)+' units. When you sketch a graph, draw its axes with ticks and labels.", 1),
 ('@media (max-width:700px){\n',
  '.bdstage{background:none!important;--fg:#17211e;--ink-blue:#1f4fc4;--bad:#c0322b;--good:#14784f;--warn:#a86508;color:#17211e;box-shadow:0 2px 10px rgba(0,0,0,.18)}\n'
  '.bdpaper{position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none}\n'
  '.bdbar select{min-height:40px}.bdbar .swatch{--fg:#17211e;--ink-blue:#1f4fc4;--bad:#c0322b}\n'
  '.bdsol{position:absolute;z-index:1;pointer-events:none}\n'
  # the working sheet: handwriting on plain A4, the way the homework's text pages are written
  ".bdwork{position:absolute;z-index:1;pointer-events:none;overflow:hidden;font-family:'Patrick Hand',cursive;color:#2f3338;font-size:9px;line-height:1.3}\n"
  '.bdwork .wkin{transform-origin:0 0;will-change:transform}.bdstage{border-radius:12px}\n'
  '.bdwork .wkl.hl{background:rgba(255,212,59,.55);border-radius:4px;box-shadow:0 0 0 2px rgba(250,176,5,.55)}\n'
  '.bdwork .wkl.fixed{border-inline-start:3px solid #2b8a3e;background:rgba(64,192,87,.13)}.bdwork .wkl.fixed.hl{background:rgba(255,212,59,.55)}\n'
  '.bdsol .hlg path,.bdsol .hlg line,.bdsol .hlg polyline,.bdsol .hlg circle,.bdsol .hlg rect,.bdsol path.hlg,.bdsol line.hlg,.bdsol polyline.hlg{stroke:#e8590c!important;stroke-width:3.2px!important}.bdsol .hlg text,.bdsol text.hlg{fill:#e8590c!important;font-weight:700}\n'
  '#left{position:relative}.stickies{position:absolute;inset:0;pointer-events:none;z-index:6}\n'
  ".sticky{position:absolute;width:min(300px,40%);min-width:170px;pointer-events:auto;border-radius:4px 4px 10px 4px;box-shadow:0 6px 18px rgba(0,0,0,.28);color:#2b2b2b;font-family:'Patrick Hand',cursive;font-size:1.02rem;line-height:1.3;transform:rotate(-.6deg)}\n"
  '.sticky.sy{background:#fff3a8}.sticky.sp{background:#ffd6e7}.sticky.sb{background:#d0ebff}.sticky.sg{background:#d3f9d8}\n'
  '.sthd{display:flex;align-items:center;gap:6px;padding:5px 8px;cursor:grab;border-bottom:1px solid rgba(0,0,0,.08);touch-action:none}.sthd b{flex:1;font-size:.95rem}\n'
  '.stx{border:0;background:none;font-size:1.2rem;line-height:1;cursor:pointer;color:#555;min-width:28px;min-height:28px}.stbd{padding:6px 10px 10px}.stbd math,.sttex math{color:#222}.sttex{margin-top:4px;overflow-x:auto}\n'
  '.bdfixes{border-top:1px solid var(--line);margin-top:8px;padding-top:8px;display:grid;gap:6px}.fxrow{font-size:.85rem}.fxold{color:var(--muted);text-decoration:line-through;font-size:.8rem}\n'
  '.moredrop{display:grid;gap:4px;place-items:center;text-align:center;border:2px dashed var(--accent);border-radius:12px;padding:28px 16px;margin:12px 0;cursor:pointer;background:var(--raised)}\n'
  '.moredrop:focus-within{outline:2px solid var(--accent)}.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}\n'
  '.morelog{display:grid;gap:4px;font-size:.88rem}.mline.good{color:var(--good)}.mline.bad{color:var(--bad)}.morelist{display:grid;gap:6px;margin-top:12px}\n'
  '.bdwork .wkb{padding:.25em 0 .15em}.bdwork .wkhead{font-size:1.05em;color:#555a60;border-bottom:1px solid #c9ccd0;margin-bottom:.2em}\n'
  '.bdwork .wkt{text-decoration:underline;text-underline-offset:.15em;margin:.15em 0 .1em}\n'
  '.bdwork .wkl{white-space:nowrap;overflow:hidden;padding:.08em 0 .08em .6em;color:#2f3338}\n'
  '.bdwork .wkl math,.bdwork .katex{font-size:1em;color:#2f3338!important}.bdwork *{--fg:#2f3338}.bdwork .wkn{font-style:italic}\n'
  '.bdwork .wkl.ans>span{display:inline-block;border:1.6px solid #2f49b0;border-radius:3px;padding:.05em .35em;color:#2f49b0}.bdwork .wkl.ans math,.bdwork .wkl.ans .katex{color:#2f49b0!important}\n'
  '.bdwork .now{animation:bdfade .7s ease both}.bdpn{font:600 .75rem var(--mono);color:var(--muted);align-self:center;margin-inline-start:.4rem}\n'
  '.bdcard .bdwarn,.bdcard .bdcheck{border-inline-start:3px solid var(--accent);padding-inline-start:.6rem;margin-top:.5rem}\n'
  '.qpic{display:block;width:100%;max-width:760px;height:auto;background:#fff;border:1px solid var(--line);border-radius:6px;margin:4px 0 8px}\n'
  '.bdfit{display:block!important;overscroll-behavior:contain}.bdfit>.bdstage{margin:0 auto;flex:none}.bdfit,.bdfit>.bdstage,.bdstage canvas{transition:none!important}.bdstage canvas.bdmove{cursor:grab}\n'
  '.bdzoom{display:inline-flex;gap:4px;align-items:center;margin-inline-start:.4rem}.bdzoom .bdpn{margin:0;min-width:3.2em;text-align:center}\n'
  '.qtyped{margin:4px 0}.qtyped summary{cursor:pointer;color:var(--muted);font-size:.85rem}\n'
  '.bdsol .visual{background:none;border:0;padding:0;height:100%;position:relative!important;--accent:#0b6e74;--tint:rgba(11,110,116,.14);--muted:#55635e;--line:#b8c3bd;--surface:transparent;--raised:transparent}\n'
  '.bdsol .visual svg{width:100%;height:100%;max-height:none!important}\n'
  # writing on the sheets looks like the homework: pencil handwriting, coloured pen for the constructions
  '.bdsol .visual{--fg:#45494e;--accent:#2f49b0;--muted:#5c6066}\n'
  ".bdsol .visual svg text{font-family:'Patrick Hand',cursive;font-weight:400!important;fill:#3d4146}\n"
  '.bdsol .visual svg .s,.bdsol .visual svg .f{stroke:#53575c}\n'
  '.bdsol .fresh{animation:bdfade .6s ease both}.bdsol path.fresh,.bdsol .fresh path,.bdsol line.fresh,.bdsol polyline.fresh,.bdsol .fresh polyline{stroke-dasharray:2400;stroke-dashoffset:2400;animation:bddraw 1.2s ease forwards}\n'
  '@keyframes bdfade{from{opacity:0}to{opacity:1}}@keyframes bddraw{to{stroke-dashoffset:0}}\n'
  '.bdsol .mdot{fill:var(--accent)}.mvlabel{font:600 .8rem var(--mono);color:var(--accent);margin:0}\n'
  '.bdcard{border:1.5px solid var(--accent);border-radius:10px;padding:12px;display:grid;gap:8px;background:var(--raised)}.bdcard h3{font-size:1.05rem}\n'
  '@media (prefers-reduced-motion:reduce){.bdsol .fresh,.bdsol .fresh path{animation:none;stroke-dasharray:none}}\n'
  '@media (max-width:700px){\n', 1),
]
if not WB:
    GRAPH = {
        "w=Math.min(availW,availH*BW/BH),h=w*BH/BW;": None,          # the sheet keeps its paper's shape
        "function renderBoard(p,it){\n  boardLoad(p);": "function renderBoard(p,it){\n  boardLoad(p);var VW=sheetView(p,it),PK=VW==='work'?'a4n':B.paper;BH=Math.round(BW*PAPERS[PK].h/PAPERS[PK].w);",
    }
    P2 = []
    for a, c, n in PATCH:
        if a in GRAPH:
            if GRAPH[a] is None:
                continue
            c = GRAPH[a]
        c = c.replace("u('Step through it on paper')", "u('Step through it on graph paper')")
        c = c.replace("' paper (plain white, no grid), '+BW+' units wide by '+BH+' high, origin at the top left; 1 mm = '+(BW/PAPERS[B.paper].w).toFixed(2)+' units. When you sketch a graph, draw its axes with ticks and labels.",
                      "' millimetre graph paper, '+BW+' units wide by '+BH+' high, origin at the top left; 1 mm = '+(BW/PAPERS[B.paper].w).toFixed(2)+' units, so a 10 mm grid square is '+(10*BW/PAPERS[B.paper].w).toFixed(1)+' units. Line graphs up with the grid when you draw axes.")
        if a == "  bar.append(clr);\n":
            c = c.replace("  bar.append(clr);\n", "  bar.append(clr);\n"
                "  var ps=el('select',{'aria-label':'Paper',title:'Paper'});Object.keys(PAPERS).filter(function(k){return k!=='wb';}).forEach(function(k){ps.append(el('option',{value:k,text:u(PAPER_NAMES[k])}));});ps.value=B.paper;\n"
                "  ps.onchange=function(){setPaper(ps.value);B.paperSet=true;boardSave();renderBoard(p,it);};bar.append(ps);\n", 1)
        P2.append((a, c, n))
    PATCH = P2
for a, c, n in PATCH:
    assert html.count(a) == n, (html.count(a), n, a[:90])
    html = html.replace(a, c)

# paper names in Arabic, through the player's UI dictionary
html = html.replace('var UI={', 'var UI={"Scroll up":"تمرير لأعلى","Scroll down":"تمرير لأسفل","Hide notes":"إخفاء الملاحظات","Show notes":"إظهار الملاحظات","Note":"ملاحظة","Corrected":"مصحّح","Corrected the solution":"صحّحت الحل","saved for everyone":"محفوظ للجميع","saved on this device":"محفوظ على هذا الجهاز","Corrections to this solution":"تصحيحات هذا الحل","was":"كان","Undo":"تراجع","More":"المزيد","More: your own questions":"المزيد: أسئلتك الخاصة","Upload question sheets":"ارفع أوراق الأسئلة","Your questions, solved like the course":"أسئلتك محلولة مثل المقرر","Solved uploads":"الأسئلة المحلولة","Fit":"ملاءمة","Pan":"تحريك الورقة","Drag the sheet around":"اسحب الورقة لتحريكها","Zoom in":"تكبير","Zoom out":"تصغير","Write the working":"اكتب خطوات الحل","Working":"الحل المكتوب","Graph":"الرسم","Page":"صفحة","A clean sheet of paper":"ورقة فارغة",'
                    '"Start like the exam: an empty sheet. Each press writes the next step of the working on the paper; this card explains why.":"ابدأ مثل الاختبار: ورقة فارغة. كل ضغطة تكتب الخطوة التالية من الحل على الورقة، وهذه البطاقة تشرح السبب.",'
                    '"A4 plain":"A4 عادية (بدون مربعات)","A4 portrait":"A4 عمودي","A4 landscape":"A4 أفقي","A3 portrait":"A3 عمودي","A3 landscape":"A3 أفقي",'
                    '"Previous step":"الخطوة السابقة","Hide solution":"أخفِ الحل","Show solution":"أظهر الحل",'
                    '"Step through it on paper":"حلّها خطوة بخطوة على الورقة","Step through it on graph paper":"حلّها خطوة بخطوة على ورق الرسم",'
                    '"Finish this step":"أكمل هذه الخطوة","Next move":"الحركة التالية","Previous move":"الحركة السابقة","Move":"الحركة","step":"الخطوة","Solution on the paper":"الحل على الورقة",'
                    '"Axes and scales":"المحاور والمقاييس","Mark three points of the curve":"حدّد ثلاث نقاط من المنحنى","Draw the curve through them":"ارسم المنحنى خلالها",'
                    '"Step off one stage":"ارسم stage واحدة","Plot a point":"ضع نقطة","Draw it":"ارسمها","Draw a line":"ارسم خطاً","Label it":"اكتب التسمية",'
                    '"Start like the exam: an empty sheet. Each press adds one move: the axes and scales, each given point, each curve (three points first, then the curve), then every line and stage of the solution.":"ابدأ مثل الاختبار: ورقة فارغة. كل ضغطة تضيف حركة واحدة: المحاور والمقاييس، ثم كل نقطة معطاة، ثم كل منحنى (ثلاث نقاط أولاً ثم المنحنى)، ثم كل خط وكل stage في الحل.",'
                    '"Axes and scales, the given data and the given points. Try the next move yourself with the pen, then press Next move to compare.":"المحاور والمقاييس، والبيانات والنقاط المعطاة. جرّب الحركة التالية بنفسك بالقلم، ثم اضغط الحركة التالية لتقارن.",'
                    '"empty paper":"ورقة فارغة","the foundation":"الأساس","A clean sheet of graph paper":"ورقة رسم بياني فارغة","The foundation":"الأساس",'
                    '"Start like the exam: an empty sheet. Next comes the foundation (axes, scales, the equilibrium data and the given points), then each step adds its own construction.":"ابدأ مثل الاختبار: ورقة فارغة. بعدها يأتي الأساس (المحاور، والمقاييس، وبيانات الـ equilibrium، والنقاط المعطاة)، ثم كل خطوة تضيف رسمها.",'
                    '"Axes and scales, the equilibrium data and the given points. Try the first move yourself with the pen, then press Next step to compare.":"المحاور والمقاييس، وبيانات الـ equilibrium، والنقاط المعطاة. جرّب أول خطوة بنفسك بالقلم، ثم اضغط الخطوة التالية لتقارن.",', 1)
open(out, 'w', encoding='utf8', newline='').write(html)
print('mode', 'whiteboard' if WB else 'graph paper', '| sections', [(s['id'], len(s['pages'])) for s in sections], '| derivations', len(derivs), '|', out)
