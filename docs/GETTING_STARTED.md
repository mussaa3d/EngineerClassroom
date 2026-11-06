# Getting started with the course classroom skill

The skill turns a university course folder into one interactive study classroom: a single page on claude.ai where
every subject is taught from the professor's material and every question is solved step by step the way a student
writes it on paper.

## 1. Get your course folder ready
Put everything in one folder (sub-folders are fine):

| What | Examples | Needed? |
|---|---|---|
| The professor's main material | slide decks, chapter notes (PDF, Word, PowerPoint) | yes |
| Tutorial / homework sheets | `Tutorial 3.pdf`, `HW2.docx` | recommended |
| Past exams | midterms and finals; scans and phone photos are fine | recommended |
| A student's solved homework | scanned pages | optional: the solutions copy its layout and paper |
| Textbook | the course textbook PDF | optional: same-type questions only |

## 2. Start it
In Claude Code (terminal, desktop app or web), say:

> make a classroom for "C:\Users\me\Desktop\Thermo 2"

or type `/course-classroom`. Claude can also start from a GitHub link or a folder you drag in.

## 3. Answer the first questions
Before reading anything big, Claude asks what it can't tell from the folder:
- **Main resource.** Which file or folder is the professor's main material, and which are the tutorials, the exams and
  any solved homework.
- **Paper style:**
  - **Graph paper.** Real millimetre sheets, A4 or A3, portrait or landscape, chosen per subject, the way the homework
    is drawn. Best for courses with graphical methods (McCabe–Thiele, ternary diagrams, psychrometric charts…).
  - **Whiteboard.** A board that fills the screen and zooms to what is drawn, with graphs as clean plots. Best for
    courses where graphs are responses, diagrams and sketches (control, reactors, circuits…).
- **Subjects.** The list and order, named the way the professor names them. Confirm, merge or split them.
- **Scope.** Only the professor's material plus questions of the same type? Textbook questions too? Which exam years?
  Arabic explanations on or off?
- **Names.** The course name, the professor, the assistant's name (for example "Thermo AI"), and whether to add the
  **More** subject, where anyone can upload their own question sheets.

Later, if one question needs something different (a chart printed on the sheet, a different paper, missing data),
Claude asks you about that question, with a suggested default.

## 4. Let it work
Claude converts and reads every file, transcribes and sorts every question, writes the subjects with helper agents,
builds the page, tests every page and move, and publishes it. A full course often takes one to a few hours. You'll get
a link plus a list of:
- what is in each subject
- every model answer it found to be wrong, and what it corrected
- every assumption it had to make

## 5. Use the classroom
- **Subjects** (tabs along the top). Each one runs:
  1. ideas (interactive)
  2. the professor's tutorials and homework
  3. exam and textbook questions of the same type
  4. quizzes
  5. derivations (they get their own tab)
- **The board.** Worked questions open on a clean sheet. **Next move** writes the next step of the working, then draws
  it. Curves appear as three dots first, staircases one stage at a time. The card on the right explains why each step
  is done. **Working / Graph** switch between the two sheets.
- **Zoom and scroll.** Use **− + Fit**, Ctrl + mouse wheel, or pinch to zoom. Scroll with the wheel, two fingers, the
  **Pan** tool, or **▲ ▼**.
- **Write yourself.** Use the pen (black, blue, red), eraser and undo. **Check my work** has the assistant look at your
  writing.
- **The assistant** ("Show me on the board", or type a question):
  - It highlights the lines it is talking about and writes on sticky notes. You can drag the notes; **Hide notes**
    hides them all.
  - If a line of a solution is wrong, it corrects the page itself. The card lists every correction, each with **Undo**.
- **More** (last tab). Upload PDF, Word or photos of questions on any topic, and each question becomes a solved page
  the same way.
- **English / عربي.** Switches all explanations; the questions stay in English, as in the exam.

## 6. Change it later
Ask Claude in the same project, for example:
- "make the font bigger on the board"
- "add the new tutorials in C:\…\New"
- "put Tutorial 5's own graph instead of graph paper"

Claude edits the subject files or the engine, rebuilds, tests, and republishes to the same link. Corrections the
assistant made inside the classroom can be folded back into the files: "fold the saved corrections into the files".

## Sharing
The page starts private. Use the page's **Share** menu to share it. People you give edit access can save corrections
and uploads for everyone; anyone else's are saved on their own device.

## Needs
- Python 3.9+ with pymupdf, pillow, numpy, scipy and sympy (the installer adds them).
- To read the equations and figures in Word or PowerPoint files, Microsoft Office on Windows or LibreOffice. Without
  them those files are read as text only.
