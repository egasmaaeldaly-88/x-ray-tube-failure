import json
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

BASE = "https://api.fda.gov/device/event.json"
SEARCH = 'device.generic_name:"x-ray"'


def call(**params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print("HTTP error:", e.code, e.read().decode()[:300])
        raise SystemExit(1)


# 1) How many reports per event type?
counts = call(search=SEARCH, count="event_type.exact")
print("Reports per event type:")
for item in counts["results"]:
    print("  ", item["term"], item["count"])

# 2) Sample of full reports
data = call(search=SEARCH, limit=100)
rows = []
for rec in data["results"]:
    dev = (rec.get("device") or [{}])[0]
    texts = [t.get("text") or "" for t in rec.get("mdr_text", [])]
    rows.append({
        "event_type": rec.get("event_type"),
        "date_received": rec.get("date_received"),
        "generic_name": dev.get("generic_name"),
        "manufacturer": dev.get("manufacturer_d_name"),
        "product_problems": "; ".join(p for p in (rec.get("product_problems") or []) if p),
        "narrative": " ".join(texts),
    })

df = pd.DataFrame(rows)
df.to_csv("data/maude_sample.csv", index=False)

print()
print("Shape:", df.shape)
print(df[["event_type", "generic_name", "product_problems"]].head(10).to_string())
print()
print("Example narrative:")
print(df["narrative"].iloc[0][:400])
