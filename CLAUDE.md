# Project Notes for Claude

## Reference Documentation

Before answering any question about ClawHub commands, SKILL.md format, or skill configuration — fetch and read the relevant documentation page first:

- https://docs.openclaw.ai/ - OpenClaw documentation
- https://docs.openclaw.ai/tools/clawhub — ClawHub CLI commands (install, update, list, publish, etc.)
- https://docs.openclaw.ai/tools/skills — SKILL.md structure and frontmatter spec
- https://docs.openclaw.ai/tools/skills-config — skill configuration and openclaw.json
- https://docs.pyrogram.org/ — Pyrogram API reference; fetch before answering any question about Pyrogram behaviour, errors, or usage
- https://tl.telethon.dev/ — Telethon TL reference; fetch before answering any question about Telethon behaviour, errors, or usage

### ClawHub CLI reference (from docs)

```
clawhub install <slug>
clawhub update <slug>
clawhub update --all
clawhub update --version <version>   # single slug only
clawhub update --force               # overwrite when local files don't match published version
clawhub list                         # reads .clawhub/lock.json
```

## Key conventions

- **Open-source project.** Everything checked into this repo is publicly visible on GitHub and the ClawHub registry. Two consequences:
  - **English only** for every file that lives in the repo: code, code comments, docstrings, CHANGELOG, commit messages, PR titles and bodies, issue text, README, SKILL.md body, files under `tasks/`. Conversational chat in other languages is fine; anything written to disk inside the repo is English.
  - **No sensitive data ever.** Never paste into a repo-tracked file: real `TG_API_ID` / `TG_API_HASH` / session blobs / `.tg-reader-state.json` content / personal absolute paths (`/Users/<name>/...`, `/home/<name>/...`), real channel IDs the user does not want public, OAuth tokens, or any other secret. Use placeholders (`<your_api_id>`, `~/path/to/...`) and reference auto-memory by file name only — never by its full host-local path. Before saving or committing any new file, scan it for these patterns.
- **CHANGELOG style:** Lead with a user-friendly description (what changed and why it matters). Technical details (function names, error types, etc.) are allowed after the plain-language summary.
- `SKILL.md` frontmatter `metadata` must be a **single-line JSON** with the `openclaw` namespace:
  ```
  metadata: {"openclaw": {"requires": {"bins": [...], "env": [...]}, "primaryEnv": "..."}}
  ```
- `name` in SKILL.md frontmatter is the registry package ID (e.g. `sergei-mikhailov-stt`), not a display name
- Display name is the `#` heading in the body of SKILL.md

---

## Project: sergei-mikhailov-tg-channel-reader

**Type:** OpenClaw skill (Python package published to ClawHub registry)
**Registry slug:** `sergei-mikhailov-tg-channel-reader`
**ClawHub display name:** `Telegram Channel Reader` (pass `--name "Telegram Channel Reader"` when publishing)
**Current version:** 0.9.4
**License:** MIT

### What it does

Reads posts from Telegram channels via MTProto (official protocol). Supports Pyrogram (default) and Telethon as interchangeable backends. Outputs JSON or plain text.

### Key files

| File | Purpose |
|------|---------|
| `SKILL.md` | OpenClaw skill definition — frontmatter + agent instructions |
| `setup.py` | Python package config, entry points, dependencies |
| `reader.py` | Pyrogram implementation |
| `reader_telethon.py` | Telethon implementation |
| `tg_reader_unified.py` | Unified entry point — auto-selects backend |
| `tg_check.py` | Offline diagnostic script (`tg-reader-check`) |
| `tg_state.py` | Read-tracking state management (load/save per-channel last_read_id) |
| `CHANGELOG.md` | Version history |
| `DISCLAIMER.md` | Legal disclaimer |
| `README_TELETHON.md` | Telethon-specific docs |
| `TESTING_GUIDE.md` | Troubleshooting & test scenarios |

### Entry points (from setup.py)

```
tg-reader              → tg_reader_unified:main   (auto-selects backend)
tg-reader-pyrogram     → reader:main              (force Pyrogram)
tg-reader-telethon     → reader_telethon:main     (force Telethon)
tg-reader-check        → tg_check:main            (offline diagnostic)
```

### Dependencies

```
pyrofork>=2.3.69    # drop-in replacement for pyrogram (Aug 2023, frozen); current TL schema; same `pyrogram` import namespace; sessions format-compatible
tgcrypto>=1.2.0
telethon>=1.24.0
python>=3.9
```

**Important:** Do not declare `pyrogram` as a dependency. The PyPI `pyrogram` package is pinned at 2.0.106 from Aug 2023 and silently drops content for posts with newer TL constructor IDs (rolled out in May 2026 and later). `pyrofork` ships the current schema and installs under the `pyrogram` import namespace, so `from pyrogram import Client` still works unchanged in `reader.py`. Existing user sessions on disk continue to work without re-auth.

### Environment variables

| Var | Required | Notes |
|-----|----------|-------|
| `TG_API_ID` | Yes | Numeric ID from my.telegram.org |
| `TG_API_HASH` | Yes | Secret — treat like a password, never commit |
| `TG_SESSION` | No | Path to session file (default: `~/.tg-reader-session`) |
| `TG_USE_TELETHON` | No | Set to `"true"` to use Telethon instead of Pyrogram |
| `TG_READ_UNREAD` | No | Set to `"true"` to enable read_unread mode (env overrides config) |
| `TG_STATE_FILE` | No | Path to state file (default: `~/.tg-reader-state.json`) |

