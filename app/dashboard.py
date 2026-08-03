"""A narrow, read-only client for the NHL dashboard public API."""

from dataclasses import dataclass
from typing import Any

import httpx


class DashboardUnavailable(Exception):
    """The dashboard could not provide the requested context."""


@dataclass
class ContextBundle:
    facts: dict[str, Any]
    evidence: list[dict[str, str]]


class DashboardClient:
    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.client = client

    async def _get(self, path: str) -> Any:
        try:
            if self.client:
                response = await self.client.get(path)
            else:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
                    response = await client.get(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise DashboardUnavailable("The NHL dashboard data is temporarily unavailable.") from exc

    async def player_context(self, player_id: int) -> ContextBundle:
        player = await self._get(f"/players/{player_id}")
        return ContextBundle(
            facts={"player": player},
            evidence=[{"label": "Player profile and season statistics", "endpoint": f"/players/{player_id}"}],
        )

    async def team_context(self, team_abbrev: str) -> ContextBundle:
        abbrev = team_abbrev.upper()
        standings = await self._get("/standings/latest")
        roster = await self._get(f"/teams/{abbrev}/roster")
        playoff_odds = await self._get("/playoff-odds")
        return ContextBundle(
            facts={
                "team_abbrev": abbrev,
                "standing": next((row for row in standings if row.get("team_abbrev") == abbrev), None),
                "roster": roster,
                "playoff_odds": next((row for row in playoff_odds if row.get("team_abbrev") == abbrev), None),
            },
            evidence=[
                {"label": "Current standings", "endpoint": "/standings/latest"},
                {"label": "Current roster and season totals", "endpoint": f"/teams/{abbrev}/roster"},
                {"label": "Playoff simulation", "endpoint": "/playoff-odds"},
            ],
        )

    async def league_context(self) -> ContextBundle:
        return ContextBundle(
            facts={
                "standings": await self._get("/standings/latest"),
                "player_leaders": await self._get("/players/leaders"),
                "playoff_odds": await self._get("/playoff-odds"),
            },
            evidence=[
                {"label": "Current standings", "endpoint": "/standings/latest"},
                {"label": "Player leaderboard", "endpoint": "/players/leaders"},
                {"label": "Playoff simulation", "endpoint": "/playoff-odds"},
            ],
        )
