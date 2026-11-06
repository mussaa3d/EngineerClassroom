"""Prepares a course's source files for reading: every file gets a short ASCII code, is copied to <work>/<code>.<ext>,
Word files are converted to PDF (Microsoft Word on Windows, or LibreOffice), every page is rendered to
<work>/img/<code>/pNN.png (photos copied as p01.jpg) and its text layer saved to <work>/txt/<code>.txt.
Writes <work>/manifest.json {code: original relative path} and prints one line per file (pages, characters, SCAN when
the PDF has no text layer — those must be read from the PNGs).
Usage: python -I -X utf8 prepare.py <source folder> <work folder> [--skip "textbook name part" ...]
Keep <work> short and ASCII (e.g. C:\\cw\\che415): long or Arabic paths break Word and some PDF tools."""
import glob, json, os, re, shutil, subprocess, sys
import pymupdf

src, work = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
skip = [a for i, a in enumerate(sys.argv[3:]) if i > 0 and sys.argv[3:][i - 1] == '--skip']
os.makedirs(os.path.join(work, 'img'), exist_ok=True)
os.makedirs(os.path.join(work, 'txt'), exist_ok=True)
AR = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')

def code_for(rel, taken):
    parts = [re.sub(r'[^A-Za-z0-9]+', '', p.translate(AR)) for p in rel.split(os.sep)]
    folder = ''.join(p[:3] for p in parts[:-1] if p)[:9]
    base = re.sub(r'[^A-Za-z0-9]+', '', os.path.splitext(rel.split(os.sep)[-1])[0].translate(AR))[-14:] or 'f'
    c = (folder + '_' if folder else '') + base
    while c in taken:
        c += 'x'
    return c

man = {}
for p in sorted(glob.glob(os.path.join(src, '**', '*'), recursive=True)):
    rel = os.path.relpath(p, src)
    ext = os.path.splitext(p)[1].lower()
    if os.path.isdir(p) or ext not in ('.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.ppt', '.pptx') or any(s.lower() in rel.lower() for s in skip):
        continue
    c = code_for(rel, man)
    man[c] = rel
    shutil.copy(p, os.path.join(work, c + ext))
json.dump(man, open(os.path.join(work, 'manifest.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)

# Word and PowerPoint -> PDF
office = [f for f in glob.glob(os.path.join(work, '*')) if os.path.splitext(f)[1].lower() in ('.doc', '.docx', '.ppt', '.pptx')]
if office:
    ps = r'''$w=$null;$p=$null
foreach($f in $args){$o=[IO.Path]::ChangeExtension($f,'.pdf');$e=[IO.Path]::GetExtension($f).ToLower()
 try{ if($e -like '.doc*'){ if(-not $w){$w=New-Object -ComObject Word.Application;$w.Visible=$false;$w.DisplayAlerts=0}; $d=$w.Documents.Open($f,$false,$true);$d.SaveAs([ref]$o,[ref]17);$d.Close([ref]0) }
      else { if(-not $p){$p=New-Object -ComObject PowerPoint.Application}; $d=$p.Presentations.Open($f,$true,$false,$false);$d.SaveAs($o,32);$d.Close() }
      "ok $f" } catch { "FAIL $f $($_.Exception.Message)" } }
if($w){$w.Quit()};if($p){$p.Quit()}'''
    done = False
    if os.name == 'nt':
        r = subprocess.run(['powershell', '-NoProfile', '-Command', ps] + office, capture_output=True, text=True)
        print(r.stdout.strip()); done = 'ok ' in r.stdout
    if not done:
        so = shutil.which('soffice') or shutil.which('libreoffice')
        if so:
            subprocess.run([so, '--headless', '--convert-to', 'pdf', '--outdir', work] + office, capture_output=True)
        else:
            print('WARNING: no Word/PowerPoint or LibreOffice to convert', len(office), 'office files; read them as text only')

# render every page, save text
for f in sorted(glob.glob(os.path.join(work, '*.pdf'))):
    c = os.path.splitext(os.path.basename(f))[0]
    d = pymupdf.open(f); os.makedirs(os.path.join(work, 'img', c), exist_ok=True)
    txt = []
    for i, pg in enumerate(d):
        pg.get_pixmap(dpi=110).save(os.path.join(work, 'img', c, f'p{i + 1:02d}.png'))
        txt.append(f'=== page {i + 1} ===\n' + pg.get_text())
    open(os.path.join(work, 'txt', c + '.txt'), 'w', encoding='utf8').write('\n'.join(txt))
    chars = sum(len(t) for t in txt) - 16 * len(txt)
    print(f'{c:28s} {d.page_count:4d} pages {chars:8d} chars' + ('  SCAN' if chars < 80 * d.page_count else '') + '   <- ' + man.get(c, ''))
for f in glob.glob(os.path.join(work, '*.jp*g')) + glob.glob(os.path.join(work, '*.png')):
    c = os.path.splitext(os.path.basename(f))[0]
    os.makedirs(os.path.join(work, 'img', c), exist_ok=True)
    shutil.copy(f, os.path.join(work, 'img', c, 'p01' + os.path.splitext(f)[1].lower()))
    print(f'{c:28s}    1 photo                SCAN   <- ' + man.get(c, ''))
