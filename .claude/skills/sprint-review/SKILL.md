---
name: sprint-review
description: Close a sprint by reviewing what actually happened. Finds the Claude Code and Codex sessions and commits from the sprint window, asks which projects belonged to this sprint, and writes sprints/sprint-N-review.md summarizing when the work happened, where it got stuck, and which builder axis it advanced. Use at the end of every sprint, or when the user says "review my sprint", "close out my sprint", or "/sprint-review".
---

# Sprint Review

Read what actually happened over the last two weeks and write it up. The report is for the
builder first: it is usually more accurate about where the time went than memory is.

Run `scripts/sprint_scan.py` in this skill's directory to do the reading. It never sends
anything anywhere.

## Steps

### 1. Establish the sprint and its window

Find the highest `sprints/sprint-N-plan.md`. That is this sprint. Read it: the goal, why, done
looks like, predicted difficulty.

The window starts at the plan file's first commit and ends now:

```bash
git log --diff-filter=A --format=%aI -- sprints/sprint-N-plan.md | tail -1
```

If the plan file was never committed, say so plainly. That costs them points and they should
know now rather than at grading. Use the last 14 days as the window and continue.

### 2. Find candidate sessions

```bash
python3 <skill-dir>/scripts/sprint_scan.py --since <ISO date> --list
```

This lists every project directory with Claude Code or Codex session activity in the window:
the working directory, the session count by tool, and first and last activity. Building in
Codex is fine; its sessions are read the same way. It reads filenames
and timestamps only, not session content.

### 3. Ask which projects belonged to this sprint, and what else was used

Show the list. Pre-select any whose path is at or under this repo, and any whose name relates
to the goal in the plan. Present the rest unselected.

Ask once: which of these were this sprint's work? In the same message, ask what else they used
this sprint that this scan cannot see (Claude or ChatGPT in a browser or the desktop chat,
Cursor, another computer, meetings, research outside any tool).

**Read nothing until they answer.** If they exclude a directory, do not ask why and do not
name it in the report. Record only the count of excluded sessions.

### 4. Read the confirmed sessions

```bash
python3 <skill-dir>/scripts/sprint_scan.py --since <ISO date> --projects <path> [<path> ...] --analyze
```

You get back per-day activity, session count and duration, the user's own prompts, and tool
usage counts. Also read the git log for the window, in this repo and in every other repo the
work happened in: the ones listed under **Where the work lives** in the README, and any local
repo among the confirmed projects. For each, summarize its commits in the window: count, days,
and messages. Never copy code or file contents from another repo into the report; a company
repo may be private, and dates, messages, and file names are enough.

### 5. Work out what happened

- **When they worked.** Which days, and whether it was spread or bunched.
- **Where they got stuck.** Look for runs of prompts circling one problem: repeated retries,
  rephrasing, error text pasted back. Name the two or three biggest, and say how each ended.
- **What took the most time.** By session duration and prompt volume, not by commit count.
- **Which axis this advanced.** Pick exactly one, from the work itself rather than from what
  they intended:
  - **Agentic Workflow**: directing the agent, CLAUDE.md, slash commands, subagents, specs
  - **Discovery**: users, interviews, problem framing, validation, positioning research
  - **Design**: interface, layout, flow, usability, responsive work
  - **Application Architecture**: data, auth, APIs, deployment, tests, refactoring
  - **AI Systems**: model calls in the product, prompts in the product, evals
  - **Launch and Learn**: landing pages, acquisition, pricing, analytics, metrics
  If it is genuinely split, name the one with the most time and say so.

### 6. Write the report

Write `sprints/sprint-N-review.md`:

```markdown
# Sprint N Review

**Window:** <start> to <end>
**Sessions reviewed:** N across M projects (Claude Code A, Codex B; X sessions excluded at your request)
**Not visible to this review:** <what they said they used outside these sessions, or "nothing reported">

## Where the work lives

<each repo with its commit count in the window and whether it is shared with sdmurff; each live
URL. For a repo that is not shared, a short list of its commits in the window: date and message>

## When you worked

<days active out of 14, and the shape: spread, bunched, front-loaded, one long push>

## Where you got stuck

<the two or three real ones, and how each ended>

## What took the most time

<by session time and prompt volume>

## Axis

**<axis>.** <one sentence on why, from the work>

## Against your plan

**Goal was:** <from the plan file>
<Does the work match the goal? Say it plainly either way.>

---

## Your retro

*Written by you, after reading the report above. Answer each prompt.*

**Did you hit the goal?** Yes, partly, or no, and one sentence on why.

**What did the report show you?** One or two things from the report above that you didn't expect
or would not have noticed yourself.

**If the plan changed, why?** Skip if it didn't.

**Actual difficulty:** 1 to 5, and one sentence on why it differed from the difficulty you
predicted.

**What will you change next sprint?** One specific thing.
```

Leave every retro prompt as written, unanswered. The retro is the builder's, not yours.

Facts, not encouragement. No praise, no coaching, no suggestions for next time. The builder
draws the conclusions in their retro.

### 7. Hand off to the retro

Tell them to read the report, then answer the five prompts under **Your retro** at the bottom of
the same file, in their own words. Do not draft answers for them. The retro is graded on whether
it answers each prompt and responds to something specific in the report.

Then commit and push:

```bash
git add sprints/ && git commit -m "Sprint N review and retro" && git push
```

Finally, remind them to submit the Sprint N Wrap-up on Canvas: the GitHub link to this file and
their Loom demo link.

## Rules

- Never read a project the user did not confirm.
- Never copy transcript text into the report. Summarize.
- Never name an excluded project. Report the count only.
- If no sessions are found, say so and write the report from git alone.
