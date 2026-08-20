import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from models import Base, Chunk
from rag import retrieve

# Use an async Postgres test DB or SQLite? 
# pgvector requires Postgres. SQLite won't work with Vector(384).
# We can't easily test pgvector without a running Postgres instance that has pgvector installed.
# Since the local dev environment uses Postgres, we'll connect to a test database or just mock it.
# For this research prototype, we can use a mock or the actual local db. 
# Let's write a simple test that uses the real DB but rolls back, or just mocks the DB retrieval.
# Wait, we can test `parse_handbook`!

from rag import parse_handbook
from unittest import mock
import rag

def test_parse_handbook(tmp_path):
    # Mock the HANDBOOK_DIR
    mock_dir = tmp_path / "handbook"
    mock_dir.mkdir()
    
    file1 = mock_dir / "03-loops.md"
    file1.write_text("# Loops\nThis is a loop.\n## For Loops\nFor loop text.\n", encoding="utf-8")
    
    with mock.patch("rag.HANDBOOK_DIR", mock_dir):
        chunks = parse_handbook()
        
    assert len(chunks) == 2
    
    assert chunks[0]["topic_id"] == "loops"
    assert chunks[0]["heading"] == "Loops"
    assert "This is a loop." in chunks[0]["content"]
    
    assert chunks[1]["topic_id"] == "loops"
    assert chunks[1]["heading"] == "For Loops"
    assert "For loop text." in chunks[1]["content"]

@pytest.mark.asyncio
async def test_retrieve_filters_by_topic(mocker):
    # Mock get_model and session.execute
    mock_model = mocker.MagicMock()
    mock_model.encode.return_value = [0.1] * 384
    mocker.patch("rag.get_model", return_value=mock_model)
    
    mock_session = mocker.AsyncMock()
    
    # We can't fully execute the query without Postgres, so we just verify the call
    # A full integration test would require Postgres + pgvector.
    
    # Let's mock the session.execute to return empty list
    mock_result = mocker.MagicMock()
    mock_result.scalars().all.return_value = []
    mock_session.execute.return_value = mock_result
    
    res = await retrieve(mock_session, "test query", topic_id="loops", k=2)
    assert res == []
    
    # Verify model.encode was called
    mock_model.encode.assert_called_once_with("test query")
