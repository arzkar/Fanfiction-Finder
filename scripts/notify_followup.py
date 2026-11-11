#!/usr/bin/env python3
"""One-shot follow-up: support-server info for owners already notified.

Companion to notify_admins.py — sends a short one-line PS to every unique
guild owner. Owners whose DMs are closed will simply fail again (harmless).

REST-only. SEND = True by default here (it only ever sends one short line).

Usage (on the server):
    cd /home/arbaaz/Projects/Fanfiction-Finder
    .venv/bin/python scripts/notify_followup.py
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

SEND = True
SLEEP_BETWEEN_SENDS = 1.5

PS = (
    "\ud83d\udc4b Quick PS to the notice you just received: questions about the change? "
    "Join the support server https://discord.gg/GtVbKraTGa "
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
    owners: dict[str, list[str]] = {}
    for g in get_all_guilds():
        r = requests.get(f"{API}/guilds/{g['id']}", headers=HDRS, timeout=30)
        if r.status_code != 200:
            continue
        owners.setdefault(str(r.json()["owner_id"]), []).append(g["name"])
        time.sleep(0.25)

    logger.info(f"{len(owners)} unique owner(s) to follow-up; SEND={SEND}")

    sent = failed = 0
    for i, (owner_id, names) in enumerate(sorted(owners.items()), 1):
        r = requests.post(
            f"{API}/users/@me/channels",
            json={"recipient_id": owner_id},
            headers=HDRS,
            timeout=30,
        )
        if r.status_code != 200:
            logger.warning(f"({i}/{len(owners)}) owner {owner_id}: no DM channel ({r.status_code})")
            failed += 1
            continue

        if not SEND:
            logger.info(f"[DRY RUN] ({i}/{len(owners)}) owner {owner_id} <- PS")
            time.sleep(0.5)
            continue

        r = requests.post(
            f"{API}/channels/{r.json()['id']}/messages",
            json={"content": PS},
            headers=HDRS,
            timeout=30,
        )
        if r.status_code in (200, 201):
            sent += 1
            logger.info(f"({i}/{len(owners)}) owner {owner_id} <- PS")
        else:
            failed += 1
            logger.warning(f"({i}/{len(owners)}) owner {owner_id}: send failed ({r.status_code})")

        time.sleep(SLEEP_BETWEEN_SENDS)

    logger.info(f"Done. sent={sent} failed={failed} (SEND={SEND})")


if __name__ == "__main__":
    main()
