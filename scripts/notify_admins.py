#!/usr/bin/env python3
"""One-shot announcer for the slash-command transition.

Sends ONE notice per unique guild owner (owners of multiple servers get a
single DM listing all of them). Enumerating every admin-perm user would
require the privileged Guild Members intent, which is not available to this
app, so the owner is the intended recipient.

REST-only (no gateway session), so it is safe to run while the bot service
is connected to the gateway.

Set SEND = True to actually send (False = dry run).

Usage (on the server):
    cd /home/arbaaz/Projects/Fanfiction-Finder
    .venv/bin/python scripts/notify_admins.py
"""
from __future__ import annotations

import os
import time

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]

API = "https://discord.com/api/v10"
HDRS = {
    "Authorization": f"Bot {TOKEN}",
    "User-Agent": "Fanfiction-Finder-Bot (https://github.com/arzkar/Fanfiction-Finder, 1.0)",
}

SEND = True           # True = actually send DMs; False = dry run (print only)
GUILD_LIMIT = None    # set to e.g. 5 to test on the first few guilds first
SLEEP_BETWEEN_SENDS = 1.5  # seconds; keeps us well under rate limits

NOTICE = (
    "**Fanfiction Finder — service notice**\n"
    "Reading message content is temporarily disabled while the bot awaits "
    "Discord's privileged-intent review. Until then:\n"
    "- \u2705 Use `/linkao3`, `/linkfic`, `/help` (slash commands work everywhere)\n"
    "- \u23f8\ufe0f Pasting a fic link no longer auto-embeds\n"
    "- \u23f8\ufe0f `,` prefix commands (`,allow` etc.) are unavailable\n"
    "Slash commands need no setup. Thanks for your patience!\n\n"
    "\u2753 Questions? Join the support server: https://discord.gg/GtVbKraTGa "
    "— or DM <@696707335418282074> directly."
)


def get_all_guilds() -> list[dict]:
    guilds: list[dict] = []
    after = "0"
    while True:
        r = requests.get(
            f"{API}/users/@me/guilds",
            params={"limit": 200, "after": after},
            headers=HDRS,
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        guilds.extend(batch)
        if len(batch) < 200:
            return guilds
        after = batch[-1]["id"]


def main() -> None:
    guilds = get_all_guilds()
    if GUILD_LIMIT:
        guilds = guilds[:GUILD_LIMIT]

    # Dedupe: one DM per unique owner, regardless of how many servers they own.
    owners: dict[str, list[str]] = {}
    skipped_guilds = 0
    for g in guilds:
        r = requests.get(f"{API}/guilds/{g['id']}", headers=HDRS, timeout=30)
        if r.status_code != 200:
            logger.warning(f"[{g['name']}] could not fetch guild ({r.status_code}); skipped")
            skipped_guilds += 1
            continue
        owners.setdefault(str(r.json()["owner_id"]), []).append(g["name"])
        time.sleep(0.25)

    logger.info(
        f"{len(guilds)} guild(s) ({skipped_guilds} unresolvable) -> "
        f"{len(owners)} unique owner(s) to DM; SEND={SEND}"
    )

    sent = failed = 0
    total = len(owners)
    for i, (owner_id, names) in enumerate(sorted(owners.items()), 1):
        # Open (or fetch) a DM channel with the owner.
        r = requests.post(
            f"{API}/users/@me/channels",
            json={"recipient_id": owner_id},
            headers=HDRS,
            timeout=30,
        )
        if r.status_code != 200:
            logger.warning(f"({i}/{total}) owner {owner_id}: could not open DM ({r.status_code}); skipped")
            failed += 1
            continue
        dm_channel_id = r.json()["id"]

        msg = NOTICE
        msg += (
            f"\n\nThis affects your server: **{names[0]}**"
            if len(names) == 1
            else f"\n\nThis affects your servers: **{', '.join(names)}**"
        )

        if not SEND:
            logger.info(f"[DRY RUN] ({i}/{total}) owner {owner_id} <- {len(names)} server(s): {', '.join(names)}")
            time.sleep(0.5)
            continue

        r = requests.post(
            f"{API}/channels/{dm_channel_id}/messages",
            json={"content": msg},
            headers=HDRS,
            timeout=30,
        )
        if r.status_code in (200, 201):
            sent += 1
            logger.info(f"({i}/{total}) owner {owner_id} <- notice ({len(names)} server(s))")
        else:
            failed += 1
            logger.warning(f"({i}/{total}) owner {owner_id}: send failed ({r.status_code}: {r.text[:120]})")

        time.sleep(SLEEP_BETWEEN_SENDS)

    logger.info(f"Done. sent={sent} failed={failed} (SEND={SEND})")


if __name__ == "__main__":
    main()
