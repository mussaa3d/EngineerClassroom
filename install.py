"""Installs the course-classroom skill for Claude Code.

    python install.py              install for this user  (~/.claude/skills/course-classroom)
    python install.py --project    install into this folder's project (.claude/skills/course-classroom)
    python install.py --target DIR install into DIR/course-classroom
    python install.py --no-deps    skip installing the Python packages
    python install.py --check      only check what is installed, change nothing

It copies the skill, installs the Python packages the tools use (pymupdf, pillow, numpy, scipy, sympy), checks for a
way to convert Word/PowerPoint files (Microsoft Office on Windows, or LibreOffice), and prints how to use the skill.
Run it again to update: the old copy is replaced (a backup is kept next to it as course-classroom.bak)."""
import argparse, os, shutil, subprocess, sys

NAME = 'course-classroom'
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'skills', NAME)
PKGS = ['pymupdf', 'pillow', 'numpy', 'scipy', 'sympy']
IMPORTS = {'pymupdf': 'pymupdf', 'pillow': 'PIL', 'numpy': 'numpy', 'scipy': 'scipy', 'sympy': 'sympy'}

def ok(msg): print('  [ok]  ' + msg)
def warn(msg): print('  [!!]  ' + msg)

def missing_packages():
    out = []
    for pkg, mod in IMPORTS.items():
        r = subprocess.run([sys.executable, '-I', '-c', 'import ' + mod], capture_output=True)
        if r.returncode:
            out.append(pkg)
    return out

def office_converter():
    if os.name == 'nt':
        ps = "try{$w=New-Object -ComObject Word.Application;$w.Quit();'word'}catch{''}"
        r = subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, text=True)
        if 'word' in r.stdout:
            return 'Microsoft Word'
    for exe in ('soffice', 'libreoffice'):
        if shutil.which(exe):
            return 'LibreOffice'
    return None

def main():
    a = argparse.ArgumentParser(description='Install the course-classroom skill for Claude Code.')
    a.add_argument('--project', action='store_true', help='install into ./.claude/skills of the current folder')
    a.add_argument('--target', help='install into TARGET/course-classroom')
    a.add_argument('--no-deps', action='store_true', help='do not pip-install the Python packages')
    a.add_argument('--check', action='store_true', help='only report what is installed')
    o = a.parse_args()

    if not os.path.exists(os.path.join(SRC, 'SKILL.md')):
        sys.exit('Run this from the repository folder (skills/course-classroom/SKILL.md not found next to install.py).')
    if o.target:
        base = os.path.abspath(o.target)
    elif o.project:
        base = os.path.join(os.getcwd(), '.claude', 'skills')
    else:
        base = os.path.join(os.path.expanduser('~'), '.claude', 'skills')
    dst = os.path.join(base, NAME)

    print('\nCourse classroom skill\n')
    if sys.version_info < (3, 9):
        warn('Python %d.%d found; Python 3.9 or newer is needed.' % sys.version_info[:2])
    else:
        ok('Python %d.%d' % sys.version_info[:2])

    if not o.check:
        os.makedirs(base, exist_ok=True)
        if os.path.exists(dst):
            bak = dst + '.bak'
            if os.path.exists(bak):
                shutil.rmtree(bak)
            shutil.move(dst, bak)
        shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        ok('skill installed in ' + dst)
    else:
        (ok if os.path.exists(os.path.join(dst, 'SKILL.md')) else warn)('skill ' + ('found in ' if os.path.exists(dst) else 'not installed in ') + dst)

    miss = missing_packages()
    if miss and not o.no_deps and not o.check:
        print('  ...   installing Python packages: ' + ', '.join(miss))
        r = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade'] + miss)
        if r.returncode:
            warn('pip could not install them; run:  %s -m pip install %s' % (sys.executable, ' '.join(miss)))
        miss = missing_packages()
    if miss:
        warn('missing Python packages: ' + ', '.join(miss) + '  (python -m pip install ' + ' '.join(miss) + ')')
    else:
        ok('Python packages: ' + ', '.join(PKGS))

    conv = office_converter()
    if conv:
        ok('Word/PowerPoint files are converted with ' + conv)
    else:
        warn('no Microsoft Word or LibreOffice found: .doc/.docx/.ppt files can only be read as text '
             '(install LibreOffice to read their equations and figures)')

    print(open(os.path.join(HERE, 'docs', 'AFTER_INSTALL.txt'), encoding='utf8').read())

if __name__ == '__main__':
    main()
