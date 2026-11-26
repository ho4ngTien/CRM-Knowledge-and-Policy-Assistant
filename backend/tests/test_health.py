import pytest

from src.config import settings


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["timezone"] == "Asia/Ho_Chi_Minh"
    assert payload["streaming_enabled"] is False
    assert payload["mounted_modules"] == 13


@pytest.mark.asyncio
async def test_selection_health_is_mounted_at_api_selection_path(client):
    response = await client.get("/api/v1/selection/health")
    assert response.status_code == 200
    assert response.json()["module"] == "selection"


def test_sec06_environment_and_llm_contract_bounds():
    assert settings.APP_ENV in {"development", "test"}
    assert settings.APP_TIMEZONE == "Asia/Ho_Chi_Minh"
    assert settings.ENABLE_ANSWER_STREAMING is False
    assert settings.LLM_MAX_INPUT_TOKENS == 6000
    assert settings.LLM_MAX_OUTPUT_TOKENS == 900
    assert settings.LLM_MAX_CALLS_PER_PACKAGE == 2
    assert settings.LLM_MAX_CALLS_PER_MONTH == 2000

