# 📡 sergei-mikhailov-tg-channel-reader

> OpenClaw skill for reading Telegram channels via MTProto (Pyrogram or Telethon)

An [OpenClaw](https://openclaw.ai) skill that lets your AI agent fetch and summarize posts from any Telegram channel — public or private (if you're subscribed).

## Features

- 📥 Fetch posts from one or multiple channels in one command
- ⏱️ Flexible time windows: `24h`, `7d`, `2w`, or specific date
- 📊 JSON output with views, forwards, and direct links
- 🔒 Secure credential storage via env vars
- 🤖 Works with any public channel — no bot admin required

## Why Use This Skill Instead of Web Monitoring?

OpenClaw can monitor Telegram channels via web scraping, but this skill uses **MTProto** — the same official protocol used by the Telegram app itself. Here's why it matters:

| | Web monitoring | This skill (MTProto) |
|---|---|---|
| **Reliability** | Breaks when Telegram updates its web UI | Always works — official protocol |
| **Speed** | Slow (browser rendering) | Fast — direct API calls |
| **Private channels** | ❌ Public only | ✅ Any channel you're subscribed to |
| **Data richness** | Text only | Views, forwards, links, dates |
| **Rate limits** | Frequent blocks & captchas | Soft limits, sufficient for personal use |
| **Agent integration** | Requires extra parsing | Clean JSON, ready for agent to analyze |

**Bottom line:** if you follow Telegram channels regularly and want your agent to summarize them, this skill is faster, more reliable, and gives you richer data than web monitoring.

## Install via ClawHub

```bash
npx clawhub@latest install sergei-mikhailov-tg-channel-reader
```

Then install Python dependencies:

```bash
cd ~/.openclaw/workspace/skills/sergei-mikhailov-tg-channel-reader
pip install pyrogram tgcrypto telethon
pip install -e .
```

Make sure `~/.local/bin` is in your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Manual Install

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/bzSega/sergei-mikhailov-tg-channel-reader
cd sergei-mikhailov-tg-channel-reader
pip install pyrogram tgcrypto telethon
pip install -e .
```

## Setup

### Step 1 — Get Telegram API credentials

You need a personal Telegram API key. This is free and takes 2 minutes.

1. Open https://my.telegram.org in your browser
2. Enter your phone number (with country code, e.g. `+79991234567`) and click **Send Code**
3. Enter the confirmation code you receive in Telegram
4. Click **"API Development Tools"**
5. Fill in the form:
   - **App title**: any name (e.g. `MyReader`)
   - **Short name**: any short word (e.g. `myreader`)
   - Other fields can be left as default
6. Click **"Create application"**
7. You'll see your credentials:
   - **App api_id** — a number like `12345678`
   - **App api_hash** — a 32-character string like `a1b2c3d4e5f6789012345678abcdef12`

> ⚠️ Keep these credentials private. Never share or commit them to git.

### Step 2 — Set credentials securely

```bash
# Add to ~/.bashrc so they persist across sessions
echo 'export TG_API_ID=12345678' >> ~/.bashrc
echo 'export TG_API_HASH=your_api_hash_here' >> ~/.bashrc
source ~/.bashrc
```

Alternatively, create `~/.tg-reader.json` (never commit this file!):
```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here"
}
```

### Step 3 — Authenticate once

```bash
tg-reader auth
```

You'll be asked for your phone number. After entering it, you'll receive a confirmation code in your Telegram app — look for a message from the official **"Telegram"** service chat (not SMS).

> If the code doesn't arrive — check all devices where Telegram is open (phone, desktop, web).

Authentication creates a session file at `~/.tg-reader-session.session`. You only need to do this once.

### Step 4 — Choose your library (optional)

By default, `tg-reader` uses **Pyrogram**. You can switch to **Telethon** if needed:

**Option 1: Environment variable (persistent)**
```bash
echo 'export TG_USE_TELETHON=true' >> ~/.bashrc
source ~/.bashrc
```

**Option 2: Command flag (one-time)**
```bash
tg-reader fetch @durov --since 24h --telethon
```

**Option 3: Direct commands**
```bash
tg-reader-pyrogram fetch @durov --since 24h  # Force Pyrogram
tg-reader-telethon fetch @durov --since 24h  # Force Telethon
```

### Step 5 — Start reading

```bash
# Last 24 hours from a channel (default: Pyrogram)
tg-reader fetch @durov --since 24h

# Use Telethon instead
tg-reader fetch @durov --since 24h --telethon

# Last week, multiple channels
tg-reader fetch @channel1 @channel2 --since 7d --limit 200

# Human-readable format
tg-reader fetch @channel_name --since 24h --format text
```

## Usage with OpenClaw

Once installed and authenticated, just ask your agent:

> "Summarize the last 24 hours from @durov"
> "What's new in @hacker_news_feed this week?"
> "Check all my tracked channels and give me a digest"

The agent will automatically use `tg-reader` and summarize the results.

## Output Example

```json
{
  "channel": "@durov",
  "fetched_at": "2026-02-22T10:00:00Z",
  "count": 3,
  "messages": [
    {
      "id": 735,
      "date": "2026-02-22T08:15:00Z",
      "text": "Post content here...",
      "views": 120000,
      "forwards": 4200,
      "link": "https://t.me/durov/735"
    }
  ]
}
```

## Troubleshooting

**`tg-reader: command not found`**

Add `~/.local/bin` to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Or run directly with Python:
```bash
python3 -m reader auth
python3 -m reader fetch @channel --since 24h
```

## Library Selection

The skill supports two MTProto implementations that you can switch between:

### Pyrogram (default)
- Modern, actively maintained
- Default choice for `tg-reader` command
- Session file: `~/.tg-reader-session.session`

### Telethon (alternative)
- Mature, stable library
- Useful if you experience issues with Pyrogram
- Session file: `~/.telethon-reader.session`

### How to switch

**Temporary (one command):**
```bash
tg-reader fetch @durov --since 24h --telethon
```

**Permanent (all commands):**
```bash
echo 'export TG_USE_TELETHON=true' >> ~/.bashrc
source ~/.bashrc
```

**Direct commands (bypass auto-selection):**
```bash
tg-reader-pyrogram fetch @durov --since 24h
tg-reader-telethon fetch @durov --since 24h
```

Both implementations use the same API credentials and provide identical functionality.

**Confirmation code not arriving**
- Check all your Telegram devices — the code goes to the Telegram app, not SMS
- Look for a message from the official "Telegram" service chat
- If you hit a rate limit on my.telegram.org, wait a few hours and try again

**`ChannelInvalid` error**
- For public channels: double-check the username spelling
- For private channels: make sure you're subscribed with the authenticated account

**`FloodWait` error**
- Telegram is rate-limiting requests
- The error shows how many seconds to wait — just retry after that

## Security

- ✅ Credentials stored in env vars or `~/.tg-reader.json` (outside the project)
- ✅ Session file stored in home directory (`~/.tg-reader-session.session`)
- ❌ Never commit `TG_API_HASH`, `TG_API_ID`, or `*.session` files

`.gitignore` includes:
```
*.session
*.session-journal
.tg-reader.json
.env
```

## License

MIT — made by [@bzSega](https://github.com/bzSega)
