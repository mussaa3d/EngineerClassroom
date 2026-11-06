<p align="center"><img src="assets/logo.png" width="160" alt="Course Classroom logo: graph paper with stages stepped off between a curve and the diagonal, and a pencil"></p>

<h1 align="center">Course Classroom</h1>
<p align="center"><b>A Claude Code skill that turns a university course into an interactive study classroom.</b></p>


Turn a university course folder (professor's slides or notes, tutorials, homework, past exams, textbook) into one
interactive study classroom published on claude.ai:

- Ideas first, then every question solved step by step on paper, the way an undergraduate writes it.
- Real graph paper (A4/A3, portrait or landscape) or a zooming whiteboard with plotted graphs.
- An AI assistant that highlights, writes on sticky notes and corrects wrong solution lines.
- A "More" tab that solves uploaded question sheets.

## Install

**The easy way: ask Claude.** In Claude Code, paste this repository's link and say **"install skill"**, or say
"install the skill from https://github.com/<owner>/course-classroom". Claude follows the steps in the
[Instructions for Claude](#instructions-for-claude-installing-this-skill) below.

**By hand:**
```bash
git clone https://github.com/<owner>/course-classroom
```
```bash
cd course-classroom
```
```bash
python install.py
```
Then restart Claude Code. Use `python install.py --project` to install into the current project only, or
`python install.py --check` to see what is installed. Run it again after a `git pull` to update.

**As a Claude Code plugin:** this repository is also a plugin marketplace.
```
/plugin marketplace add <owner>/course-classroom
```
```
/plugin install course-classroom@course-classroom
```
Plugins don't run the installer. After installing the plugin, run the installer anyway (or install the Python
packages in `requirements.txt` yourself).

## Use
Say **make a classroom for "C:\path\to\my course"**, or type `/course-classroom`. Claude asks a few questions first,
then builds, tests and publishes the classroom. The full walkthrough is in [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

## What's inside
```
skills/course-classroom/
  SKILL.md        the workflow Claude follows (questions first, then prepare → inventory → write → build → test → publish)
  engine/         the classroom player, the graph-paper and whiteboard boards, the AI assistant, the builder
  tools/          source preparation, question pictures, page validators, graph-sheet renderer, page walker
  briefs/         the authoring guide, the question-inventory brief, the solving-style template
  examples/       example pages and example course settings for both paper styles
install.py        installer (copies the skill, installs Python packages, checks for Word/LibreOffice, prints the walkthrough)
docs/             getting started
```

## Requirements
- Claude Code, with access to Artifacts (to publish the classroom)
- Python 3.9+ (the installer adds pymupdf, pillow, numpy, scipy, sympy)
- Optional: Microsoft Word/PowerPoint (Windows) or LibreOffice, to read the equations in .doc/.docx/.ppt files

---

## Instructions for Claude: installing this skill
When a user gives you this repository (a link or a local folder) and asks to install it:

1. **Clone it.** Clone into a short folder in your scratchpad or the user's home, for example:
   ```bash
   git clone --depth 1 https://github.com/<owner>/course-classroom ~/course-classroom-src
   ```
   If git is missing, download the repository ZIP from GitHub and unzip it. Use the user's link, not the
   placeholder above.
2. **Read before running.** Read `install.py` before running it. It only copies `skills/course-classroom` into
   `~/.claude/skills/`, pip-installs the packages in `requirements.txt`, and checks for Word/LibreOffice.
3. **Run the installer** with the same Python the user uses:
   ```bash
   python install.py
   ```
   Add `--project` if the user wants it only in the current project. If pip fails, show the user the command the
   installer printed.
4. **Report what the installer checked.** Tell the user what is installed, and anything marked `[!!]`, such as no Word
   or LibreOffice.
5. **Tell them to restart.** Claude Code picks up new skills in a new session.
6. **Walk them through using it.** Base this on `docs/GETTING_STARTED.md`:
   - Where to put their course files.
   - The exact sentence to start: make a classroom for "<their folder>".
   - The questions they will be asked.
   - How long it takes.
   - What the finished classroom does.

   Keep it short, then offer to start on their course right away.
