import pytest
from app.services.retrieval import retrieve_context
from app.schemas.chat import SourceNode

@pytest.mark.asyncio
async def test_retrieve_context_returns_empty_when_no_data(mocker):
    # Mock database session
    mock_db = mocker.AsyncMock()
    mock_db.execute.return_value.fetchall.return_value = []
    
    # Mock embedding call
    mocker.patch("app.services.retrieval.get_embedding", return_value=[0.1] * 768)
    
    results = await retrieve_context("Growth tactics", mock_db)
    assert isinstance(results, list)
    assert len(results) == 0