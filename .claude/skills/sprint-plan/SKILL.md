---
name: sprint-plan
description: Start a sprint by defining its goal, or change the current sprint's plan. Interviews the builder about what they will accomplish in the next two weeks, pushes back on vague or unambitious goals, and writes sprints/sprint-N-plan.md; mid-sprint, asks what changed and why, updates the plan with a dated Changes note, and commits it. Use at the start of every sprint, or when the user says "start my sprint", "plan my sprint", "change my plan", "update my sprint plan", or "/sprint-plan".
---

# Sprint Plan

Write the plan file that opens a two-week sprint. It runs at the start of the sprint; the plan
is due on Canvas by that Wednesday at 11:59 PM and is graded for completion. The builder may
change it later in the sprint, noting what changed and why.

## Steps

### 1. New plan, or a change to the current one?

Find the highest `sprints/sprint-N-plan.md`. If `sprints/` does not exist, this is Sprint 1;
create it and go to step 2.

- **`sprints/sprint-N-review.md` exists** (that sprint is closed): this is a new plan for Sprint
  N+1. Go to step 2.
- **Sprint N has a plan but no review yet** (the sprint is in progress): ask once, "You have a
  Sprint N plan from <date of its first commit>. Do you want to change it, or start Sprint N+1?"
  If they are changing it, go to **Changing a plan** below. If they are starting the next sprint,
  go to step 2 with N+1.

### 2. Read the context

- `README.md` in the repo root for the context declaration: their role, what they are working
  on, who it is for, and who uses their work.
- The previous sprint's retro: at the bottom of `sprints/sprint-<N-1>-review.md` (in Sprint 1 it
  is at the end of that sprint's plan file). Pay attention to **What will you change next
  sprint?**, which is what they said they would do differently.
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
answers, revised or not. You are not negotiating, and the plan is theirs. Its quality is not
graded, but a plan with these problems makes the sprint harder to finish and to review. If nothing fails, say so in one line and go straight to writing the file.

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

The retro does not go here. `/sprint-review` puts it at the bottom of the review file.

### 6. Tell them to commit and submit

Print the exact command:

```bash
git add sprints/sprint-N-plan.md && git commit -m "Sprint N plan" && git push
```

Then tell them to paste the file's GitHub link into the Sprint N Plan assignment on Canvas by
Wednesday, 11:59 PM (open `sprints/sprint-N-plan.md` on github.com and copy the URL), and that if
the plan changes later they edit this file and add a `**Changes:**` line saying what changed and
why. They do not resubmit: the link always shows the current file.

## Changing a plan

Plans change once the builder learns something, and that costs nothing. Your job is to record the
change in their words and keep the plan coherent.

1. Show the current plan. Ask: "What's changing, and why?"
2. Work out which fields the change touches: Goal, Why this, Done looks like, or Predicted
   difficulty. Ask about any that are now unclear, one question at a time.
3. Apply the same checks as a new plan (step 4) to the changed fields only: specific, checkable,
   matches the goal, sized for the time left in the sprint. Raise problems once, then accept
   their answer.
4. Rewrite only the changed fields, in their words. Add a line to `**Changes:**` (create it below
   Predicted difficulty if it is missing), starting with today's date, for example: "Oct 6:
   dropped the slide template and added a competitor benchmark, because the licensing research
   had to come first." Earlier change lines stay; never edit or remove them.
5. Show the full updated plan and ask, "Save it?"
6. On yes, commit and push:

   ```bash
   git add sprints/ && git commit -m "Sprint N plan: <short description of the change>" && git push
   ```

7. Tell them: "Saved. Nothing to resubmit on Canvas; your plan link shows the current file."

Never change a field they did not ask to change. Never write the reason for them: if they cannot
say why, ask once, then record what they said.

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
