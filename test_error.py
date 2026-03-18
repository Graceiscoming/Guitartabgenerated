import json
import urllib.request
import traceback

data = {
    "notes": ["C", "D", "E"],
    "min_fret": 0,
    "max_fret": 5,
    "allowed_strings": [1,2,3,4,5,6]
}
try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/tab/generate",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    res = urllib.request.urlopen(req)
    print("SUCCESS")
    print(res.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode())
except Exception as e:
    traceback.print_exc()
