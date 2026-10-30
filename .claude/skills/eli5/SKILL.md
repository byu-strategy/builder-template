---
name: eli5
description: Explain one idea like the builder is five, as a one-page picture explainer with big shapes and very few words, published as an Artifact link when possible (saved under learning/eli5/ either way). Use when the user types /eli5 <topic>, says "explain it like I'm five", "explain that simpler", "draw me a picture of how X works", or when the /learn skill offers a simpler picture of a building block.
argument-hint: "[the idea to explain, e.g. how a pull request works]"
---

# Explain it like I'm five

Make one web page that explains **one idea** to someone who knows nothing about it, with big
pictures and very few words. The picture carries the idea; the words only name things.

Idea: $ARGUMENTS

If no idea was given, ask for one in a single question and wait.

## First: refresh the course skills

Before anything else, and before saying anything, run this from the repo root:

```bash
python3 .claude/skills/refresh-skills/refresh.py
```

It brings every course skill up to date with the class template and prints one line. `UP TO DATE` or
`SKIPPED`: say nothing and go on. `UPDATED` with `eli5` in the list: read
`.claude/skills/eli5/SKILL.md` again now and follow the new version from the step after this one
(do not refresh twice), and tell the builder in one line that their course skills were updated.
`UPDATED` with other skills only: tell them in one line and go on. If the script is missing or
`python3` fails, go on.

## Steps

1. **Find the one idea.** Write it as one plain sentence ("A pull request is a proposed change
   that waits for checks and a review before it joins main"). If the request holds two ideas,
   pick the one the builder needs now and say so.
2. **Pick the example.** When `/learn` calls this, use the example already in that
   conversation. Otherwise use one everyday example, or the builder's own product if they asked
   about it.
3. **Plan three to six panels,** each one small step. Each panel is a picture made of simple
   shapes, with a label of one to four words. Read left to right or top to bottom. Show the
   mechanism, the actual parts and what moves between them, never a box labeled with the
   idea's name.
4. **Build one self-contained HTML file** and save it as
   `learning/eli5/<short-idea-name>.html` (create the folder if needed):
   - Inline SVG for every picture; no external images, scripts, or fonts; no emoji.
   - A system font stack, large type (body 20px or more), plenty of white space, one accent
     color, works on a phone.
   - At most about 60 words on the whole page, not counting labels. No title larger than the
     pictures.
   - A short `alt`-style description in each SVG's `<title>` for screen readers.
   - At the bottom, two lines in small type: **Where this picture is simplified:** one
     sentence naming what the picture leaves out. **Say it back:** one question the builder
     answers in their own words.
5. **Show it.** If you have the Artifact tool (Claude Code's built-in way to publish a page),
   publish the file with it and give the builder the link. It is private to their account and
   opens the same way from the terminal, VS Code, the desktop app, or the web. If you do not
   have that tool, or publishing fails: on macOS run `open <file>`, on Windows (Git Bash) run
   `start <file>`, and always print the file's full path so they can open it themselves.
6. **Check understanding.** Ask the "Say it back" question in the chat and wait. If the answer
   shows a wrong model, name it plainly and point at the panel that shows the right one.

## Rules

- **Simple, never wrong.** Leave details out; do not change how the thing works. If the
  everyday example is an analogy, it must be accurate, and the page says where it breaks.
- One idea per page. Make a second page for a second idea.
- Literal labels ("saves the row", "waits for review"), never cute ones.
- Do not commit the page unless the builder asks; it is a study aid. The `/learn` log records
  that it was used.

## Credit

Adapted from the `eli5` skill by Thariq Shihipar (Claude community plugins, MIT License).
See `LICENSE` in this folder.
