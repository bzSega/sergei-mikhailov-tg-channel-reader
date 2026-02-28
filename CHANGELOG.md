# Changelog

---

## [0.7.1] - 2026-02-28

**Теперь скилл не падает, если канал закрыт или вас забанили.** Раньше одна ошибка ломала весь запрос. Теперь агент получает понятный ответ с типом ошибки и подсказкой, что делать дальше — удалить канал из списка, подождать или попросить у вас новую ссылку-приглашение.

### Improved
- Channel error handling: both Pyrogram and Telethon backends now catch `ChannelPrivate`, `ChannelBanned`, `ChatForbidden`, `ChatRestricted`, `UserBannedInChannel`, `InviteHashExpired`, and more
- Errors return structured JSON with `error_type` (access_denied, banned, not_found, invite_expired, flood_wait) and `action` field for agent automation
- `SKILL.md`: updated Error Handling section with error_type/action reference table

---

## [0.7.0] - 2026-02-28

**Новая команда `tg-reader-check` — быстрая диагностика за секунду.** Агент запускает её перед чтением каналов и сразу видит, всё ли на месте: credentials, session-файл, нужные библиотеки. Если что-то не так — получает конкретную подсказку, как починить. Больше никаких загадочных ошибок при первом запуске.

### Added
- `tg-reader-check` command — offline diagnostic that verifies credentials, session files, and backend availability
- Outputs structured JSON with `status`, `credentials`, `session`, `backends`, and `problems` fields
- Stale session detection: warns when config points to an older session while a newer one exists (common after re-auth)
- Shows `config_session_override` and `default_path` when config overrides the default session — helps spot mismatches
- Supports `--config-file` and `--session-file` flags (same as reader commands)
- `SKILL.md`: new "Pre-flight Check" section; agent should run `tg-reader-check` before fetching
- `_find_session_files()` deduplication fix (Python 3.13+ `glob` matches dotfiles with `*`)

---

## [0.6.1] - 2026-02-28

**Скилл больше не зависает, если session-файл потерялся.** Раньше при отсутствии файла Telegram молча просил пройти авторизацию заново — агент не мог это обработать. Теперь вы получите JSON с объяснением, где файл ожидался, какие session-файлы найдены на диске, и точную команду для исправления.

### Fixed
- Session file validation: `fetch` and `info` commands now check that the `.session` file exists before connecting, instead of silently triggering a re-auth prompt
- When the session file is missing, both Pyrogram and Telethon backends output a structured JSON error with: expected path, list of found `.session` files in `~` and CWD, and a suggested `--session-file` fix
- `get_config()` now strips `.session` suffix if the user passes a full filename (e.g. `--session-file /path/to/foo.session`), preventing Pyrogram/Telethon from looking for `foo.session.session`

---

## [0.6.0] - 2026-02-24

**Скилл теперь работает в автоматических задачах (cron) и изолированных агентах.** Если ваш агент работает по расписанию или в песочнице, где нет доступа к домашней папке — просто передайте путь к конфигу и session-файлу явно. Всё заработает без танцев с бубном.

### Added
- `--config-file` flag — pass explicit path to config JSON (overrides `~/.tg-reader.json`)
- `--session-file` flag — pass explicit path to session file (overrides default session path)
- Both flags work with all subcommands (`fetch`, `info`, `auth`) and both backends (Pyrogram, Telethon)
- `SKILL.md`: new "Isolated Agents & Cron Jobs" section with usage examples

### Fixed
- Skill now works in isolated sub-agent environments (e.g. OpenClaw cron with `sessionTarget: "isolated"`) where `~/` is not accessible

---

## [0.5.0] - 2026-02-23

**Новая команда `tg-reader info` — узнайте всё о канале за секунду.** Название, описание, количество подписчиков и ссылка. Удобно, чтобы проверить канал перед тем, как читать его посты, или собрать список каналов с описаниями.