### .gitignore (critical — never commit these)

```
*.session
*.session-journal
.tg-reader.json
.tg-reader-state.json
.env
```

### SKILL.md frontmatter note

`metadata` is single-line JSON as required by spec (fixed 2026-02-23).

### Publishing workflow

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Ensure `SKILL.md` is valid per registry spec
4. Publish via ClawHub CLI (check docs for exact command)

### Security constraints

- **Never** commit `TG_API_HASH`, `TG_API_ID`, or `*.session` files
- Session file (`~/.tg-reader-session.session`) grants full Telegram account access
- Credentials belong in env vars or `~/.tg-reader.json` (outside the repo)

---

## Session workflow rules

### End-of-session retrospective (every successful session, daily)

At the end of every working session — before the user closes the session or moves on — perform a short retrospective and persist the lessons to auto-memory so future sessions can build on them:

1. **What was useful** — what techniques, file locations, commands, or facts proved valuable during this session that were not obvious from the code/CLAUDE.md alone. Save as a `project` or `reference` memory if it's project-knowledge, or `feedback` if it's a working preference.
2. **What went wrong** — any mistakes, wrong assumptions, dead ends, wasted tool calls, or things the user had to correct. Save as a `feedback` memory with the `**Why:**` line citing the actual incident from this session, so the next session has concrete evidence (not a vague rule).
3. **What to do differently next time** — translate each mistake into a concrete `**How to apply:**` instruction.

Do not save trivia. Save only items that would change behaviour in a future session. Update existing memory files instead of creating duplicates. Trim or remove memories that the session proved wrong or outdated.

This retrospective is mandatory at session close even if the work felt smooth — successful patterns also deserve a memory entry so I don't drift away from them.

### Code review before commit/push/deploy

For any non-trivial change to this project (new feature, bugfix that touches >1 file, refactor, dependency or version bump, security-relevant edit), the flow is:

1. Make the changes on a feature branch (do **not** commit to `main` directly).
2. Open a pull request against `main` — `gh pr create` with a clear title and Summary/Test plan body.
3. Run the `/review` slash command (and `/security-review` when the change touches credentials, session files, env handling, or any code with a security boundary) against that PR.
4. Read the review output carefully and **fix every legitimate issue** found before proceeding. If a finding is a false positive, explain why in chat.
5. Only **after** the review issues are resolved, propose to the user the next actions: commit final fixes, push, merge the PR, deploy / publish (e.g. `clawhub publish`, version bump).

Never skip steps 3–4 to save time. The reason this rule exists: small "obvious" changes have shipped bugs and security regressions in this project before (see CHANGELOG entries for 0.8.11, 0.8.12, 0.9.1 — all single-commit fixes for issues that a review would have caught). Treat every change as if a reviewer will see it, because one will.

Trivial exception — for typo fixes in markdown, single-line comment edits, and CHANGELOG-only changes: keep the feature branch and the PR, but a quick visual scan replaces the formal `/review` step. The user must still confirm before push and merge.

### Task tracking — `tasks/` folder

All non-trivial plans and tasks must be recorded as markdown files in the `tasks/` folder at the repo root, named `task-NNNN.md` with a zero-padded 4-digit counter (e.g. `task-0001.md`, `task-0042.md`). Number monotonically — never reuse, never renumber.

Each `task-NNNN.md` file must contain:

- **Title** (`#` heading) — short noun phrase describing the task
- **Status** — one of `planned` / `in-progress` / `done` / `cancelled`, with a date
- **Context** — what prompted the task, what problem it solves
- **Plan** — if a planning step happened (plan mode, `/plan`, or a structured design), paste or link the plan here. If there was no formal plan, write a 2–4 bullet outline of the intended approach.
- **Result / outcome** — what was actually built, links to commits / PRs / files changed. Fill this in as work progresses, finalize on `done`.
- **Lessons** — optional; copy here anything that also became an auto-memory entry (cross-reference the memory file name).

Update the task index in this CLAUDE.md (below) every time a task file is created, status-changed, or finished. The index is the authoritative summary so a query like "what tasks did we have?" can be answered by reading just CLAUDE.md, with file dives only when details are needed.

**Status flips happen inside the same PR that delivers the work — never in a separate follow-up PR.** Concretely: in the final commit before clicking merge, the `Status` line in the task file and the matching index row in CLAUDE.md both flip to `done` (with the merge date), the `Result / outcome` section is rewritten in past tense, and only then does the PR get merged. The trivial exception in the Code-review rule above applies — a `/review` pass is not required for that final flip-to-done commit, just a visual scan. No second "bookkeeping PR" after the fact.

#### Task index

| # | Title | Status | File |
|---|-------|--------|------|
| 0001 | Audit project + add session workflow & task-tracking rules to CLAUDE.md | done (2026-05-16) | [tasks/task-0001.md](tasks/task-0001.md) |
| 0002 | Surface link-preview / web_page content in reader output | done (2026-05-16) | [tasks/task-0002.md](tasks/task-0002.md) |
| 0003 | Migrate Pyrogram backend to pyrofork (restore recent posts) | done (2026-05-16) | [tasks/task-0003.md](tasks/task-0003.md) |
