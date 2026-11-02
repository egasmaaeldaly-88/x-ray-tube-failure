import json
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.fda.gov/device/event.json"
SEARCH = 'device.generic_name:"x-ray"'


def top(field, n=25):
    params = {"search": SEARCH, "count": field, "limit": n}
    url = BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)["results"]
    except urllib.error.HTTPError as e:
        print("HTTP error on", field, e.code, e.read().decode()[:200])
        return []


print("Top product problems:")
for it in top("product_problems.exact", 30):
    print(f"  {it['count']:>8}  {it['term']}")

print()
print("Top device names:")
for it in top("device.generic_name.exact", 20):
    print(f"  {it['count']:>8}  {it['term']}")
