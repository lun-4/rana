async def test_user_fetch(test_cli_user):
    resp = await test_cli_user.get('/api/v1/users/current')
    assert resp.status == 200
    rjson = await resp.json()

    assert isinstance(rjson, dict)
    assert isinstance(rjson['id'], str)
    assert isinstance(rjson['username'], str)
    assert isinstance(rjson['email'], str)
