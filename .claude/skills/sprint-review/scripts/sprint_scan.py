#!/usr/bin/env python3
"""Scan local Claude Code and Codex session transcripts for a sprint window.

Reads only what it is told to read. --list reads each transcript's recorded working
directory and nothing else; message content is opened solely for the projects named
with --projects. Nothing is sent anywhere.
"""
import argparse, json, os, re, subprocess, sys, datetime as dt
from collections import Counter, defaultdict
from pathlib import Path

# The roster reads this line to tell whether a student's /sprint-review is current. Change the date
# whenever the scan or SKILL.md changes in a way the grader relies on.
SCAN_VERSION = "2026-10-16"

ROOT = Path.home() / ".claude" / "projects"
CODEX = Path.home() / ".codex" / "sessions"   # Codex CLI and the Codex VS Code extension


def codex_cwd(jsonl: Path) -> str:
    """Codex records its working directory in the first line, a session_meta record."""
    try:
        with open(jsonl, "r", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i > 5:
                    break
                d = json.loads(line)
                if d.get("type") == "session_meta":
                    return (d.get("payload") or {}).get("cwd") or "?codex"
    except (OSError, ValueError):
        pass
    return "?codex"


def project_cwd(jsonl: Path, fallback: str) -> str:
    """The real working directory, read from the first record that carries one.

    The directory name under ~/.claude/projects encodes both "/" and "-" as "-",
    so it cannot be decoded unambiguously. Each transcript records its own cwd.
    """
    try:
        with open(jsonl, "r", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i > 40:
                    break
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("cwd"):
                    return d["cwd"]
    except OSError:
        pass
    return fallback


def sessions(since: dt.datetime):
    """Yield (tool, cwd, jsonl_path, mtime) for Claude Code and Codex sessions active since `since`."""
    def recent(f):
        try:
            m = dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc)
        except OSError:
            return None
        return m if m >= since else None

    if ROOT.is_dir():
        for proj in sorted(ROOT.iterdir()):
            if proj.is_dir():
                for f in proj.glob("*.jsonl"):
                    m = recent(f)
                    if m:
                        yield "claude", project_cwd(f, "?" + proj.name), f, m
    if CODEX.is_dir():
        for f in CODEX.rglob("rollout-*.jsonl"):
            m = recent(f)
            if m:
                yield "codex", codex_cwd(f), f, m


def cmd_list(since):
    agg = defaultdict(lambda: {"n": 0, "first": None, "last": None, "tools": Counter()})
    for tool, key, f, m in sessions(since):
        a = agg[key]
        a["n"] += 1
        a["tools"][tool] += 1
        a["first"] = m if a["first"] is None else min(a["first"], m)
        a["last"] = m if a["last"] is None else max(a["last"], m)
    if not agg:
        print("No sessions found in the window.")
        return
    rows = sorted(agg.items(), key=lambda kv: kv[1]["n"], reverse=True)
    print(f"{'sessions':>8}  {'first':<11} {'last':<11} {'tool':<14} project")
    for path, a in rows:
        tools = ", ".join(f"{k} {v}" for k, v in sorted(a["tools"].items()))
        print(f"{a['n']:>8}  {a['first']:%Y-%m-%d}  {a['last']:%Y-%m-%d}  {tools:<14} {path}")
    print(f"\n{len(rows)} projects, {sum(a['n'] for _, a in rows)} sessions.")


def codex_records(path):
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") == "response_item" and isinstance(d.get("payload"), dict):
                yield d.get("timestamp", ""), d["payload"]


def user_turns(path, tool="claude"):
    """Yield (timestamp, text) for the human's own turns only."""
    if tool == "codex":
        for ts, p in codex_records(path):
            if p.get("type") == "message" and p.get("role") == "user":
                text = " ".join(b.get("text", "") for b in p.get("content") or []
                                if isinstance(b, dict) and b.get("type") == "input_text").strip()
                if text and not text.startswith("<"):
                    yield ts, text
        return
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") != "user":
                continue
            msg = d.get("message") or {}
            c = msg.get("content")
            text = ""
            if isinstance(c, str):
                text = c
            elif isinstance(c, list):
                text = " ".join(
                    b.get("text", "") for b in c
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            text = text.strip()
            if text and not text.startswith("<"):
                yield d.get("timestamp", ""), text


def tool_uses(path, tool="claude"):
    if tool == "codex":
        for _ts, p in codex_records(path):
            if p.get("type") in ("function_call", "custom_tool_call"):
                yield p.get("name", "?")
        return
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") != "assistant":
                continue
            for b in (d.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    yield b.get("name", "?")


COURSE_SKILLS = {"sprint-plan", "sprint-review", "sprint-coach", "learn", "eli5"}
# Subagent types that ship with Claude Code. Claude can start these on its own (Explore during a
# search, for example), so they are listed apart from agents the builder or a plugin defined.
BUILTIN_AGENTS = {"general-purpose", "Explore", "Plan", "statusline-setup", "claude-code-guide",
                  "output-style-setup", "fork"}
# Where a session ran, from the entrypoint every record carries. "sdk-cli" is a non-interactive
# run: `claude -p "..."` in a terminal or a script, or a program built on the Agent SDK.
SURFACES = {"cli": "terminal or IDE, interactive", "sdk-cli": "non-interactive (claude -p or the Agent SDK)",
            "sdk-ts": "Agent SDK (TypeScript)", "sdk-py": "Agent SDK (Python)",
            "claude-vscode": "VS Code extension", "claude-desktop": "Claude desktop app"}


def permission_event(d):
    """What happened to one tool call's permission, from a user record that carries its result, or
    None when nothing worth listing happened (a call the current mode or a hook settled is not one;
    hooks have their own rows). Newer logs record the decision in permissionDecision; older ones
    only in the error text, so both are read."""
    tur = d.get("toolUseResult")
    text = tur if isinstance(tur, str) else ""
    if not text:
        c = (d.get("message") or {}).get("content")
        if isinstance(c, list):
            text = " ".join(str(b.get("content", "")) for b in c
                            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"))
    if "User rejected tool use" in text or "doesn't want to proceed with this tool use" in text:
        return "you declined at a prompt"
    if "denied by the Claude Code auto mode classifier" in text:
        return "blocked by auto mode"
    if "denied by a built-in Claude Code safety check" in text:
        return "blocked by a built-in safety check"
    pd = d.get("permissionDecision")
    if isinstance(pd, dict):
        decision, source, reason = pd.get("decision"), pd.get("source"), pd.get("reasonType")
        if decision == "accept" and source == "user_temporary":
            return "you approved at a prompt"
        if decision == "accept" and source == "user_permanent":
            return "you approved and saved a rule"
        if decision == "reject" and source == "config" and reason == "safetyCheck":
            return "blocked by a built-in safety check"
        if decision == "reject" and source == "config":
            return "denied by a permission rule"
        if decision == "accept" and source == "config" and reason == "rule":
            return "allowed by a permission rule"
    if re.search(r"Permission to use \S+ .*has been denied", text, re.S):
        return "denied by a permission rule or mode"
    return None
# Command-line tools for outside services: one of the three routes beyond the repo (with MCP
# servers and direct API calls). Shell basics like ls or git are not counted here.
SERVICE_CLIS = {"gh", "supabase", "vercel", "netlify", "stripe", "firebase", "aws", "gcloud", "az",
                "heroku", "railway", "fly", "flyctl", "wrangler", "render", "expo", "eas", "neonctl",
                "turso", "prisma", "doctl", "linear", "op", "resend", "twilio", "shopify", "sentry-cli"}
API_CLIS = {"curl", "wget", "http", "https", "xh"}


def programs(command):
    """The program at the start of each part of a shell command, skipping VAR=value prefixes and
    sudo; for npx and bunx, the package it runs."""
    for part in re.split(r"&&|\|\||;|\|", command):
        words = [w for w in part.strip().split() if not re.match(r"^\w+=", w) and w != "sudo"]
        if words and words[0] in ("npx", "bunx", "pnpx") and len(words) > 1:
            words = [w for w in words[1:] if not w.startswith("-")] or words
        if words:
            yield Path(words[0]).name


def builder_tools(path, tool="claude"):
    """Which Claude Code building blocks a session used: skills, slash commands, hooks, subagents,
    MCP servers, plan mode, permission modes, worktrees, and the memory and instruction files it
    loaded or wrote. Counts and names only; never prompt or file content. Codex logs carry tool
    names only, so they add nothing here."""
    out = {k: Counter() for k in ("skills", "commands", "hooks", "hooks_blocked", "subagents",
                                  "subagents_named", "mcp", "cli", "api_calls", "plugins", "messages",
                                  "modes", "plan", "worktrees", "permissions", "surfaces",
                                  "instructions_loaded", "memory_written")}
    if tool == "codex":
        return out
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return out
    surface = None
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("type")
            if surface is None and d.get("entrypoint"):
                surface = d["entrypoint"]
                out["surfaces"][SURFACES.get(surface, surface)] += 1
            if t == "user":
                if d.get("permissionMode"):
                    out["modes"][d["permissionMode"]] += 1
                    if d["permissionMode"] == "plan":
                        # Plan mode turned on with Shift+Tab shows only as the permission mode.
                        out["plan"]["turns in plan mode"] += 1
                ev = permission_event(d)
                if ev:
                    out["permissions"][ev] += 1
                c = (d.get("message") or {}).get("content")
                if isinstance(c, str):
                    m = re.search(r"<command-name>/?([^<]+)</command-name>", c)
                    if m:
                        out["commands"][m.group(1).strip()] += 1
                elif isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "tool_result" and "hook error" in str(b.get("content", "")):
                            ev = re.search(r"(\w+(?::\w+)?) hook error", str(b.get("content", "")))
                            out["hooks_blocked"][ev.group(1) if ev else "hook"] += 1
            elif t == "attachment":
                a = d.get("attachment") or {}
                if a.get("type") == "hook_success":
                    out["hooks"][a.get("hookName") or a.get("hookEvent") or "hook"] += 1
                elif a.get("type") == "invoked_skills":
                    for sk in a.get("skills") or []:
                        out["skills"][sk.get("name", "?")] += 1
                elif a.get("type") == "instructions":
                    for f in a.get("files") or []:
                        out["instructions_loaded"][f"{f.get('type', '?')}: {Path(f.get('path', '?')).name}"] += 1
            elif t == "assistant":
                for b in (d.get("message") or {}).get("content") or []:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    name, inp = b.get("name", ""), b.get("input") or {}
                    if name == "Bash":
                        for prog in programs(str(inp.get("command", ""))):
                            if prog in SERVICE_CLIS:
                                out["cli"][prog] += 1
                            elif prog in API_CLIS:
                                out["api_calls"][prog] += 1
                    if name == "Skill":
                        out["skills"][inp.get("skill", "?")] += 1
                    elif name in ("Agent", "Task"):
                        kind = inp.get("subagent_type") or "general-purpose"
                        out["subagents" if kind in BUILTIN_AGENTS else "subagents_named"][kind] += 1
                    elif name.startswith("mcp__"):
                        out["mcp"][name.split("__")[1]] += 1
                    elif name == "SendMessage":
                        to = str(inp.get("to") or "")
                        if re.fullmatch(r"a[0-9a-f]{12,}", to):
                            out["messages"]["a subagent"] += 1
                        elif to.startswith(("uds:", "pipe:")) or not to:
                            out["messages"]["a session on this computer"] += 1
                        else:
                            out["messages"][f"session {to}"] += 1
                    elif name == "ListAgents":
                        out["messages"]["listed reachable sessions"] += 1
                    elif name in ("EnterPlanMode", "ExitPlanMode"):
                        out["plan"][name] += 1
                    elif name in ("EnterWorktree", "ExitWorktree"):
                        out["worktrees"][name] += 1
                    elif name in ("Write", "Edit", "MultiEdit"):
                        fp = str(inp.get("file_path", ""))
                        if "/memory/" in fp or fp.endswith(("CLAUDE.md", "AGENTS.md", "MEMORY.md")):
                            out["memory_written"][Path(fp).name] += 1
    return out


# ---------------------------------------------------------------- users this sprint
# Evidence that people outside the team used the work, and that the builder changed it because of
# them (depth level 4). Calibrated 2026-10-15 on a product with real users: a production read by
# itself proves nothing (it happens before any user exists), so lookups are not reported; what
# counts is a person who did or said something, followed by a change.
DB_CALL = re.compile(r"\b(psql|pgcli|mysql|mongosh|neonctl|turso db shell|pscale shell)\b|/rest/v1/|firestore|"
                     r"firebase-admin|\.from\(['\"]\w+['\"]\)|prisma\.\w+\.(count|groupBy|find)", re.I)
USER_TABLE = re.compile(r"\b(auth\.)?(users?|profiles?|accounts?|members|signups?|waitlist|sessions|events|"
                        r"page_?views|visits|feedback|orders|subscriptions|customers|submissions)\b", re.I)
AGGREGATE = re.compile(r"count\(\s*distinct|group by|date_trunc|interval '\d|last_sign_in|last_seen", re.I)
LOCAL = re.compile(r"127\.0\.0\.1|localhost|:54322|supabase start|\.env\.(localdb|test|demo)|seed|fixture|faker|"
                   r"demo\.local|example\.com|/api/health|\[boot\]", re.I)
LOGS = re.compile(r"\b(vercel|railway|netlify|fly|flyctl|heroku|render) logs\b|wrangler tail|firebase functions:log|"
                  r"gcloud logging read|analytics/endpoints/logs|sentry-cli|sentry\.io/api|posthog\.com/api|"
                  r"plausible\.io/api|mixpanel|amplitude", re.I)
LOG_FILTER = re.compile(r"--filter|grep\b.*(user|@|/api/|/auth)", re.I)
REPORT = re.compile(r"\b(a|one|this|my|our|the) (user|customer|teacher|professor|client|tester|student|player|buyer)s?\b"
                    r".{0,40}\b(said|told|asked|emailed|texted|reported|complained|is seeing|ran into|couldn'?t|"
                    r"didn'?t (like|understand|know))|feedback from|got (some|this) feedback|on a (call|zoom|meeting) with|"
                    r"screen ?shar|user (interview|test)|interviewed|forwarded message|^(From|Subject):", re.I | re.M)
NAMED = re.compile(r"\b([A-Z][a-z]{2,})(?: [A-Z][a-z]+)? (?:just )?(said|asked|wants|reported|submitted|didn'?t like|"
                   r"couldn'?t|emailed|texted|told me)\b")
NOT_NAMES = {"Claude", "Codex", "Cursor", "Vercel", "Supabase", "Stripe", "Google", "Chrome", "Railway", "Firebase",
             "The", "This", "That", "It", "He", "She", "They", "You", "We", "Someone", "Nobody", "Everyone", "Agent"}
TICKET = re.compile(r"/fix-bug|/triage|gh issue (view|list)|\bfrom (bug_reports|feedback|tickets|support_\w+)", re.I)
SELF_FILED = re.compile(r"/file-bug|engineering-filed|not user-reported", re.I)
OUTREACH = re.compile(r"api\.resend\.com/emails|resend\.emails\.send|mailgun\.net/v3/\S+/messages|api\.sendgrid\.com|"
                      r"postmarkapp|chat\.postMessage|inviteUserByEmail|/auth/v1/invite|notify[-_]?(shipped|reporter|users)",
                      re.I)
CHANGE_MSG = re.compile(r"\((bug|issue|ticket) [0-9a-f]{6,}\)|(fixes|closes|resolves) #\d+|reported by|feedback from|"
                        r"(a|the|one) (user|customer|tester|teacher|student|player)s? (reported|said|asked|couldn'?t)", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def _skip_prompt(text):
    return (text.startswith(("This session is being continued", "<", "Base directory for this skill"))
            or "<task-notification>" in text or "<cross-session-message" in text
            or text.startswith("Another Claude session sent a message"))


def _clip(text, n=110):
    """One line of evidence, with email addresses removed (the report is committed to a repo)."""
    return EMAIL.sub("[email]", " ".join(str(text).split()))[:n]


def users_signals(path, self_emails, tool="claude", since="", roots=()):
    """Hits, in time order: (timestamp, kind, strength, evidence). Kinds: user report in your own
    words, a ticket from someone else, usage counted over people, logs filtered to users, a message
    to users, and a change made after a user signal in the same session."""
    hits = []
    if tool == "codex":
        return hits
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return hits
    signal_at = None
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = d.get("timestamp", "")
            if ts and since and ts < since:
                continue
            if d.get("type") == "user":
                c = (d.get("message") or {}).get("content")
                text = c if isinstance(c, str) else " ".join(
                    b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text")
                text = text.strip()
                if not text or _skip_prompt(text):
                    continue
                m = REPORT.search(text)
                n = next((x for x in NAMED.finditer(text) if x.group(1) not in NOT_NAMES), None)
                if (m or n) and not re.search(r"\b(assume|pretend|imagine|role-?play|persona|what if)\b", text, re.I):
                    named = NAMED.sub(lambda x: x.group(0) if x.group(1) in NOT_NAMES else "[user] " + x.group(2), text)
                    hits.append((ts, "a user report, in your words", "strong", _clip(named)))
                    signal_at = signal_at or ts
                if TICKET.search(text) and not SELF_FILED.search(text):
                    hits.append((ts, "a ticket loaded", "strong", _clip(text, 60)))
                    signal_at = signal_at or ts
            elif d.get("type") == "assistant":
                for b in (d.get("message") or {}).get("content") or []:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    name, inp = b.get("name", ""), b.get("input") or {}
                    if name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                        fp = str(inp.get("file_path", ""))
                        if signal_at and any(fp.startswith(r) for r in roots) and not re.search(r"scratch|/tmp/|\.test\.", fp):
                            hits.append((ts, "a change after a user signal", "level 4",
                                         f"edited {Path(str(inp.get('file_path', '?'))).name}"))
                            signal_at = None
                        continue
                    cmd = str(inp.get("command", "")) if name == "Bash" else json.dumps(inp)[:2000]
                    if name == "Bash" and re.search(r"cat\s*>>?\s*\S|python3? -\s*<<|open\(p\)", cmd):
                        continue  # writing code that mentions a query is not running one
                    if name == "Bash" and set(programs(cmd)) <= {"grep", "rg", "ls", "cat", "head", "tail", "sed", "find", "echo", "cd"}:
                        continue
                    is_db = DB_CALL.search(cmd) or (name.startswith("mcp__") and re.search(
                        r"supabase|neon|firebase|planetscale|postgres", name, re.I) and re.search(r"sql|query", name, re.I))
                    mine = LOCAL.search(cmd) or any(e and e.lower() in cmd.lower() for e in self_emails)
                    if is_db and USER_TABLE.search(cmd) and AGGREGATE.search(cmd) and not mine:
                        hits.append((ts, "usage counted over people", "medium", _clip(cmd)))
                    if LOGS.search(cmd) and LOG_FILTER.search(cmd) and not mine:
                        hits.append((ts, "logs filtered to users", "medium", _clip(cmd)))
                    if TICKET.search(cmd) and not SELF_FILED.search(cmd) and not mine:
                        hits.append((ts, "a ticket loaded", "strong", _clip(cmd, 80)))
                        signal_at = signal_at or ts
                    if OUTREACH.search(cmd) and not mine:
                        hits.append((ts, "a message to users", "medium", _clip(cmd, 80)))
                    if name == "Bash" and "git commit" in cmd and signal_at:
                        msg = re.search(r"-m\s+[\"']([^\"']{1,120})", cmd)
                        hits.append((ts, "a change after a user signal", "level 4",
                                     f"commit \"{_clip(msg.group(1) if msg else 'see git log', 90)}\""))
                        signal_at = None
    # One line per session and kind: the first piece of evidence, and how many times it recurred.
    out, seen = [], {}
    for h in hits:
        k = (h[1], h[2])
        if k in seen:
            seen[k][4] += 1
        else:
            seen[k] = [*h, 1]
            out.append(seen[k])
    return [(ts, kind, st, ev + (f"  (x{n} in this session)" if n > 1 else "")) for ts, kind, st, ev, n in out]


def users_from_git(repo, since):
    """Commits in the window whose message ties the change to a user or a ticket."""
    try:
        out = subprocess.run(["git", "-C", repo, "log", f"--since={since.isoformat()}", "--format=%h %ad %s",
                              "--date=short"], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return []
    return [line for line in out.splitlines() if CHANGE_MSG.search(line)]


def self_emails(repos):
    found = set()
    for r in repos:
        try:
            e = subprocess.run(["git", "-C", r, "config", "user.email"], capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            e = ""
        if e:
            found.add(e)
    return found


def record_times(path):
    """Every timestamp in a session file (prompts, replies, tool calls), for counting active time."""
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            m = re.search(r'"timestamp"\s*:\s*"([^"]+)"', line)
            if m:
                try:
                    yield dt.datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
                except ValueError:
                    continue


ACTIVE_GAP = dt.timedelta(minutes=15)


def active_hours(files, since):
    """Hours with session activity: the gaps between consecutive events, across all sessions merged,
    counting only gaps under 15 minutes. Parallel sessions count once; a long break counts zero."""
    ts = sorted(t for f in files for t in record_times(f) if t >= since)
    total = sum(((b - a) for a, b in zip(ts, ts[1:]) if b - a < ACTIVE_GAP), dt.timedelta())
    return total.total_seconds() / 3600


def cmd_analyze(since, wanted):
    want = {w.rstrip("/") for w in wanted}
    picked = [(tool, f) for tool, cwd, f, _m in sessions(since)
              if any(cwd.rstrip("/").startswith(w) for w in want)]
    if not picked:
        print("No sessions matched those projects.")
        return

    by_day, prompts, tools = Counter(), [], Counter()
    bt = {}
    for tool, f in picked:
        for ts, text in user_turns(f, tool):
            if ts:
                by_day[ts[:10]] += 1
            prompts.append((ts, text))
        tools.update(tool_uses(f, tool))
        for k, v in builder_tools(f, tool).items():
            bt.setdefault(k, Counter()).update(v)

    by_tool = Counter(tool for tool, _ in picked)
    print(f"SESSIONS: {len(picked)} ({', '.join(f'{k} {v}' for k, v in sorted(by_tool.items()))})")
    print(f"PROMPTS: {len(prompts)}")
    print(f"DAYS ACTIVE: {len(by_day)}")
    print(f"ACTIVE SESSION TIME: about {active_hours([f for _t, f in picked], since):.1f} hours "
          f"(time between session events, gaps under 15 minutes, parallel sessions counted once)\n")

    print("ACTIVITY BY DAY")
    for day in sorted(by_day):
        print(f"  {day}  {'#' * min(by_day[day], 50)} {by_day[day]}")

    print("\nTOOL USE")
    for name, n in tools.most_common(12):
        print(f"  {n:>5}  {name}")

    def show(label, c, note=""):
        items = ", ".join(f"{k} ({v})" for k, v in c.most_common(10))
        print(f"  {label:<22} {items or 'none'}{note}")
    # A skill or subagent named plugin:name came from a plugin.
    for k, v in list(bt["skills"].items()) + list(bt["subagents_named"].items()):
        if ":" in k:
            bt["plugins"][k.split(":")[0]] += v
    own = Counter({k: v for k, v in bt["skills"].items() if k not in COURSE_SKILLS})
    course = Counter({k: v for k, v in bt["skills"].items() if k in COURSE_SKILLS})
    print(f"SCAN VERSION: {SCAN_VERSION}")
    print("\nBUILDER TOOLS USED (counts across the confirmed sessions)")
    show("Skills, your own", own)
    show("Skills, course", course)
    show("Slash commands", bt["commands"])
    show("Hooks that ran", bt["hooks"])
    show("Hooks that blocked", bt["hooks_blocked"])
    show("Subagents, named", bt["subagents_named"], "  (defined in .claude/agents, by a plugin, or by you)")
    show("Subagents, built-in", bt["subagents"], "  (ship with Claude Code; Claude may start these on its own)")
    show("MCP servers", bt["mcp"], "  (connectors from the Claude app appear as claude_ai_...)")
    show("Service CLI tools", bt["cli"])
    show("Direct API calls", bt["api_calls"], "  (curl and similar, run by the agent)")
    show("Plugins", bt["plugins"], "  (skills or subagents that came from a plugin)")
    show("Messages to sessions", bt["messages"], "  (to subagents or your other sessions, by recipient)")
    show("Plan mode", bt["plan"], "  (plan tool calls, and turns spent in plan mode)")
    show("Permission modes", bt["modes"], "  (turns in each mode)")
    show("Permission prompts", bt["permissions"], "  (prompts you answered, and calls a rule or check denied)")
    show("Where sessions ran", bt["surfaces"], "  (sessions by surface)")
    show("Worktrees", bt["worktrees"])
    show("Instructions loaded", bt["instructions_loaded"], "  (times each file was loaded)")
    show("Memory written", bt["memory_written"], "  (edits to memory or instruction files)")

    selfs = self_emails(want)
    roots = tuple(w + "/" for w in want)
    uh = sorted(h for tool, f in picked for h in users_signals(f, selfs, tool, since.isoformat()[:19], roots))
    commits = sorted({c for w in want for c in users_from_git(w, since)})
    print("\nUSERS THIS SPRINT (people outside the team, and changes made because of them)")
    if not uh and not commits:
        print("  none found")
    for ts, kind, strength, ev in uh[:40]:
        print(f"  [{ts[:16]}] {strength:<7} {kind}: {ev}")
    for c in commits[:20]:
        print(f"  commit tied to a user or ticket: {_clip(c, 120)}")
    print("  (production lookups by id are not listed: they happen whether or not anyone uses the app)")

    print("\nPROMPTS (chronological, truncated)")
    for ts, text in sorted(prompts, key=lambda x: x[0]):
        one = " ".join(text.split())
        print(f"  [{ts[:16]}] {one[:220]}")


def field(text, label):
    """The value after **Label:** on one line, or the paragraph under a ## Label heading."""
    import re
    m = re.search(r"^\*\*" + re.escape(label) + r":\*\*\s*(.+)$", text, re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^##\s+" + re.escape(label) + r"\s*\n+(.*?)(?=\n##\s|\Z)", text, re.M | re.S)
    if m:
        return " ".join(m.group(1).split())
    return ""


def band(value):
    """A /learn rating in the exam's three bands. Logs before 2026-10-16 used 1 to 5: 1 and 2 read
    as Developing, 3 as Proficient, 4 and 5 as Strong. Anything else is returned unchanged."""
    m = re.match(r"\s*([1-5])\b(.*)", value or "", re.S)
    if not m:
        return value
    word = {"1": "Developing", "2": "Developing", "3": "Proficient", "4": "Strong", "5": "Strong"}[m.group(1)]
    rest = re.sub(r"(shown:\s*)([1-5])\b", lambda x: x.group(1) + band(x.group(2)).split(" (")[0], m.group(2))
    return f"{word} (logged as {m.group(1)} on the old 1 to 5 scale){rest}"


def cmd_learning(since, repo):
    """List the /learn sessions logged in learning/ during the window. Facts only, no score."""
    import re
    folder = Path(repo) / "learning"
    day0 = since.date()
    logs = []
    for f in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        m = re.match(r"(\d{4}-\d{2}-\d{2})-", f.name)
        if not m:
            continue                      # skips 000-learning-template.md
        try:
            day = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if day < day0:
            continue
        text = f.read_text(errors="replace")
        title = re.search(r"^#\s+(?:Learning log:\s*)?(.+)$", text, re.M)
        logs.append({
            "day": day.isoformat(),
            "file": f"learning/{f.name}",
            "section": title.group(1).strip() if title else f.stem,
            "finished": field(text, "Finished"),
            "axis": field(text, "Axis"),
            "time": field(text, "Time"),
            "start": band(field(text, "Starting point")),
            "confidence": band(field(text, "Confidence")),
            "concept": field(text, "Concept"),
            "asked": field(text, "What I asked about"),
            "question": field(text, "Still wondering"),
        })
    print(f"LEARNING SESSIONS: {len(logs)}")
    axes = {}
    for g in logs:
        if g["axis"]:
            axes[g["axis"]] = axes.get(g["axis"], 0) + 1
    if axes:
        print("  by axis: " + ", ".join(f"{k} {v}" for k, v in sorted(axes.items(), key=lambda x: -x[1])))
    for g in logs:
        print(f"\n  {g['day']}  {g['section']}  ({g['file']})")
        for k in ("concept", "time", "finished", "axis", "asked", "start", "confidence", "question"):
            if g[k]:
                print(f"    {k}: {g[k][:300]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", action="version", version=f"sprint_scan {SCAN_VERSION}")
    ap.add_argument("--since", required=True, help="ISO date, e.g. 2026-10-12")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--projects", nargs="*", default=[])
    ap.add_argument("--learning", metavar="REPO", help="list /learn logs in REPO/learning/ since --since")
    a = ap.parse_args()

    try:
        since = dt.datetime.fromisoformat(a.since)
    except ValueError:
        sys.exit(f"Bad --since: {a.since}")
    if since.tzinfo is None:
        since = since.replace(tzinfo=dt.timezone.utc)

    if a.learning:
        cmd_learning(since, a.learning)
    elif a.list:
        cmd_list(since)
    elif a.analyze:
        if not a.projects:
            sys.exit("--analyze needs --projects")
        cmd_analyze(since, a.projects)
    else:
        sys.exit("Pass --list, --analyze, or --learning")


if __name__ == "__main__":
    main()
