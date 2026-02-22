# 📡 sergei-mikhailov-tg-channel-reader

> OpenClaw skill for reading Telegram channels via MTProto (Pyrogram)

An [OpenClaw](https://openclaw.ai) skill that lets your AI agent fetch and summarize posts from any Telegram channel — public or private (if you're subscribed).

## Features

- 📥 Fetch posts from one or multiple channels in one command
- ⏱️ Flexible time windows: `24h`, `7d`, `2w`, or specific date
- 📊 JSON output with views, forwards, and direct links
- 🔒 Secure credential storage via env vars
- 🤖 Works with any public channel — no bot admin required

## Quick Start

### 1. Install

```bash
pip install pyrogram tgcrypto
pip install -e .
```

### 2. Get Telegram API credentials

Go to https://my.telegram.org → "API Development Tools" → create an app.

### 3. Set credentials (securely)

```bash
export TG_API_ID=12345678
export TG_API_HASH=your_api_hash_here
```

Or create `~/.tg-reader.json` (never commit this file!):
```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here"
}
```

### 4. Authenticate once

```bash
tg-reader auth
```

### 5. Start reading

```bash
# Last 24 hours from a channel
tg-reader fetch @durov --since 24h

# Last week, multiple channels
tg-reader fetch @channel1 @channel2 --since 7d --limit 200

# Human-readable format
tg-reader fetch @channel_name --since 24h --format text
```

## Usage with OpenClaw

Once installed, your agent can use it automatically. Just ask:

> "Summarize the last 24 hours from @ProductHunt"
> "What's new in @hacker_news_feed this week?"
> "Check all my tracked channels and give me a digest"

## Security

- ✅ Credentials stored in env vars or `~/.tg-reader.json` (outside the project)
- ✅ Session file stored in home directory (`~/.tg-reader-session.session`)
- ❌ Never commit `TG_API_HASH`, `TG_API_ID`, or `*.session` files

`.gitignore` includes:
```
*.session
.tg-reader.json
.env
```

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

## License

MIT — made by [@bzsega](https://github.com/bzsega)
