---
name: sergei-mikhailov-tg-channel-reader
description: Read and summarize posts from Telegram channels via MTProto (Pyrogram). Fetch recent messages, filter by time window, and summarize content.
metadata:
  openclaw:
    emoji: "📡"
    requires:
      bins: ["tg-reader"]
      python: ["pyrogram", "tgcrypto"]
---

# tg-channel-reader

Lets your agent read posts from Telegram channels using MTProto (Pyrogram).
No need to add a bot to the channel — works with any public channel and private channels you're subscribed to.

## Setup (first time)

1. Get your API credentials at https://my.telegram.org → "API Development Tools"
2. Store credentials securely — **never hardcode in files**:

```bash
# Option A: Environment variables (recommended)
export TG_API_ID=12345678
export TG_API_HASH=your_hash_here

# Option B: ~/.tg-reader.json (add to .gitignore!)
{
  "api_id": 12345678,
  "api_hash": "your_hash_here"
}
```

3. Authenticate once (creates session file):
```bash
tg-reader auth
```

## When to Use

Use this skill when the user:
- Asks to "check", "read", or "monitor" a Telegram channel
- Wants a digest or summary of recent posts from channels
- Asks "what's new in @channel" or "summarize last 24h from @channel"
- Wants to track multiple channels and compare content

## How to Use

```bash
# Fetch last 24h from one channel
tg-reader fetch @channel_name --since 24h --format json

# Fetch last 7 days, up to 200 posts
tg-reader fetch @channel_name --since 7d --limit 200

# Fetch multiple channels at once
tg-reader fetch @channel1 @channel2 @channel3 --since 24h

# Human-readable output
tg-reader fetch @channel_name --since 24h --format text
```

## Output Format

JSON output per channel:
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

After running tg-reader, you should:
1. Parse the JSON output
2. Filter out empty/media-only posts if text summary is requested
3. Summarize key themes, top posts by views, and notable links
4. Save summary to `memory/YYYY-MM-DD.md` if user wants to track over time

## Saving Channel List

Store the user's tracked channels in `TOOLS.md`:
```markdown
## Telegram Channels
- @channel1 — description/why tracked
- @channel2 — description/why tracked
```

## Error Handling

- `FloodWait` → wait the specified seconds and retry
- `ChannelInvalid` → channel doesn't exist or user not subscribed (for private)
- Missing credentials → guide user through setup

## Security Notes

- Session file (`~/.tg-reader-session.session`) grants full account access — keep it safe
- Never commit `TG_API_HASH` or session files to git
- `.gitignore` should include: `*.session`, `.tg-reader.json`
