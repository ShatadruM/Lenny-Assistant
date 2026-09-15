import pytest

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_chat_creates_new_session(async_client, mocker):
    # Mock the LLM factory so we don't actually call Ollama during unit tests
    mocker.patch("app.services.agent.LLMFactory.generate_local", return_value="Mocked response")
    mocker.patch("app.services.agent.retrieve_context", return_value=[])

    response = await async_client.post(
        "/api/chat",
        json={"message": "What is product-market fit?", "llm_provider": "local"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["reply"] == "Mocked response"
    assert data["source_nodes"] == []