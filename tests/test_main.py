import httpx
import pytest

from app.config import Settings
from app.dashboard import DashboardClient
from app.main import ChatContext, ChatRequest, IntelligenceService


class FakeResponses:
    async def create(self, **kwargs):
        assert kwargs["model"] == "test-model"
        assert "Player One" in kwargs["input"]
        return type("Response", (), {"output_text": "Player One is producing efficiently."})()


class FakeOpenAI:
    responses = FakeResponses()


@pytest.mark.asyncio
async def test_player_answer_uses_dashboard_context():
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"name": "Player One", "points": 50}))
    async with httpx.AsyncClient(base_url="https://dashboard.test", transport=transport) as client:
        service = IntelligenceService(
            Settings("https://dashboard.test", "test-key", "test-model", ["http://localhost:5173"]),
            dashboard=DashboardClient("https://dashboard.test", client), openai_client=FakeOpenAI(),
        )
        result = await service.answer(ChatRequest(message="How is he doing?", context=ChatContext(page="player", player_id=7)))
    assert result.answer == "Player One is producing efficiently."
    assert result.evidence[0].endpoint == "/players/7"


def test_player_context_requires_player_id():
    with pytest.raises(ValueError):
        ChatContext(page="player")
