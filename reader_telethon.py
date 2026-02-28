#!/usr/bin/env python3
"""
tg-channel-reader — Telegram channel reader skill for OpenClaw
Reads posts from public/private Telegram channels via MTProto (Telethon)
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from telethon import TelegramClient
    from telethon.errors import (
        FloodWaitError,
        ChannelInvalidError,
        ChannelPrivateError,
        ChannelBannedError,
        ChatForbiddenError,
        ChatInvalidError,
        ChatRestrictedError,
        PeerIdInvalidError,
        UsernameNotOccupiedError,
        UserBannedInChannelError,
        InviteHashExpiredError,
        InviteHashInvalidError,
    )
    from telethon.tl.types import Channel
except ImportError:
    print(json.dumps({"error": "telethon not installed. Run: pip install telethon"}))
    sys.exit(1)


def _channel_error(channel: str, error_type: str, message: str, action: str) -> dict:
    """Build a structured channel error dict for the agent."""
    return {
        "error": message,
        "error_type": error_type,
        "channel": channel,
        "action": action,
    }


# ── Session helpers ──────────────────────────────────────────────────────────

def _find_session_files() -> list:
    """Find .session files in home directory and current working directory."""
    found = []
    seen: set = set()
    dirs_checked: set = set()
    for d in [Path.home(), Path.cwd()]:
        d = d.resolve()
        if d in dirs_checked:
            continue
        dirs_checked.add(d)
        for pattern in ["*.session", ".*.session"]:
            for f in d.glob(pattern):
                if f.name.endswith("-journal"):
                    continue
                resolved = f.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                found.append(f)
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


def _validate_session(session_name: str) -> None:
    """Verify the session file exists; exit with a JSON error and hints if not.

    Both Pyrogram and Telethon store sessions as ``{name}.session``.
    This check prevents a silent re-auth prompt when the file is missing.
    """
    session_file = Path(f"{session_name}.session")
    if session_file.exists():
        return

    found = _find_session_files()
    error: dict = {
        "error": f"Session file not found: {session_file}",
        "expected_path": str(session_file),
        "fix": [
            "Run 'tg-reader-telethon auth' to create a new session",
            "Or set TG_SESSION=/path/to/existing-session (without .session suffix)",
            "Or add {\"session\": \"/path/to/session\"} to ~/.tg-reader.json",
            "Or pass --session-file /path/to/session (without .session suffix)",
        ],
    }
    if found:
        error["found_sessions"] = [str(f) for f in found[:10]]
        suggestion = str(found[0]).removesuffix(".session")
        error["suggestion"] = f"Likely fix: use --session-file {suggestion}"

    print(json.dumps(error, indent=2))
    sys.exit(1)


# ── Config ──────────────────────────────────────────────────────────────────

def get_config(config_file=None, session_file=None):
    """Load credentials from env or config file (env takes priority).

    Args:
        config_file: Explicit path to config JSON (overrides ~/.tg-reader.json)
        session_file: Explicit path to session file (overrides default and config value)
    """
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    session_name = os.environ.get("TG_SESSION", str(Path.home() / ".telethon-reader"))

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

    # Normalize: strip .session suffix if user passed full filename
    if session_name.endswith(".session"):
        session_name = session_name[: -len(".session")]

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


async def fetch_messages(client: TelegramClient, channel: str, since: datetime, limit: int, include_media: bool):
    """Fetch messages from a single channel."""
    messages = []
    
    try:
        # Get the channel entity
        entity = await client.get_entity(channel)
        
        # Ensure it's a channel
        if not isinstance(entity, Channel):
            return {"error": f"'{channel}' is not a channel", "channel": channel}
        
        # Fetch messages
        async for msg in client.iter_messages(entity, limit=limit):
            # Check if message is older than 'since'
            msg_date = msg.date.replace(tzinfo=timezone.utc)
            if msg_date < since:
                break
            
            # Extract message data
            entry = {
                "id": msg.id,
                "date": msg_date.isoformat(),
                "text": msg.message or "",
                "views": msg.views or 0,
                "forwards": msg.forwards or 0,
                "link": f"https://t.me/{channel.lstrip('@')}/{msg.id}",
            }
            
            if include_media and msg.media:
                entry["media_type"] = type(msg.media).__name__
            
            messages.append(entry)
            
    except (ChannelPrivateError, ChatForbiddenError, ChatRestrictedError) as e:
        return _channel_error(
            channel, "access_denied",
            f"Channel is private or access denied: {e}",
            "remove_from_list_or_rejoin",
        )
    except (ChannelBannedError, UserBannedInChannelError) as e:
        return _channel_error(
            channel, "banned",
            f"Banned from channel: {e}",
            "remove_from_list",
        )
    except (ChannelInvalidError, ChatInvalidError, PeerIdInvalidError,
            UsernameNotOccupiedError, ValueError) as e:
        return _channel_error(
            channel, "not_found",
            f"Channel not found or username is incorrect: {e}",
            "check_username",
        )
    except (InviteHashExpiredError, InviteHashInvalidError) as e:
        return _channel_error(
            channel, "invite_expired",
            f"Invite link expired or invalid: {e}",
            "request_new_invite",
        )
    except FloodWaitError as e:
        return _channel_error(
            channel, "flood_wait",
            f"Rate limited: retry after {e.seconds}s",
            f"wait_{e.seconds}s",
        )
    except Exception as e:
        return _channel_error(
            channel, "unexpected",
            f"Unexpected error: {e}",
            "report_to_user",
        )

    return {
        "channel": channel,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "since": since.isoformat(),
        "count": len(messages),
        "messages": messages,
    }


_FLOOD_WAIT_MAX = 60  # auto-retry only if wait is <= this many seconds


async def fetch_multiple(channels: list, since: datetime, limit: int, include_media: bool,
                         config_file=None, session_file=None, delay: float = 10):
    """Fetch messages from multiple channels sequentially with delays.

    Channels are fetched one at a time to avoid Telegram FloodWait.
    If a FloodWait <= 60s is hit, the request is retried once automatically.
    """
    api_id, api_hash, session_name = get_config(config_file, session_file)
    _validate_session(session_name)

    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        print(json.dumps({"error": "Not authorized. Please run: tg-reader-telethon auth"}))
        await client.disconnect()
        sys.exit(1)

    results = []
    try:
        for i, channel in enumerate(channels):
            result = await fetch_messages(client, channel, since, limit, include_media)

            # Auto-retry on FloodWait if wait is reasonable
            if (isinstance(result, dict) and result.get("error_type") == "flood_wait"):
                wait_action = result.get("action", "")
                try:
                    wait_seconds = int(wait_action.replace("wait_", "").replace("s", ""))
                except (ValueError, AttributeError):
                    wait_seconds = 0
                if 0 < wait_seconds <= _FLOOD_WAIT_MAX:
                    await asyncio.sleep(wait_seconds)
                    result = await fetch_messages(client, channel, since, limit, include_media)

            results.append(result)

            # Delay between channels (skip after the last one)
            if i < len(channels) - 1:
                await asyncio.sleep(delay)
    finally:
        await client.disconnect()

    return results


async def fetch_single(channel: str, since: datetime, limit: int, include_media: bool,
                       config_file=None, session_file=None):
    """Fetch messages from a single channel."""
    api_id, api_hash, session_name = get_config(config_file, session_file)
    _validate_session(session_name)

    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    
    if not await client.is_user_authorized():
        print(json.dumps({"error": "Not authorized. Please run: tg-reader-telethon auth"}))
        await client.disconnect()
        sys.exit(1)
    
    try:
        return await fetch_messages(client, channel, since, limit, include_media)
    finally:
        await client.disconnect()


# ── Auth setup ───────────────────────────────────────────────────────────────

async def setup_auth(config_file=None, session_file=None):
    """Interactive first-time auth — creates session file."""
    api_id, api_hash, session_name = get_config(config_file, session_file)
    print(f"Starting auth for session: {session_name}.session")
    print("You will receive a code in Telegram. Enter it when prompted.\n")
    
    client = TelegramClient(session_name, api_id, api_hash)
    
    # Use lambda to make phone input interactive
    await client.start(phone=lambda: input("Enter phone number (with country code, e.g. +79991234567): "))
    
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n✅ Authenticated as: {me.phone} ({me.first_name})")
        print(json.dumps({
            "status": "authenticated",
            "user": me.username or str(me.id),
            "phone": me.phone,
            "session_file": f"{session_name}.session"
        }))
    else:
        print(json.dumps({"error": "Authentication failed"}))
        sys.exit(1)
    
    await client.disconnect()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="tg-reader-telethon",
        description="Read Telegram channel posts for OpenClaw agent (Telethon version)"
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
    fetch_p.add_argument("--delay", type=float, default=10,
                        help="Seconds to wait between channels (default 10)")
    fetch_p.add_argument("--format", choices=["json", "text"], default="json")

    # auth
    sub.add_parser("auth", help="Authenticate with Telegram (first-time setup)")

    args = parser.parse_args()
    cf = args.config_file
    sf = args.session_file

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
            result = asyncio.run(fetch_single(args.channels[0], since_dt, args.limit, args.media, cf, sf))
        else:
            result = asyncio.run(fetch_multiple(args.channels, since_dt, args.limit, args.media, cf, sf,
                                                delay=args.delay))

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