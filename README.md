# 📡 sergei-mikhailov-tg-channel-reader

> OpenClaw skill for reading Telegram channels via MTProto (Pyrogram)

An [OpenClaw](https://openclaw.ai) skill that lets your AI agent fetch and summarize posts from any Telegram channel — public or private (if you're subscribed).

## Features

- 📥 Fetch posts from one or multiple channels in one command
- ⏱️ Flexible time windows: `24h`, `7d`, `2w`, or specific date
- 📊 JSON output with views, forwards, and direct links
- 🔒 Secure credential storage via env vars
- 🤖 Works with any public channel — no bot admin required

## Install via ClawHub

```bash
npx clawhub@latest install sergei-mikhailov-tg-channel-reader
```

## Manual Install (as OpenClaw skill)

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/bzSega/sergei-mikhailov-tg-channel-reader
cd sergei-mikhailov-tg-channel-reader
pip install pyrogram tgcrypto
pip install -e .
```

After install, make sure `~/.local/bin` is in your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Then verify:

```bash
tg-reader --help
```

## Setup

### 1. Get Telegram API credentials

Go to https://my.telegram.org → "API Development Tools" → create an app.

You'll get:
- `App api_id` — a number like `12345678`
- `App api_hash` — a 32-character string like `a1b2c3d4e5f6789012345678abcdef12`

### 2. Set credentials (securely)

```bash
# Option A: Environment variables (recommended)
export TG_API_ID=12345678
export TG_API_HASH=your_api_hash_here

# Add to ~/.bashrc to persist across sessions:
echo 'export TG_API_ID=12345678' >> ~/.bashrc
echo 'export TG_API_HASH=your_api_hash_here' >> ~/.bashrc
```

Or create `~/.tg-reader.json` (never commit this file!):
```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here"
}
```

### 3. Authenticate once

```bash
tg-reader auth
```

You'll receive a confirmation code in your Telegram app (look for a message from the official "Telegram" service chat).

## Usage

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

> "Summarize the last 24 hours from @durov"  
> "What's new in @hacker_news_feed this week?"  
> "Check all my tracked channels and give me a digest"

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

Or run directly with:
```bash
python3 -m reader auth
python3 -m reader fetch @channel --since 24h
```

**Confirmation code not arriving**  
- Check all your Telegram devices — the code goes to the Telegram app, not SMS
- Look for a message from the official "Telegram" service chat
- If you hit a rate limit on my.telegram.org, wait a few hours and try again

**FloodWait error**  
Telegram is rate-limiting requests. The error message will tell you how many seconds to wait.

## Security

- ✅ Credentials stored in env vars or `~/.tg-reader.json` (outside the project)
- ✅ Session file stored in home directory (`~/.tg-reader-session.session`)
- ❌ Never commit `TG_API_HASH`, `TG_API_ID`, or `*.session` files

## License

MIT — made by [@bzSega](https://github.com/bzSega)
