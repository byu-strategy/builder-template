---
name: sprint-review
description: Close a sprint by reviewing what actually happened. Finds the Claude Code and Codex sessions and commits from the sprint window, asks which projects belonged to this sprint, and writes sprints/sprint-N-review.md summarizing when the work happened, where it got stuck, and which builder axis it advanced, then asks the builder five retro questions and saves their answers word for word at the bottom. Use at the end of every sprint, or when the user says "review my sprint", "close out my sprint", or "/sprint-review".
---

# Sprint Review

Read what actually happened over the last two weeks and write it up. The report is for the
builder first: it is usually more accurate about where the time went than memory is.

Run `scripts/sprint_scan.py` in this skill's directory to do the reading. It never sends
anything anywhere. Its `SCAN_VERSION` line is how the course checks that your copy of this skill is
current; `python3 <skill-dir>/scripts/sprint_scan.py --version` prints it.

## First: refresh the course skills

Before anything else, and before saying anything, run this from the repo root:

```bash
python3 .claude/skills/refresh-skills/refresh.py
```

It brings every course skill up to date with the class template and prints one line. `UP TO DATE` or
`SKIPPED`: say nothing and go on. `UPDATED` with `sprint-review` in the list: read
`.claude/skills/sprint-review/SKILL.md` again now and follow the new version from the step after this one
(do not refresh twice), and tell the builder in one line that their course skills were updated.
`UPDATED` with other skills only: tell them in one line and go on. If the script is missing or
`python3` fails, go on.

## Which course

If `course.json` at the repo root says `"course": "ai-foundry"`, follow `foundry.md` in this
skill's directory wherever it differs from the steps below. Otherwise follow the steps below
exactly as written.

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

You get back per-day activity, session count and duration, the user's own prompts, tool
usage counts, and **Builder tools used**: the skills, slash commands, hooks, subagents, MCP
servers (connectors), service CLI tools such as `gh` or `supabase`, direct API calls such as
`curl`, plugins, messages sent to other sessions, plan mode, permission modes, permission prompts
and denials, where the sessions ran (interactive, or non-interactive with `claude -p`), worktrees,
and memory and instruction files the sessions used. These are counts and names only. It also lists **Users this sprint**: signs that people
outside the team used the work (a user's report in your own prompts, a ticket someone else filed,
usage counted over people, logs filtered to users, messages to users) and any change you made after
one, plus commits whose message ties a change to a user or a ticket. Also read the git log for the window, in this repo and in every other repo the
work happened in: the ones listed under **Where the work lives** in the README, and any local
repo among the confirmed projects. For each, summarize its commits in the window: count, days,
and messages. Never copy code or file contents from another repo into the report; a company
repo may be private, and dates, messages, and file names are enough.

Then list the `/learn` sessions logged in this repo during the window:

```bash
python3 <skill-dir>/scripts/sprint_scan.py --since <ISO date> --learning .
```

