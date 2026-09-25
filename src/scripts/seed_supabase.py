"""
One-off (and repeatable) push of data/accounts.json into the Supabase
`accounts` table, which is what main.py actually reads at runtime. Run this
after first creating the table (see README's Supabase section for the SQL)
and again any time accounts.json changes, e.g. after refresh_accounts.py
merges freshly-fetched data.

Usage (from the repo root, with SUPABASE_URL and SUPABASE_SERVICE_KEY set in
.env or the environment):
    python3 src/scripts/seed_supabase.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent
DATA_PATH = BASE_DIR / "data" / "accounts.json"

load_dotenv(REPO_ROOT / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")


def main() -> None:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        sys.exit("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set (in .env or the environment).")
    if not DATA_PATH.exists():
        sys.exit(f"{DATA_PATH} not found — nothing to seed.")

    accounts = json.loads(DATA_PATH.read_text())["accounts"]
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    rows = [{"id": account["id"], "data": account} for account in accounts]
    client.table("accounts").upsert(rows).execute()
    print(f"Upserted {len(rows)} accounts into Supabase.")


if __name__ == "__main__":
    main()
