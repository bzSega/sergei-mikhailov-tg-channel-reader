## [0.6.0] - 2026-02-24

### Added
- `--config-file` flag — pass explicit path to config JSON (overrides `~/.tg-reader.json`)
- `--session-file` flag — pass explicit path to session file (overrides default session path)
- Both flags work with all subcommands (`fetch`, `info`, `auth`) and both backends (Pyrogram, Telethon)
- `SKILL.md`: new "Isolated Agents & Cron Jobs" section with usage examples

### Fixed
- Skill now works in isolated sub-agent environments (e.g. OpenClaw cron with `sessionTarget: "isolated"`) where `~/` is not accessible

## [0.5.0] - 2026-02-23

### Added
- `tg-reader info @channel` — new subcommand to fetch channel title, description, subscriber count and link
- `SKILL.md`: documented `info` command in When to Use, How to Use, and Output Format sections
- `SKILL.md`: `~/.tg-reader.json` recommended as primary credentials method for agent/server environments that don't load `.bashrc`/`.zshrc`

## [0.4.3] - 2026-02-23

### Fixed
- `reader.py`: removed `system_lang_code` from Pyrogram `Client` init — parameter is Telethon-only and caused `TypeError` on auth
- `reader.py`: fixed `TypeError: can't compare offset-naive and offset-aware datetimes` when fetching messages — `msg.date` from Pyrogram is UTC-naive, now normalized before comparison with `since`
- `reader.py`: removed iOS device spoofing (`_DEVICE`) — Telegram detects the mismatch between declared client identity and actual behaviour and terminates the session; Pyrogram's default identity is stable

## [0.4.2] - 2026-02-23

### Fixed
- `README.md`: fix `python3 -m reader` fallback → `python3 -m tg_reader_unified`
- `README.md`: add Linux venv install instructions for managed Python environments (Debian/Ubuntu)
- `README.md`: add macOS `~/.zshrc` for `TG_USE_TELETHON` alongside Linux `~/.bashrc`
- `README.md`: update PATH section to cover venv bin path, not just `~/.local/bin`
- `README.md`: add note to confirm phone number with `y` during Pyrogram auth
- `SKILL.md`: add Linux venv install instructions
- `SKILL.md`: add note to confirm phone number with `y` during Pyrogram auth

## [0.4.1] - 2026-02-23

### Security
- `test_session.py`: replaced partial `api_hash[:10]` print with masked output (`***`) to prevent secret leakage in logs or shared terminals
- `SKILL.md`: added `chmod 600` step after auth to restrict session file permissions

## [0.4.0] - 2026-02-23

### Fixed
- `SKILL.md` frontmatter converted to single-line JSON as required by OpenClaw spec
- `requires.env` format corrected to array of strings `["TG_API_ID", "TG_API_HASH"]`
- Removed undocumented `requires.python` field from metadata
- Removed optional env vars (`TG_SESSION`, `TG_USE_TELETHON`) from gating filter
- Added missing `primaryEnv: "TG_API_HASH"` for openclaw.json `apiKey` support
- Auth command in setup guide corrected from `python3 -m reader auth` to `tg-reader auth`
- Fallback command in Error Handling corrected to `python3 -m tg_reader_unified`

### Added
- macOS (`~/.zshrc`) credentials setup alongside Linux (`~/.bashrc`) in agent instructions
- `CLAUDE.md` with project context and documentation references for Claude Code

## [0.2.1] - 2026-02-22

### Added
- Unified entry point (`tg_reader_unified.py`) for automatic selection between Pyrogram and Telethon
- Support for `--telethon` flag for one-time switch to Telethon
- Support for `TG_USE_TELETHON` environment variable for persistent library selection
- Direct commands `tg-reader-pyrogram` and `tg-reader-telethon` for explicit implementation choice

### Changed
- `tg-reader` command now uses unified entry point instead of direct Pyrogram call
- Updated documentation with library selection instructions
- `setup.py` now includes all three entry points

### Improved
- Simplified process for switching between Pyrogram and Telethon for users
- Better OpenClaw integration — single skill supports both libraries

# Changelog

## [0.3.0] - 2026-02-22
### Added
- **Telethon alternative implementation** (`reader_telethon.py`)
- New command `tg-reader-telethon` for users experiencing Pyrogram auth issues
- Comprehensive Telethon documentation (`README_TELETHON.md`)
- Testing guide (`TESTING_GUIDE.md`) with troubleshooting steps
- Session file compatibility notes
- Instructions for copying sessions between machines

### Changed
- Updated `setup.py` to include both Pyrogram and Telethon versions
- Added telethon>=1.24.0 to dependencies
- Enhanced README with Telethon usage section

### Fixed
- Authentication code delivery issues by providing Telethon alternative
- Session management for users with existing Telethon sessions

## [0.2.0] - 2026-02-22
### Added
- Detailed Telegram API setup instructions in README
- Agent guidance in SKILL.md for missing credentials
- PATH fix instructions for tg-reader command not found
- Troubleshooting section with real-world errors

## [0.1.0] - 2026-02-22
### Initial release
- Fetch posts from Telegram channels via MTProto
- Support for multiple channels and time windows
- JSON and text output formats
- Secure credentials via env vars