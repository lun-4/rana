import pytest


@pytest.mark.asyncio
async def test_index_works(test_cli):
    """safety check to see if testing didn't just broke"""
    resp = await test_cli.get("/")
    assert resp.status_code == 200
