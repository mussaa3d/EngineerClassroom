---
name: course-classroom
description: Turn a university course's folder (the professor's slides or chapter notes, tutorials, homework, past exams, textbooks) into one interactive study classroom published as an Artifact. Each subject runs ideas, then every tutorial, homework and exam question solved step by step on paper the way an undergraduate writes it, then quizzes and derivations. Graphs go on real graph paper (A4/A3, portrait/landscape) or on an adaptive whiteboard, with an AI assistant that highlights, writes sticky notes and fixes solutions, plus a "More" subject that solves uploaded question sheets. Use when the user wants a classroom, course artifact, study site or "the same package" for a subject or course.
---

# Course classroom

Builds the same kind of classroom as CHE 409 (Separation Processes, graph-paper mode) and CHE 415 (Process Control,
whiteboard mode): one self-contained HTML page with a player, a step-by-step solution board, an AI assistant and the
course's own questions. Everything that makes the result look and behave the same is in this folder; follow the steps
in order and every course comes out the same way.

SKILL = this folder (`~/.claude/skills/course-classroom`):
- `engine/` — `template.html` (the player), `board-paper.js` (graph-paper board), `board-whiteboard.js` (adaptive
  whiteboard), `ai.js` (board AI: highlights, sticky notes, fixes; the More subject), `build.py` (the builder),
  `home.default.json`.
- `tools/` — `prepare.py` (sources → codes, PDFs, page PNGs, text), `qpics.py` (question pictures), `validate.py` and
  `vt.py` (page checks), `sheetview.py` (render a graph-paper page), `testhook.py` + `walk.js` (step every page).
- `briefs/` — `GUIDE.md` (authoring guide for subject writers), `INVENTORY.md` (question inventory brief),
  `STYLE.template.md` (how students write solutions).
- `examples/` — `examples.json` (real pages of every type), `course.graph.example.json`, `course.whiteboard.example.json`.

## When the user has just installed the skill, or asks how to use it
Walk them through it briefly (from `docs/GETTING_STARTED.md` in the repository; the same points are here):
1. Put the course in one folder: the professor's slides/notes (the main resource), tutorial/homework sheets, past
   exams (scans and photos are fine), optionally a solved homework and the textbook.
2. Say: make a classroom for "<that folder>" (or /course-classroom).
3. You will be asked first: the main resource, graph paper (A4/A3 like the homework) or whiteboard with plotted
   graphs, the subject list and order, what to include, the names (course, professor, assistant), and the More tab.
4. Then everything is read, sorted, written, built, tested and published as an Artifact; a full course often takes one
   to a few hours. You get the link plus the corrections and assumptions made.
5. In the classroom: subjects run ideas → professor's questions → same-type questions → quizzes; Next move writes and
   draws each solution; zoom/scroll; the assistant highlights, writes sticky notes and fixes wrong lines; More solves
   uploaded sheets; English/عربي switch.
Then offer to start on their course. Do not start reading a course before they give the folder and answer Step 0.

## Step 0 — ask the user first (AskUserQuestion), before reading anything big
Only ask what the request and the folder don't already answer, and ask it all up front (several questions per call).
Confirm, with your recommendation first:
1. **Sources.** The course folder; which file or folder is the professor's MAIN resource (slides/notes); which are the
   tutorials/homework, the exams, and any student's solved homework; textbooks to use for same-type questions, or none.
2. **Paper style.** "Graph paper like the homework" (graph mode: A4/A3, portrait/landscape per subject, like CHE 409)
   or "Whiteboard with plotted graphs" (whiteboard mode: adaptive board, plain white, like CHE 415). In graph mode:
   which paper per subject (read the student's graph sheets if there are any; otherwise propose A4 portrait for x–y
   plots and ask about A3/landscape subjects), and subjects that have no graphs (plain A4).
3. **Subjects.** Propose the subject list and order from the professor's chapters/slides (names as he uses them, e.g.
   "McCabe–Thiele method", "Ponchon–Savarit method", "Multicomponent"); ask to confirm, merge or split.
4. **Scope.** Keep only the professor's material + questions of the same type? Include the textbook's worked
   examples/exercises of the same type? Past exams: all, or some years? Arabic teaching twin on/off?
5. **Names.** Course code/title, the professor's name as it should appear, the AI assistant's name (e.g. "Design AI",
   "Control AI"), and whether to add the More (upload your own questions) subject.
Anything that differs for a particular question (a printed chart to draw on, a sheet that uses a different paper,
missing data) is asked when you find it, with a recommended default.

