# Course classroom — authoring guide for one subject (read all of it before writing)

You write ONE subject of an interactive study classroom for a university course. Students use it as their whole
course resource, so it must teach from zero to exam level, clearly and correctly. The page engine already exists;
you only write data (JSON). `<SKILL>/examples/examples.json` holds real pages — copy their structure exactly.

Your brief names: the course folder (COURSE), the work folder with the prepared sources (WORK: WORK\img\<code>\pNN.png,
WORK\txt\<code>.txt, WORK\manifest.json), your subject id (SID), its title, the page ranges of the professor's
material for your subject, the PAPER MODE ("graph" or "whiteboard"), the paper for your subject (graph mode), the
inventory file(s) of questions, and COURSE\STYLE.md (how the course's students write solutions). Run Python as
`python -I -X utf8`; keep paths short.

## The rules the user set (they apply to every course)
1. The PROFESSOR'S MATERIAL (slides, chapter notes) is the main resource: teach in his order, with his notation and
   methods. Everything from him must be in the classroom. Textbooks only support; never contradict the professor
   (if they disagree, follow him and add a `check` note).
2. Each subject runs: IDEAS (interactive, no paper) → the professor's own questions (his tutorials/homework/examples,
   solved on paper) → questions of the SAME TYPE from past exams and the textbook (solved on paper) → QUIZZES.
   Anything that is not the professor's and not the same type as his questions is left out.
3. Every question is a fully solved `worked` page in the "undergraduate solving" style of STYLE.md (below).
4. Questions are shown as a picture of the original sheet (the builder crops it from `qpic`); the typed text sits
   under it. Never put pictures of copyrighted textbook pages: textbook questions are rephrased text only.
5. Titles: 2–5 plain English words naming the system/method ("Benzene–toluene system", "Fenske–Underwood question",
   "Routh test, third order"). No `title_ar`. Chips name the source: "Tut 3 · Q1", "HW 2 · Q4", "Final 1442 · Q3",
   "Mid 1 · Q2", "Example 4", "Ex 12" (textbook exercise), "New Tut 5 · Q2".
6. Solve EVERY number with Python (numpy/scipy/sympy). Where a model answer, the homework or the notes are wrong, use
   the correct value and say so in a `check` box ("The key writes 3s+1; τ = 30 s, so it is 30s+1."). If data are
   missing, state a labelled assumption in the question ("Data used: …") and in a check box.
7. BILINGUAL: every teaching/answer text has an Arabic twin `<field>_ar` (Saudi-friendly MSA; technical terms,
   symbols, formulas and numbers stay English; wrap formula fragments in <bdi dir="ltr">…</bdi> inside HTML; plain
   strings stay plain). Needs `_ar`: step `title`, `say`, `warn`, `check`; classmate `q_ar`/`a_ar`; question `explain`;
   `model` (wrapped in <div dir="rtl" style="text-align:right">…</div>); tftable rows with a note get a 4th element.
   Questions (`q`, `options`, `rows[0]`, `t1`, `t2`, `cells.label`, page `question`) stay English only.
   (If the course is not bilingual, the brief says so: then omit every `_ar`.)

## What your subject contains (the builder keeps this order)
1. IDEA pages (3–8): every concept in the professor's pages for the subject, in his order. Each: an SVG visual with
   steps that highlight its parts (`hi`), 1–3 steps, 3–5 check questions (mc / tf / num / match).
2. WORKED pages, professor first: every example in his notes ("Example n"), every exercise in his notes, every
   tutorial/homework question of the subject (from the inventory; skip `dup_of`, name the duplicate in `source`).
3. WORKED pages for every past-exam question of the subject, and every textbook worked example/exercise of the SAME
   TYPE as his questions (only if the brief includes the textbook). Easiest → hardest inside each group.
   A question whose parts belong to different subjects: solve only your parts and say where the rest is.
4. QUIZ pages: one Concept quiz (tftable 10–20 rows, numbered matching 8–10, 1–2 written) based on statements in
   his material; Solving quiz pages (table/num, final answers only, ≤ 4 per page) from the questions you solved.
5. DERIVATIONS (1–4, the "derivations" list): the key derivations as he presents them, one algebra move per step.
Ids: "<SID>-idea-1", "<SID>-ex1" (his examples), "<SID>-tut3-q1", "<SID>-hw2-q4", "<SID>-f422-q3" (exam code
lower-case), "<SID>-tb12" (textbook), "<SID>-concepts", "<SID>-solving-1", "<SID>-d1".

