import urllib.request, json, urllib.error
req = urllib.request.Request('http://127.0.0.1:8000/api/chat/', data=json.dumps({'question': 'hello'}).encode(), headers={'Content-Type': 'application/json'})
try:
    print(urllib.request.urlopen(req).read().decode())
except urllib.error.HTTPError as e:
    print(e.read().decode())
