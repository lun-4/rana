import pytest


@pytest.mark.asyncio
async def test_user_fetch(test_cli_user):
    resp = await test_cli_user.get("/api/v1/users/current")
    assert resp.status_code == 200
    rjson = await resp.json
    assert isinstance(rjson, dict)

    data = rjson["data"]
    assert isinstance(data, dict)
    assert isinstance(data["id"], str)
    assert isinstance(data["username"], str)
    assert isinstance(data["email"], str)
