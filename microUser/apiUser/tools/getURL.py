import requests
import json

def getJSON(url):
    data = None
    content = None
    try:
        data = requests.get(url)
        content = data.content.decode()
    except:
        return {'error': 'requests'}
    js = None
    try:
        js = json.loads(content)
    except:
        return {'error': 'json parse'}
    return js