## ANSWER STYLE — the undergraduate solving part
Every worked page is solved the way a good student writes it on paper in the exam (COURSE\STYLE.md describes the
course's own students; if the course has solved homework, follow it exactly: same order, same equations, same layout):
- Step 1 "Data": every given value with its symbol, the assumptions, and what is asked ("Find: …").
- One step per block of work. Each equation is one KaTeX line, the substitution with numbers on the next line, then
  the result. Readings from a graph are written "from graph: x = 0.287" and checked by calculation.
  Trial-and-error: show each trial as its own line and say it is trial and error, and how the next guess is chosen.
- Final answers: {"ans": "…"} lines with units (they render boxed).
- Multi-part questions: step titles start with the part label "(a) …"; cases in the order of the question.
- `say`/`say_ar`: short plain words — WHAT the step does and WHY (shown beside the paper; the lines are what is
  written ON the paper). `warn` where students slip; `check` for verification or corrections.

## PAPER — two modes (the brief says which)
### graph mode (real millimetre graph paper, like a homework graph sheet)
The written working goes on a plain A4 "working sheet"; the drawing goes on graph paper. Papers: a4p (A4 portrait pad,
grid from x=13 mm, y=22 mm), a4l (A4 landscape pad, grid from x=22, y=12), a3p / a3l (A3 sheet, grid from 10 mm,
10 mm). Use the paper the brief gives for your subject (or the paper the course's homework uses for that question).
- Graph pages: `"paper": "<a4p|a4l|a3p|a3l>"`, `"sheet": true`, and a `visual` that is the WHOLE SHEET:
  `<svg viewBox="0 0 4W 4H">` with W×H the sheet in mm (a4p "0 0 840 1188", a4l "0 0 1188 840", a3p "0 0 1188 1680",
  a3l "0 0 1680 1188"): 4 units = 1 mm, origin at the sheet's top-left. Axes on whole-cm grid lines, at the scale and
  place the homework uses (e.g. x and y from 0 to 1 over 10 cm, 40 units per cm). Same tick labels, axis names and
  readings the students write. Check: `python -I -X utf8 <SKILL>/tools/sheetview.py <file> <page id> out.png` and look.
- Pages without a graph: no visual, plain A4 working only.
- If the QUESTION comes with its own printed graph (a chart to read from), do not use graph paper: the visual is that
  picture (`<image href="data:image/jpeg;base64,…">`, grey JPEG ~1000 px, unkeyed) with the construction drawn over it
  in the picture's own axis coordinates (calibrate from tick labels; verify on a printed point), `"paper": "a4n"`.
- Correlation charts (e.g. Gilliland) are shown as the chart picture with the reading drawn on it.
### whiteboard mode (adaptive whiteboard, plain white, no graph paper)
Every sheet is plain white and the board fills the screen; the builder sets the paper. Whenever the solution has or
needs a graph or diagram (responses, curves, pole maps, block diagrams, process sketches, P&IDs, reaction curves …)
the `visual` is that figure as a proper plot: `viewBox="0 0 600 H"` (H 170–420), axes with ticks and tick labels,
axis names with units, curves from REAL computed points, key points marked and labelled. No `sheet`, no `paper`.
If the question gives a graph, redraw it faithfully from the picture and solve on it.

### Both modes: how the board builds the drawing
The board shows: empty sheet → the foundation (elements with no `data-k`: axes, ticks, given data) → each step's
elements in order (curves are drawn after three dots). So put `data-k="key"` on every element a step adds, list the
key in that step's `hi`, and order elements in the order the student draws them. Staircases (stage steps) are ONE
path of M/H/V (or L) segments. Classes the engine styles: "s" stroke, "f" fill, "soft" faint helper, "a" arrowhead,
"m" muted text, "tag" bold text. `<text data-v="key">?</text>` is replaced by a step's `set:{"key":"value"}`.
No inline colours or fonts except style="stroke:var(--accent)". Arrowheads: a <marker id="<pageid>-a"> in <defs>
(ids unique per page). Text 13 units (graph sheets: 13 ≈ 3.3 mm handwriting; tick labels may use font-size 11px).

## Page format (copy examples.json)
- idea: {id, type:"idea", chip:"Idea n", title, visual?, steps:[1–3], questions:[3–5 mc/tf/num/match]}
- worked: {id, type:"worked", chip, level:"Easy|Easy+|Medium|Medium+|Hard|Hardest|Exam", title, source, question
  (HTML, English), visual?, paper?, sheet?, qpic?: [["<code>", page, top, bottom], …] (code from WORK\manifest.json,
  page 1-based, top/bottom as fractions of the page height — copy them from the inventory; for the professor's notes
  measure them on the page PNG), steps:[{title, title_ar, lines:[…], say, say_ar, hi?, set?, warn?, check?, classmate?}]}
  `lines`: KaTeX strings (\dfrac, \text{}); final answers {"ans":"…"}. Never write `\,'` (a prime after a thin space).
- quiz: {id, type:"quiz", mode:"concept"|"solving", chip, title, questions:[…]}; concept kinds tftable {head,marks,
  source,q,rows}, numbered {head,marks,source,q,t1,t2}, written {head,marks,source,q,model,model_ar,rubric}; solving
  kinds table {head,marks,source,q,useful?,cells:[{label,answer,unit,dp,tol?}]}, num {q,answer,unit,dp,tol}.
- idea questions: mc {q,options,answer,explain,explain_ar}, tf {q,answer,explain,explain_ar}, num {q,answer,unit,dp,tol?},
  match {q,pairs,explain,explain_ar}.

## Output and checks
Write COURSE\author\<SID>.json = {"section": {"id","title","short","pages":[…]}, "derivations":[…], "notes":"…"}.
(Extra question pages written by a second writer go in COURSE\author\<SID>_x1.json, same format.)
Validate: `python -I -X utf8 <SKILL>/tools/validate.py COURSE\author\<SID>.json` → fix every error.
Graph mode sheet pages also: `python -I -X utf8 <SKILL>/tools/vt.py <file>` (checks sheet viewBoxes; for a file in
the {sid: [pages]} format) and render pages with sheetview.py to check them by eye.
Reply briefly: pages by type; every question covered (ids); anything not covered and why; answers you corrected;
assumptions you made.
