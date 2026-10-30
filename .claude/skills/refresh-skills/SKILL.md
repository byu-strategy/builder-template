---
name: refresh-skills
description: Update this repo's course skills (/sprint-plan, /sprint-review, /sprint-coach, /learn, /eli5) to the latest version from the class template. Every course skill runs this on its own as its first step; run it yourself when the user says "update my course skills", "refresh my skills", or "/refresh-skills".
---

# Refresh the course skills

Run from anywhere inside the repo:

```bash
python3 .claude/skills/refresh-skills/refresh.py
```

It prints one line:

- `UP TO DATE`: nothing to do.
- `UPDATED: <names>`: those course skills were replaced with the template's copy and committed
  ("Update course skills"). Skills the builder wrote under other names are never touched, and
  nothing outside `.claude/skills` changes. The commit goes up with the builder's next push.
- `SKIPPED: <why>`: GitHub could not be reached, or this is the template itself. Carry on with the
  skills as they are; never stop for this.

If `python3` is not found, try `python`. If neither works, say so in one line and carry on.

When the user ran this directly, tell them which skills changed, if any. No restart is needed: a
skill reads its instructions from disk each time it runs.

## When another course skill runs this first

Every course skill starts with this step. Run it silently, before saying anything else:

- `UP TO DATE` or `SKIPPED`: say nothing about it and go on.
- `UPDATED` and the list includes the skill you are running: read that skill's `SKILL.md` again
  from disk now and follow the new version from its first step after the refresh step. Do not run
  the refresh a second time. Tell the builder in one line: "Your course skills were updated to the
  latest version."
- `UPDATED` with other skills only: tell the builder in one line and go on.
