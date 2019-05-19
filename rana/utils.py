from sanic import response

def json(data):
    return response.json({'data': data})
