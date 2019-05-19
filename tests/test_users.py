async def test_user_fetch(test_cli_user):
    resp = await test_cli_user.get('/api/v1/users/current')
    assert resp.status == 200
