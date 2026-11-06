# Question inventory (read all of it)

Before pages are written, every tutorial, homework and exam question of the course is transcribed and sorted by
subject. You do the inventory for a share of the files (named in your brief). Run Python as `python -I -X utf8`.

## Files
- Every source was copied by prepare.py to WORK\<code>.<ext>; WORK\manifest.json maps code → original path. Every page is
  rendered as WORK\img\<code>\pNN.png (photos as p01.jpg) and its text layer is in WORK\txt\<code>.txt. Office files
  were converted to PDF, so equations that were pictures are visible in the PNGs: ALWAYS look at the PNG (Read tool) —
  text layers garble equations, and scans have no text at all. Enlarge a photo (crop with PIL) when digits are small.
- The brief lists the subject ids and what each covers, and says which files are the professor's (tutorials/homework)
  and which are exams.

## For every question (each numbered question; keep its parts together unless they belong to different subjects)
One JSON object:
{"qid": "<code>-Q3", "src": "Final exam, 1442 2nd semester (date on the paper)", "code": "<code>",
 "crop": [[page_number, top_fraction, bottom_fraction]],   // where it is printed: page as in pNN, fractions 0–1 of
                                                           // the page height with a little margin; several if it runs on
 "subject": "<subject id>", "also": ["<other subject ids it uses>"],
 "kind": "tutorial | homework | exam | example | textbook",
 "marks": "…" or null,
 "text": "the full question in English: every number, unit and condition exactly; maths in LaTeX between $…$",
 "figure": "what any figure shows (with its numbers), or null",
 "graph_given": true/false,                                 // the question prints a chart/graph to work on
 "answer_given": "summary of any model answer / student work in the file, or null",
 "dup_of": "qid of an identical or near-identical question already listed, or null",
 "notes": "anything unclear (unreadable digits: give your best reading and say so); errors you see in a model answer"}
Add {"code": …, "skip": "why"} for a file with no questions (cover pages, formula sheets, answer-only photos — say
which question they answer).

If any file is a STUDENT'S SOLVED HOMEWORK or a graded answer booklet, describe its answering style in detail in your
reply (order of steps, how equations and substitutions are written, how answers are marked, units, how each question
ends, how graphs are drawn and on what paper — A4/A3, portrait/landscape, measured from the ruler on the sheet).
That description becomes COURSE\STYLE.md.

## Output
WORK\inv\<your name>.json = a JSON list of the objects above (valid UTF-8 JSON). Reply briefly: questions per subject,
duplicates found, unreadable files, model-answer errors noticed, and the student answering style if you saw one.