It reads only `learning/YYYY-MM-DD-*.md` in this repo: the section, time, whether it finished,
the axis it was logged against, the concept id if the session focused on one, what the builder asked about, starting point and confidence (Developing, Proficient, or Strong; the scan maps an older log's 1 to 5 to these), and the
question they still had, plus a count by axis.

### 5. Work out what happened

- **When they worked.** Which days, and whether it was spread or bunched.
- **Where they got stuck.** Look for runs of prompts circling one problem: repeated retries,
  rephrasing, error text pasted back. Name the two or three biggest, and say how each ended.
- **What took the most time.** By session duration and prompt volume, not by commit count.
- **Which axis this advanced.** Pick exactly one, from the work itself rather than from what
  they intended:
  - **Agentic Workflow**: directing the agent, CLAUDE.md, slash commands, skills, hooks,
    subagents; building AI into the product: prompts, tool use, agent loops, evals
  - **Discovery**: users, interviews, problem framing, validation, positioning research
  - **Design**: interface, layout, flow, usability, responsive work, and specs (user stories,
    acceptance criteria, PRDs, decision sections)
  - **Application Architecture**: data, auth, APIs, deployment, tests, refactoring, wiring a
    model in (API calls, retrieval pipelines, cost and latency)
  - **AI Systems**: learning how the models work: neural networks, next-word prediction,
    training and fine-tuning, embeddings and RAG, context windows, why models hallucinate
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

## Builder tools you used

<a table from the scan's BUILDER TOOLS USED section, one row each: Skills you wrote, Course
skills, Plugins, Slash commands, Hooks, Subagents (two lines: named ones, from `.claude/agents`, a
plugin, or the builder, and Claude Code's built-in ones such as Explore, which Claude can start on
its own), Messages to other sessions, Plan mode (plan tool calls and turns spent in plan mode, so
plan mode turned on with Shift+Tab counts), Permission mode (the scan's raw names: `default`,
`acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`), **Permission prompts and denials**
(prompts the builder approved or declined, and calls a permission rule, auto mode, or a built-in
safety check denied), **Where sessions ran** (interactive, or non-interactive with `claude -p` or
the Agent SDK, the desktop app, the VS Code extension), Worktrees, Memory and instructions, and
**Reaching outside the repo** (one row with its three routes: service CLI tools, MCP servers and
connectors, direct API calls). Columns: what it is (one plain line), what you used this sprint
(names and counts, or "not used"). A skill the builder wrote (anything not sprint-plan,
sprint-review, sprint-coach, learn or eli5) goes under Skills you wrote; the course's skills go
under Course skills. For Memory and instructions, say which files loaded
(CLAUDE.md, MEMORY.md) and whether any were edited. Then one sentence listing the building
blocks not used this sprint, as a plain fact, for example "Not used this sprint: hooks,
subagents, plan mode." Never judge how many is enough, and never copy prompt or file content.
Codex sessions record tool names only, so say "Codex sessions do not show these" when there
were any. Below the table, add one line: "Scan version: <the SCAN VERSION line>.">

## Users this sprint

<from the scan's USERS THIS SPRINT section: people outside your team who used the work, and what
you changed because of them. A short table, one row per real instance: date, what happened (a
user's report, a ticket from someone else, usage counted over people, logs filtered to users, a
message to users), and the change that followed (the file or the commit), or "no change yet".
Refer to people by role ("a tester", "a customer"), never by name or email: this file is
committed. Check each hit against the plan's team and drop teammates, test accounts and your own
account. Production lookups by id are not users. If nothing real is left, write "No outside users
this sprint." as a plain fact, without judging it>

## Learning sessions

<count of /learn sessions logged in the window, and the count by axis. For each: date, section,
concept id (if the log names one), axis, minutes, what they asked about, starting point and confidence (Developing, Proficient, or Strong), and the question they still
had. Then one plain sentence putting learning beside building: which axes they studied and which
axis the sprint's work advanced (from the Axis section below), for example "You studied three
Architecture sections and the sprint advanced Architecture" or "You studied Design; the sprint's
work was Discovery." State it; do not judge it. "None logged this sprint" if there were none. Facts
only: not a grade, no judgment of how many is enough, no check scores>

## Axis

**<axis>.** <one sentence on why, from the work>

## Against your plan

**Goal was:** <from the plan file>
<Does the work match the goal? Say it plainly either way.>

---

## Your retro

*The builder's own answers, recorded word for word in step 7.*

**Did you hit the goal?** <their answer>

**Hours, your estimate:** <their answer>

**If the plan changed, why?** <their answer>

**Actual difficulty:** <their answer>

**What will you change next sprint?** <their answer>
```

Write the report sections now, but leave the **Your retro** section out of the file until step 7.

Facts, not encouragement. No praise, no coaching, no suggestions for next time. The builder
draws the conclusions in their retro.

### 7. Ask the retro questions

The retro is the builder's response to the report, and it is part of this skill, not a separate
step. Show them the report, then say: "Five quick questions for your retro. Answer in your own
words; I'll save them exactly as you write them." Ask one question at a time and wait for each
answer:

1. **Did you hit the goal?** Yes, partly, or no, and why.
2. **How many hours do you estimate you worked on this sprint, all in, including time away from Claude Code?** A number or a range is fine.
3. **If the plan changed, why?** (Skip it if the plan did not change.)
4. **Actual difficulty, 1 to 5,** and why it differed from the difficulty you predicted.
5. **What will you change next sprint?** One specific thing.

Rules for the answers:

- Record each answer **word for word**. Do not rephrase, fix grammar, expand, or summarize. The
  retro is theirs; it is graded on what they say.
- Never suggest an answer, list options, or hint at what the report "really" shows. If they ask
  what to say, point them back to the report.
- If an answer is very short or vague, you may ask once for a specific. Accept whatever they say
  next. For the hours question, never suggest a number and never mention the active session time:
  the estimate is theirs.
- If they decline a question, record "(no answer)".

Then add one line under **Sessions reviewed** at the top of the report, copied from the scan's
ACTIVE SESSION TIME line: `**Active session time:** about N hours (gaps under 15 minutes)`. Add it
only now, after the retro: it must not be on screen or in the file while they estimate their hours.

Then append the **Your retro** section to `sprints/sprint-N-review.md` with their answers, show
them the finished section, and commit and push:

```bash
git add sprints/ && git commit -m "Sprint N review and retro" && git push
```

Finally, remind them to submit the Sprint N Wrap-up on Canvas: the GitHub link to this file and
their Loom demo link. Remind them to make sure Professor Murff can see the video: in Loom's Share
settings, set it to "Anyone with the link" or share it with scott.murff@byu.edu. A video he cannot
open is not graded until it is shared.

If they want to change an answer later, they edit the file and commit again; that is fine.

## Decisions

A decision counts as the builder's when the builder proposed it, or chose between options the
agent offered and wrote down why. When the report describes a choice made during the sprint
(in **Where you got stuck**, **What took the most time**, or **Against your plan**), say who made
it on that basis: an option the agent picked and the builder accepted without a reason is the
agent's choice, and the report says so plainly. You may describe options; you never pick for the
builder, and you never write a decision record in their name without their own reason.

## Rules

- Write the report in plain, literal sentences. No mannered prose: no metaphor or flourish where a
  literal phrase exists ("most commits came on Oct 10 and Oct 11", not "the sprint was
  front-loaded with a lull"). No em dashes.

- Never read a project the user did not confirm.
- Never copy transcript text into the report. Summarize.
- Never name an excluded project. Report the count only.
- If no sessions are found, say so and write the report from git alone.
- Learning sessions are reported, never graded or scored. Do not copy check results into the
  report.
