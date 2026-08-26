"""
scripts/simulate_thrashing.py — Gate 21 verification script

Simulates rapid topic-advancement thrashing for a single test student by
hitting POST /tutor/interact repeatedly in a short window.

Usage:
    python scripts/simulate_thrashing.py \\
        --base-url http://localhost:8000 \\
        --email student@example.com \\
        --password yourpassword \\
        [--count 5] \\
        [--delay 0.5]

After running, check:
    GET /monitoring/alerts  (with instructor credentials)

The anomaly alert should show alert_type='thrashing' for the student.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx


async def login(client: httpx.AsyncClient, base_url: str, email: str, password: str) -> str:
    resp = await client.post(
        f"{base_url}/auth/login",
        json={"email": email, "password": password},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


async def simulate(
    base_url: str,
    email: str,
    password: str,
    count: int,
    delay: float,
) -> None:
    print(f"[simulate_thrashing] Logging in as {email}...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        token = await login(client, base_url, email, password)
        print(f"[simulate_thrashing] Got token. Firing {count} activity requests...")

        results = []
        for i in range(count):
            resp = await client.post(
                f"{base_url}/tutor/interact",
                json={"message": "next"},
                headers={"Authorization": f"Bearer {token}"},
            )
            data = resp.json() if resp.status_code == 200 else {"error": resp.text}
            auto_applied = data.get("auto_applied", False)
            risk_tier = data.get("risk_tier", "?")
            print(
                f"  [{i+1}/{count}] status={resp.status_code} "
                f"auto_applied={auto_applied} risk_tier={risk_tier}"
            )
            results.append(data)
            if i < count - 1:
                await asyncio.sleep(delay)

        auto_count = sum(1 for r in results if r.get("auto_applied"))
        print(f"\n[simulate_thrashing] Done. {auto_count}/{count} requests auto-applied.")
        print(
            f"[simulate_thrashing] Check GET {base_url}/monitoring/alerts "
            f"(with instructor credentials) for a 'thrashing' alert."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate topic-advancement thrashing for Gate 21")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--email", required=True, help="Student account email")
    parser.add_argument("--password", required=True, help="Student account password")
    parser.add_argument("--count", type=int, default=5, help="Number of requests to fire (default 5)")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between requests (default 0.5)")
    args = parser.parse_args()

    asyncio.run(simulate(args.base_url, args.email, args.password, args.count, args.delay))


if __name__ == "__main__":
    main()
