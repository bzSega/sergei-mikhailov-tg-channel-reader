---
name: sergei-mikhailov-tg-channel-reader
description: Read and summarize posts from Telegram channels via MTProto (Pyrogram or Telethon). Fetch recent messages from public or private channels by time window.
metadata: {"openclaw": {"emoji": "📡", "requires": {"bins": ["tg-reader"], "env": ["TG_API_ID", "TG_API_HASH"]}, "primaryEnv": "TG_API_HASH"}}
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

## Setup & Installation

Full setup instructions are in [README.md](./README.md). Summary:

1. Get Telegram API credentials from https://my.telegram.org → API Development Tools
2. Set `TG_API_ID` and `TG_API_HASH` as environment variables
3. Install the skill and its Python dependencies:
   ```bash
   npx clawhub@latest install sergei-mikhailov-tg-channel-reader
   cd ~/.openclaw/workspace/skills/sergei-mikhailov-tg-channel-reader
   pip install pyrogram tgcrypto telethon && pip install -e .
   ```
   On Linux with managed Python (Ubuntu/Debian), use venv instead:
   ```bash
   python3 -m venv ~/.venv/tg-reader
   ~/.venv/tg-reader/bin/pip install pyrogram tgcrypto telethon && ~/.venv/tg-reader/bin/pip install -e .
   echo 'export PATH="$HOME/.venv/tg-reader/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
   ```
4. Authenticate once: `tg-reader auth`
5. Set session file permissions: `chmod 600 ~/.tg-reader-session.session`

> If the user asks for help with setup, refer them to README.md for full options (env vars, direnv, keychain, etc.).

## When to Use

Use this skill when the user:
- Asks to "check", "read", or "monitor" a Telegram channel
- Wants a digest or summary of recent posts from channels
- Asks "what's new in @channel" or "summarize last 24h from @channel"
- Wants to track multiple channels and compare content
- Wants to know what a channel is about — use `info` to get title, description, subscriber count

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
3. Ask user to set credentials. **Use `~/.tg-reader.json` — it works reliably in all environments** including agents and servers that don't load `.bashrc`/`.zshrc`:
   ```bash
   cat > ~/.tg-reader.json << 'EOF'
   {
     "api_id": their_id,
     "api_hash": "their_hash"
   }
   EOF
   chmod 600 ~/.tg-reader.json
   ```
   Alternatively, env vars (only if running interactively in a shell):
   ```bash
   # macOS (zsh)
   echo 'export TG_API_ID=their_id' >> ~/.zshrc
   echo 'export TG_API_HASH=their_hash' >> ~/.zshrc
   source ~/.zshrc

   # Linux (bash)
   echo 'export TG_API_ID=their_id' >> ~/.bashrc
   echo 'export TG_API_HASH=their_hash' >> ~/.bashrc
   source ~/.bashrc
   ```
   > **Note:** Agents and servers typically don't load `.bashrc`/`.zshrc`. If credentials are not found after setting env vars, use `~/.tg-reader.json` instead.
4. Run auth:
   ```bash
   tg-reader auth
   ```
   - Pyrogram will ask to confirm the phone number — answer `y`
   - User will receive a code in their Telegram app (message from "Telegram" service chat)
   - If code doesn't arrive — check all devices where Telegram is open
5. Set secure permissions on the session file:
   ```bash
   chmod 600 ~/.tg-reader-session.session
   ```
6. After auth succeeds — retry the original request

## How to Use

```bash
# Get channel title, description and subscriber count
tg-reader info @channel_name

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

# Explicit config and session paths (for isolated agents / cron jobs)
tg-reader fetch @channel_name --since 6h \
  --config-file /home/user/.tg-reader.json \
  --session-file /home/user/.tg-reader-session
```

If `tg-reader` command is not found, use:
```bash
python3 -m tg_reader_unified fetch @channel_name --since 24h
```

## Isolated Agents & Cron Jobs

When the skill runs inside an isolated sub-agent (e.g. `sessionTarget: "isolated"` in OpenClaw cron), it may not have access to the user's home directory. Use `--config-file` and `--session-file` to pass explicit paths:

```bash
tg-reader fetch @channel --since 6h \
  --config-file /home/user/.tg-reader.json \
  --session-file /home/user/.tg-reader-session
```

Both flags work with all subcommands (`fetch`, `info`, `auth`) and with both backends (Pyrogram and Telethon).

## Output Format

### info
```json
{
  "id": -1001234567890,
  "title": "Channel Name",
  "username": "channel_name",
  "description": "About this channel...",
  "members_count": 42000,
  "link": "https://t.me/channel_name"
}
```

### fetch
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
- `tg-reader: command not found` → use `python3 -m tg_reader_unified` instead
- `AUTH_KEY_UNREGISTERED` → session expired or invalidated; delete session file and re-auth:
  ```bash
  rm -f ~/.tg-reader-session.session
  tg-reader auth
  ```
- Auth code not arriving / connection issues → use the verbose debug script:
  ```bash
  python3 debug_auth.py
  ```
  It shows full MTProto-level logs so you can see exactly where the connection fails.

## Security Notes

- Session file (`~/.tg-reader-session.session`) grants **full account access** — keep it safe
- Never share or commit `TG_API_HASH` or session files
- `TG_API_HASH` should be treated as a secret — store in env vars, not in files tracked by git
