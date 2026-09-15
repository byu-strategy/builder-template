# [Your product, or your part of it]

> One sentence: what this is and who it is for.

**Where to see it:** [URL, or where the work lives: a live app, a published page, a model in this repo]
**Built by:** [your name], MSB 341 Product Management, BYU

## Context

Fill this in during Sprint 1 and keep it current. Every sprint is read against it.

- **My role:** [the hats you wear, and what you own. Most roles combine several: product,
  engineering, design, go-to-market, pricing, analytics, operations. A solo builder wears most
  of them]
- **What I am working on:** [your product, or your part of a team's product. "Not decided" is
  fine early on; list the options you are weighing]
- **Who it is for:** [the customer or segment the work ultimately serves]
- **Who uses my work:** [the specific person who will use what you make, and how you reach
  them. On a team this can be your teammates: engineers using your specs, sales using your
  pricing]

If your situation changes, revise this and note what changed. That is normal; a silent
mismatch between this file and your work is not.

## What is in this repo

| Folder | What lives here |
|---|---|
| `sprints/` | One plan and one review per sprint |
| `discovery/` | Interviews, personas, what you learned about your user |
| `design/` | Flows, screens, usability test notes |
| `product/` | The work itself: code, a pricing model, a copy deck, an automation |
| `specs/` | One spec per piece of work, written before you make it |
| `gtm/` | Launch, channels, copy, experiments |
| `metrics/` | What you measure and what it says |
| `decisions/` | Numbered records of what you decided and why |

Not everyone in this course ships software. An interview, a pricing model, a landing page
draft, and a usability finding are all artifacts, and they get committed like anything else.
Use the folders that fit your role and ignore the rest.

If you build an AI feature, put its eval set in `product/evals/`. A test set is how you know
whether a change to a prompt helped or hurt.

## Running it

[If your work includes code: how to run it locally. Delete this section if it does not.]

## Sprints

Each sprint:

```bash
/sprint-plan     # day one, then commit the plan
# ...do the work...
/sprint-review   # last day, then commit the report and write your retro
```

## Ground rules

- **Spec before work.** For anything non-trivial, the spec's commit should predate the
  work's commits.
- **Decisions get recorded.** When you make a real choice, write it in `decisions/` with the
  alternatives you rejected.
- **No real customer contact details anywhere in this repo.** Anonymize people in interview
  notes: "dental office manager, Provo" rather than a name and an email.
- **Keep `CLAUDE.md` current.** It is what your agent knows about your work. Stale context
  produces bad output.