## Step 1 — prepare the sources
```
python -I -X utf8 SKILL/tools/prepare.py "<course folder>" C:\cw\<course> --skip "<textbook file name part>" …
```
Use a short ASCII work folder. Large textbooks are skipped here and read on demand with pymupdf (render the needed pages
to PNG). It prints SCAN for files with no text layer: those are read from the PNGs. Create the course folder
(e.g. C:\cw\<course>\course\) with `course.json` (copy an example and fill in the user's answers), `facts.txt`
(one paragraph: code, professor, topics in order, grading, textbooks) and `author\`.

## Step 2 — inventory every question (subagents, in parallel, by file group)
Brief 2–3 agents with `SKILL/briefs/INVENTORY.md`, the subject ids with one line each, which files are the professor's,
and their share of the codes (e.g. finals / midterms+homework / tutorials). Output: WORK\inv\<name>.json. If a solved
homework exists, turn the agents' description of it into COURSE\STYLE.md (from STYLE.template.md); otherwise write it
from the user's answers and the examples there.

## Step 3 — write the subjects (subagents, one per subject or pair of small subjects; split a subject with many
## exam questions between two writers: teaching + homework in <sid>.json, exam questions in <sid>_x1.json)
Each brief: read `SKILL/briefs/GUIDE.md` and COURSE\STYLE.md; COURSE, WORK, SID, title/short, the page ranges of the
professor's material for the subject (look them up first: list the PDF's pages with their first lines), the paper
mode and paper, the inventory files and which subjects they cover, what to include from the textbook, and anything the
user said about particular questions. Keep writers on separate files. While they run, nothing else edits author\.
When a writer reports, read its notes: corrections to model answers and assumptions go to the user at the end.

## Step 4 — build
```
python -I -X utf8 SKILL/tools/qpics.py <COURSE> <WORK>          # question pictures (check a few PNGs in COURSE\img\qpic)
python -I -X utf8 SKILL/engine/build.py <COURSE> <COURSE>\<id>.html
```
The page must stay under 16 MB: if it is close, shrink pictures in qpics.py (width 860, JPEG quality 50).

## Step 5 — test every page (never publish untested)
```
python -I -X utf8 SKILL/tools/testhook.py <COURSE>\<id>.html <served folder>\test.html
```
Serve the folder (`python -I -m http.server 8766 --bind 127.0.0.1`, in the background), open test.html in the built-in
browser, paste `SKILL/tools/walk.js` and run `__walk(a,b)` in slices (or the async loop that does 5 pages at a time):
every page must report `errs: []`. Graph mode: also run `python -I -X utf8 SKILL/tools/gridcheck.py <built.html>`. Every sheet drawing must sit inside the printed grid with its axes on whole-cm lines. Fix a page with `tools/resheet.py` (edit its TARGET list), which moves or rescales every coordinate, then render it with sheetview.py to confirm. Then look at a few pages: a graph page at its start, middle and end; a long
working sheet; the More page. Fix in the subject file (or engine) and rebuild.

## Step 6 — publish
Copy the HTML into the session folder and publish it with the Artifact tool (first publish: an icon, a one-line
description, `capabilities: {"sample": {"images": true}, "db": {}}` — sample is the AI, db stores corrections and More
uploads for everyone the owner lets edit). Updates: publish the same file path. Tell the user what is in it per
subject (pages, questions covered), every corrected model answer, every assumption, and anything left out and why.

## What the finished classroom does (so you can describe and keep it)
- Ideas: interactive visual + checks; worked pages open on the board: an empty sheet, then the foundation, then one
  move per press (each step first writes its working on the sheet, then draws; curves after three dots; staircases
  one stage per press); the card beside it explains why; Working/Graph buttons switch sheets.
- Graph mode: real mm graph paper (A4 pad with binding strip, A3 loose sheet), a paper picker, A4 working sheets paged.
  Whiteboard mode: the board fills the panel; the drawing's camera zooms to what is drawn so far; the working zooms
  out as lines are added (min 80%), then scrolls (wheel, two fingers, Pan, ▲▼) and follows the newest line.
- Zoom anywhere on every sheet (− + Fit, Ctrl+wheel, pinch); Pan tool; pen, eraser, undo.
- The AI ("Check my work", "Show me on the board", chat): highlights the solution lines / drawing parts it explains,
  writes on draggable sticky notes (Hide/Show notes), and corrects a wrong solution line itself (saved in the shared
  store, listed with Undo). Quiz questions: hints only.
- More: upload PDF / Word / photos → every question solved into its own page the same way, saved in the classroom.
- English/Arabic switch for all teaching; questions stay English; titles stay English.

## Changing a finished classroom later
Edit the subject JSON (or the engine for behaviour), rebuild, walk-test, publish the same file. Corrections the AI saved
live in the artifact's store (`fixes/<page id>`): read them with the ArtifactData tool and fold them into the subject
files when the user asks.
