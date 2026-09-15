---
name: sprint-plan
description: Start a sprint by defining its goal. Interviews the builder about what they will accomplish in the next two weeks, pushes back on vague or unambitious goals, and writes sprints/sprint-N-plan.md ready to commit. Use at the start of every sprint, or when the user says "start my sprint", "plan my sprint", or "/sprint-plan".
---

# Sprint Plan

Write the plan file that opens a two-week sprint. The commit timestamp is the record, so this
runs on day one and the file gets committed the same day.

## Steps

### 1. Work out which sprint this is

Look in `sprints/`. The next number is one higher than the highest `sprint-N-plan.md` present.
If the directory does not exist, this is Sprint 1; create it.

### 2. Read the context

- `README.md` in the repo root for the context declaration: their role, what they are working
  on, who it is for, and who uses their work.
- The previous sprint's plan file, if there is one. Pay attention to its **Retro** and to
  **What changes next sprint**, which is what they said they would do differently.
- The previous sprint's review report in `sprints/sprint-<N-1>-review.md`, if present. Note
  which axis it tagged.

Students play different roles. Some build their own product end to end. Some are a PM,
engineer, or designer on a team. Some work on go-to-market, pricing, or something else. Not
everyone ships software. Judge the plan against their role, not against a software build.

Most roles combine several hats. Judge the plan against the hats the README lists, and if a
goal falls outside all of them, ask whether their role has changed; if it has, they should
update the README.

If the README says their work is not decided yet, a goal of choosing it is a legitimate
sprint. If the README context is blank, ask what hats they wear on their team before the goal.

If earlier reviews exist, count the axis tags across all of them and tell the user which of
the six axes they have not touched yet. They need five of six by the end.

### 3. Interview

Ask about the goal first, in the user's own terms. Then work through the rest. Ask one thing
at a time; do not present a form. During the interview, ask again only when an answer is too
vague to write down. Save judgments about size and fit for the review in step 4.

- **Goal.** What will be true in two weeks that is not true now?
- **Why this.** Why is this the right next thing for what they are working on?
- **Done looks like.** How will they know the goal was met? Specific enough that someone else
  could check, including what shipped means for this work (see the table below).
- **Predicted difficulty.** 1 to 5 on the scale below.

### 4. Review the whole plan before you write

Once all four answers are in, read them together and ask: is this a reasonable two-week
sprint for someone in their role? Check every item below, not just the first one that fails.

- **Vague goal.** "Improve the app" or "work on marketing" is not a goal. Ask what
  specifically will be different.
- **Unmeasurable.** If "done looks like" cannot be checked by another person, ask what they
  would check.
- **Shipped is undefined.** If "done looks like" does not say how someone other than them will
  reach, use, or see the result, ask. Use the table below for their kind of work. If their
  work is not in the table, ask them to say what shipped means for it.
- **Done does not match the goal.** If meeting "done looks like" would not mean the goal was
  met, point out the gap.
- **Too small.** If it reads like a day or less of work with Claude Code, say so and ask what
  else belongs in the two weeks. A tutorial-sized build, or a deliverable one prompt could
  produce, is too small even if it is new to them.
- **Too large.** If it reads like a semester, say so and ask what the two-week slice is.
- **Ignores the last retro.** If the previous retro said something would change and this plan
  ignores it, point that out.

Raise every problem you found in one message, briefly, each one once. Then accept their
answers, revised or not. You are not negotiating, and the plan is theirs; its quality is
graded. If nothing fails, say so in one line and go straight to writing the file.

Do not push back on difficulty. It is self-reported and not graded.

### 5. Write the file

Write `sprints/sprint-N-plan.md` exactly in this shape, filled in with their answers:

```markdown
# Sprint N Plan

**Goal:** ...

**Why this:** ...

**Done looks like:** ...

**Predicted difficulty:** N
```

Leave the end-of-sprint fields out. `/sprint-review` adds them later.

### 6. Tell them to commit

Print the exact command and say the timestamp is what gets graded:

```bash
git add sprints/sprint-N-plan.md && git commit -m "Sprint N plan" && git push
```

## What shipped means

Not every sprint produces code. What counts is that the thing is real and someone other than
the builder can reach it, use it, or see it.

| If the sprint is | Shipped means |
|---|---|
| A product feature | Deployed and working in the live app |
| Frontend or design work | The new interface is live, not a mockup |
| A landing page or campaign | The page is published at a URL |
| Pricing or financial modeling | The model exists, runs on real numbers, and the team can use it |
| Marketing or sales copy | The copy is published or in use, not sitting in a doc |
| An automation or workflow | It runs, and they can show it running |
| Research or discovery | The findings are written up in the repo and someone acted on them |
| Analytics or measurement | The tracking is live and returning real data |

## The difficulty scale

| | |
|---|---|
| 1 | I already know how to do this |
| 2 | I know most of it, with a few small gaps to fill |
| 3 | I will have to learn something new, but the path is clear |
| 4 | I will have to learn a lot, and the path is not clear |
| 5 | I do not know whether this is possible |

## Rules

- Write the file only after the interview. Do not draft a plan and ask them to approve it.
- Their words, not yours. Tighten wording; do not replace their thinking with your own.
- Never fill in a field they did not answer.
