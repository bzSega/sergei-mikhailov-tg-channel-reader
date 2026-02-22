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