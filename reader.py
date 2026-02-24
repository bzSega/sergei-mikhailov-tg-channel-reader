#!/usr/bin/env python3
"""
tg-channel-reader — Telegram channel reader skill for OpenClaw
Reads posts from public/private Telegram channels via MTProto (Pyrogram)
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from pyrogram import Client
    from pyrogram.errors import FloodWait, ChannelInvalid, UsernameNotOccupied
except ImportError:
    print(json.dumps({"error": "pyrogram not installed. Run: pip install pyrogram tgcrypto"}))
    sys.exit(1)


# Use Pyrogram's default device identity (Python MTProto client).
# Spoofing a mobile client causes Telegram to terminate sessions — the
# behaviour doesn't match and it's detected server-side.
_DEVICE: dict = {}

# ── Config ──────────────────────────────────────────────────────────────────

def get_config(config_file=None, session_file=None):
    """Load credentials from env or config file (env takes priority).

    Args:
        config_file: Explicit path to config JSON (overrides ~/.tg-reader.json)
        session_file: Explicit path to session file (overrides default and config value)
    """
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    session_name = os.environ.get("TG_SESSION", str(Path.home() / ".tg-reader-session"))

    if not api_id or not api_hash:
        config_path = Path(config_file) if config_file else Path.home() / ".tg-reader.json"
        if config_path.exists():
            with open(config_path) as f:
                cfg = json.load(f)
                api_id = api_id or cfg.get("api_id")
                api_hash = api_hash or cfg.get("api_hash")
                session_name = cfg.get("session", session_name)

    # Explicit --session-file overrides everything
    if session_file:
        session_name = session_file

    if not api_id or not api_hash:
        print(json.dumps({
            "error": "Missing credentials. Set TG_API_ID and TG_API_HASH env vars, "
                     "or create ~/.tg-reader.json with {\"api_id\": ..., \"api_hash\": \"...\"}. "
                     "For isolated agents, pass --config-file /path/to/tg-reader.json"
        }))
        sys.exit(1)

    return int(api_id), api_hash, session_name


# ── Core ─────────────────────────────────────────────────────────────────────

def parse_since(since: str) -> datetime:
    """Parse --since flag: '24h', '7d', '2026-02-01', etc."""
    since = since.strip()
    now = datetime.now(timezone.utc)
    if since.endswith("h"):
        return now - timedelta(hours=int(since[:-1]))
    if since.endswith("d"):
        return now - timedelta(days=int(since[:-1]))
    if since.endswith("w"):
        return now - timedelta(weeks=int(since[:-1]))
    # Try ISO date
    try:
        dt = datetime.fromisoformat(since)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        raise ValueError(f"Cannot parse --since value: {since!r}. Use '24h', '7d', or 'YYYY-MM-DD'.")


async def fetch_messages(channel: str, since: datetime, limit: int, include_media: bool,
                         config_file=None, session_file=None):
    api_id, api_hash, session_name = get_config(config_file, session_file)

    messages = []
    async with Client(session_name, api_id=api_id, api_hash=api_hash, **_DEVICE) as app:
        try:
            async for msg in app.get_chat_history(channel, limit=limit):
                msg_date = msg.date if msg.date.tzinfo else msg.date.replace(tzinfo=timezone.utc)
                if msg_date < since:
                    break
                entry = {
                    "id": msg.id,
                    "date": msg_date.isoformat(),
                    "text": msg.text or msg.caption or "",
                    "views": msg.views,
                    "forwards": msg.forwards,
                    "link": f"https://t.me/{channel.lstrip('@')}/{msg.id}",
                }
                if include_media and msg.media:
                    entry["media_type"] = str(msg.media)
                messages.append(entry)
        except (ChannelInvalid, UsernameNotOccupied) as e:
            return {"error": str(e), "channel": channel}
        except FloodWait as e:
            return {"error": f"FloodWait: retry after {e.value}s", "channel": channel}

    return {
        "channel": channel,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "since": since.isoformat(),
        "count": len(messages),
        "messages": messages,
    }


async def fetch_multiple(channels: list, since: datetime, limit: int, include_media: bool,
                         config_file=None, session_file=None):
    tasks = [fetch_messages(ch, since, limit, include_media, config_file, session_file)
             for ch in channels]
    results = await asyncio.gather(*tasks)
    return list(results)


# ── Channel info ─────────────────────────────────────────────────────────────

async def fetch_info(channel: str, config_file=None, session_file=None):
    api_id, api_hash, session_name = get_config(config_file, session_file)
    async with Client(session_name, api_id=api_id, api_hash=api_hash) as app:
        try:
            chat = await app.get_chat(channel)
            return {
                "id": chat.id,
                "title": chat.title,
                "username": chat.username,
                "description": chat.description,
                "members_count": chat.members_count,
                "link": f"https://t.me/{chat.username}" if chat.username else None,
            }
        except (ChannelInvalid, UsernameNotOccupied) as e:
            return {"error": str(e), "channel": channel}


# ── Auth setup ───────────────────────────────────────────────────────────────

async def setup_auth(config_file=None, session_file=None):
    """Interactive first-time auth — creates session file."""
    api_id, api_hash, session_name = get_config(config_file, session_file)
    print(f"Starting auth for session: {session_name}")
    print("You will receive a code in Telegram. Enter it when prompted.")
    async with Client(session_name, api_id=api_id, api_hash=api_hash, **_DEVICE) as app:
        me = await app.get_me()
        print(json.dumps({"status": "authenticated", "user": me.username or str(me.id)}))


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="tg-reader",
        description="Read Telegram channel posts for OpenClaw agent"
    )
    # Global options (available to all subcommands)
    parser.add_argument("--config-file", default=None,
                        help="Path to config JSON (overrides ~/.tg-reader.json)")
    parser.add_argument("--session-file", default=None,
                        help="Path to session file (overrides default session path)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # fetch
    fetch_p = sub.add_parser("fetch", help="Fetch posts from one or more channels")
    fetch_p.add_argument("channels", nargs="+", help="Channel usernames e.g. @durov")
    fetch_p.add_argument("--since", default="24h", help="Time window: 24h, 7d, 2w, or YYYY-MM-DD")
    fetch_p.add_argument("--limit", type=int, default=100, help="Max posts per channel (default 100)")
    fetch_p.add_argument("--media", action="store_true", help="Include media type info")
    fetch_p.add_argument("--format", choices=["json", "text"], default="json")

    # info
    info_p = sub.add_parser("info", help="Get channel title, description and subscriber count")
    info_p.add_argument("channel", help="Channel username e.g. @durov")

    # auth
    sub.add_parser("auth", help="Authenticate with Telegram (first-time setup)")

    args = parser.parse_args()
    cf = args.config_file
    sf = args.session_file

    if args.cmd == "info":
        result = asyncio.run(fetch_info(args.channel, cf, sf))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "auth":
        asyncio.run(setup_auth(cf, sf))
        return

    if args.cmd == "fetch":
        try:
            since_dt = parse_since(args.since)
        except ValueError as e:
            print(json.dumps({"error": str(e)}))
            sys.exit(1)

        if len(args.channels) == 1:
            result = asyncio.run(fetch_messages(args.channels[0], since_dt, args.limit, args.media, cf, sf))
        else:
            result = asyncio.run(fetch_multiple(args.channels, since_dt, args.limit, args.media, cf, sf))

        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # Human-readable text output
            items = result if isinstance(result, list) else [result]
            for ch_result in items:
                if "error" in ch_result:
                    print(f"[ERROR] {ch_result['channel']}: {ch_result['error']}")
                    continue
                print(f"\n=== {ch_result['channel']} ({ch_result['count']} posts since {args.since}) ===")
                for msg in ch_result["messages"]:
                    print(f"\n[{msg['date']}] {msg['link']}")
                    print(msg["text"][:500] + ("..." if len(msg["text"]) > 500 else ""))


if __name__ == "__main__":
    main()
