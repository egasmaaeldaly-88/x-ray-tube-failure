import json
import time
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

BASE = "https://api.fda.gov/device/event.json"
YEARS = range(2016, 2026)
PER_YEAR = 600
OUT = "data/maude_raw.csv"


def fetch(year):
    search = (
        'device.generic_name:"x-ray" AND '
        f"date_received:[{year}0101 TO {year}1231]"
    )
    params = {"search": search, "limit": PER_YEAR}
    url = BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)["results"]
    except urllib.error.HTTPError as e:
        print(year, "HTTP error:", e.code, e.read().decode()[:200])
        return []


rows = []
for year in YEARS:
    recs = fetch(year)
    print(year, "->", len(recs), "reports")
    for rec in recs:
        dev = (rec.get("device") or [{}])[0]
        texts = [
            [t.get("text_type_code"), t.get("text")]
            for t in (rec.get("mdr_text") or [])
        ]
        problems = [p for p in (rec.get("product_problems") or []) if p]
        rows.append({
            "report_number": rec.get("report_number"),
            "event_type": rec.get("event_type"),
            "date_received": rec.get("date_received"),
            "generic_name": dev.get("generic_name"),
            "brand_name": dev.get("brand_name"),
            "manufacturer": dev.get("manufacturer_d_name"),
            "product_problems": "; ".join(dict.fromkeys(problems)),
            "mdr_text_json": json.dumps(texts),
        })
    time.sleep(1)

df = pd.DataFrame(rows).drop_duplicates(subset="report_number")
df.to_csv(OUT, index=False)

print()
print("Saved:", OUT, "shape:", df.shape)
print()
print(df["event_type"].value_counts(dropna=False))
print()
print("Missing product_problems:", (df["product_problems"] == "").mean().round(3))
print("Has text:", (df["mdr_text_json"] != "[]").mean().round(3))