### Added
- `tg-reader info @channel` — new subcommand to fetch channel title, description, subscriber count and link
- `SKILL.md`: documented `info` command in When to Use, How to Use, and Output Format sections
- `SKILL.md`: `~/.tg-reader.json` recommended as primary credentials method for agent/server environments that don't load `.bashrc`/`.zshrc`

---

## [0.4.3] - 2026-02-23

**Исправлены три бага, из-за которых авторизация и чтение постов могли ломаться.** Если раньше `tg-reader auth` выдавал непонятную ошибку или посты не загружались — обновите до этой версии.

### Fixed
- `reader.py`: removed `system_lang_code` from Pyrogram `Client` init — parameter is Telethon-only and caused `TypeError` on auth
- `reader.py`: fixed `TypeError: can't compare offset-naive and offset-aware datetimes` when fetching messages — `msg.date` from Pyrogram is UTC-naive, now normalized before comparison with `since`
- `reader.py`: removed iOS device spoofing (`_DEVICE`) — Telegram detects the mismatch between declared client identity and actual behaviour and terminates the session; Pyrogram's default identity is stable

---

## [0.4.2] - 2026-02-23

**Улучшена документация для macOS и Linux.** Инструкции по установке теперь покрывают оба варианта, включая виртуальные окружения Python на Ubuntu/Debian.

### Fixed
- `README.md`: fix `python3 -m reader` fallback to `python3 -m tg_reader_unified`
- `README.md`: add Linux venv install instructions for managed Python environments (Debian/Ubuntu)
- `README.md`: add macOS `~/.zshrc` for `TG_USE_TELETHON` alongside Linux `~/.bashrc`
- `README.md`: update PATH section to cover venv bin path, not just `~/.local/bin`
- `README.md`: add note to confirm phone number with `y` during Pyrogram auth
- `SKILL.md`: add Linux venv install instructions
- `SKILL.md`: add note to confirm phone number with `y` during Pyrogram auth

---

## [0.4.1] - 2026-02-23

**Повышена безопасность.** Session-файл теперь защищён правами доступа, а секретные ключи больше не попадают в логи.

### Security
- `test_session.py`: replaced partial `api_hash[:10]` print with masked output (`***`) to prevent secret leakage in logs or shared terminals
- `SKILL.md`: added `chmod 600` step after auth to restrict session file permissions

---

## [0.4.0] - 2026-02-23

**Скилл теперь корректно подключается к OpenClaw.** Исправлен формат метаданных в SKILL.md, чтобы OpenClaw мог автоматически определять, что скиллу нужны credentials от Telegram.

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

---

## [0.3.0] - 2026-02-22

**Добавлен второй движок — Telethon.** Если у вас не приходит код авторизации через Pyrogram или возникают другие проблемы с подключением — попробуйте Telethon. Одна команда, тот же результат.

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

---

## [0.2.1] - 2026-02-22

**Одна команда `tg-reader` — и скилл сам выберет лучший движок.** Больше не нужно думать, Pyrogram или Telethon — всё работает автоматически. Но если хотите управлять вручную — флаг `--telethon` или переменная окружения к вашим услугам.

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

---

## [0.2.0] - 2026-02-22

**Подробные инструкции по установке и настройке.** Теперь даже если вы никогда не работали с Telegram API — пошаговый гайд проведёт вас от создания приложения на my.telegram.org до первого запроса.

### Added
- Detailed Telegram API setup instructions in README
- Agent guidance in SKILL.md for missing credentials
- PATH fix instructions for tg-reader command not found
- Troubleshooting section with real-world errors

---

## [0.1.0] - 2026-02-22

**Первый релиз! Читайте Telegram-каналы прямо из терминала.** Получайте посты из публичных и приватных каналов за любой период — в JSON для автоматизации или в текстовом формате для чтения глазами.

### Initial release
- Fetch posts from Telegram channels via MTProto
- Support for multiple channels and time windows
- JSON and text output formats
- Secure credentials via env vars
