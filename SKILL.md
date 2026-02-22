---
name: sergei-mikhailov-tg-channel-reader
description: Read and summarize posts from Telegram channels via MTProto (Pyrogram or Telethon). Fetch recent messages from public or private channels by time window.
metadata:
  openclaw:
    emoji: "📡"
    requires:
      bins: ["tg-reader"]
      python: ["pyrogram", "tgcrypto", "telethon"]
      env:
        - name: TG_API_ID
          description: Telegram API ID from my.telegram.org. Required for MTProto authentication.
          required: true
        - name: TG_API_HASH
          description: Telegram API Hash from my.telegram.org. Treat as a secret — never commit to git.
          required: true
          secret: true
        - name: TG_SESSION
          description: Path to session file (optional, default is ~/.tg-reader-session). Session grants full account access — store securely.
          required: false
        - name: TG_USE_TELETHON
          description: Set to "true" to use Telethon instead of Pyrogram (optional).
          required: false
---

# tg-channel-reader

Lets your agent read posts from Telegram channels using MTProto (Pyrogram or Telethon).
Works with any public channel and private channels the user is subscribed to.

> ⚠️ **Security notice:** This skill requires `TG_API_ID` and `TG_API_HASH` credentials from [my.telegram.org](https://my.telegram.org). The resulting session file grants full access to the Telegram account — store it securely and never share it.

## Library Selection

The skill supports two MTProto implementations:
- **Pyrogram** (default) — modern, actively maintained
- **Telethon** — alternative, useful if Pyrogram has issues

Users can choose the library via:
1. **Environment variable** (persistent):
   ```bash
   export TG_USE_TELETHON=true
   ```
2. **Command flag** (one-time):
   ```bash
   tg-reader fetch @channel --since 24h --telethon
   ```

Direct commands are also available:
- `tg-reader-pyrogram` — force Pyrogram
- `tg-reader-telethon` — force Telethon

## When to Use

Use this skill when the user:
- Asks to "check", "read", or "monitor" a Telegram channel
- Wants a digest or summary of recent posts from channels
- Asks "what's new in @channel" or "summarize last 24h from @channel"
- Wants to track multiple channels and compare content

## Before Running — Check Credentials

**Always check credentials before fetching.** Run:

```bash
tg-reader fetch @durov --since 1h --limit 1
```

If you see `{"error": "Missing credentials..."}` — stop and guide the user:

1. Tell the user they need a Telegram API key from https://my.telegram.org
2. Walk them through these exact steps:
   - Go to https://my.telegram.org and log in with their phone number
   - Click **"API Development Tools"**
   - Fill in "App title" (any name) and "Short name" (any short word)
   - Click **"Create application"**
   - Copy **App api_id** (a number) and **App api_hash** (32-character string)
3. Ask user to set credentials:
   ```bash
   echo 'export TG_API_ID=their_id' >> ~/.bashrc
   echo 'export TG_API_HASH=their_hash' >> ~/.bashrc
   source ~/.bashrc
   ```
4. Run auth:
   ```bash
   python3 -m reader auth
   ```
   - User will receive a code in their Telegram app (message from "Telegram" service chat)
   - If code doesn't arrive — check all devices where Telegram is open
5. After auth succeeds — retry the original request

## How to Use

```bash
# Fetch last 24h from one channel (default: Pyrogram)
tg-reader fetch @channel_name --since 24h --format json

# Use Telethon instead (one-time)
tg-reader fetch @channel_name --since 24h --telethon

# Fetch last 7 days, up to 200 posts
tg-reader fetch @channel_name --since 7d --limit 200

# Fetch multiple channels at once
tg-reader fetch @channel1 @channel2 @channel3 --since 24h

# Human-readable output
tg-reader fetch @channel_name --since 24h --format text

# Force specific library
tg-reader-pyrogram fetch @channel_name --since 24h
tg-reader-telethon fetch @channel_name --since 24h
```

If `tg-reader` command is not found, use:
```bash
python3 -m tg_reader_unified fetch @channel_name --since 24h
```

## Output Format

```json
{
  "channel": "@channel_name",
  "fetched_at": "2026-02-22T10:00:00Z",
  "since": "2026-02-21T10:00:00Z",
  "count": 12,
  "messages": [
    {
      "id": 1234,
      "date": "2026-02-22T09:30:00Z",
      "text": "Post content...",
      "views": 5200,
      "forwards": 34,
      "link": "https://t.me/channel_name/1234"
    }
  ]
}
```

## After Fetching

1. Parse the JSON output
2. Filter out empty/media-only posts if text summary is requested
3. Summarize key themes, top posts by views, notable links
4. Save summary to `memory/YYYY-MM-DD.md` if user wants to track over time

## Saving Channel List

Store the user's tracked channels in `TOOLS.md`:
```markdown
## Telegram Channels
- @channel1 — why tracked
- @channel2 — why tracked
```

## Error Handling

- `Missing credentials` → guide user through setup (see above)
- `FloodWait` → tell user to wait N seconds and retry
- `ChannelInvalid` → channel doesn't exist or user not subscribed (for private)
- `tg-reader: command not found` → use `python3 -m reader` instead

## Security Notes

- Session file (`~/.tg-reader-session.session`) grants **full account access** — keep it safe
- Never share or commit `TG_API_HASH` or session files
- `TG_API_HASH` should be treated as a secret — store in env vars, not in files tracked by git
