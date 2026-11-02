import json
import collections

import pandas as pd

df = pd.read_csv("data/maude_raw.csv")
print("Shape:", df.shape)
print()
print("Reports per year:")
print(df["date_received"].astype(str).str[:4].value_counts().sort_index().to_dict())

terms = df["product_problems"].fillna("").str.split("; ").explode()
terms = terms[terms != ""]
print()
print("Distinct problem terms:", terms.nunique())
print(terms.value_counts().head(15).to_string())

n_terms = df["product_problems"].fillna("").apply(
    lambda s: len([x for x in s.split("; ") if x])
)
print()
print("Problem terms per report:")
print(n_terms.value_counts().sort_index().head(6).to_string())

codes = collections.Counter()
for s in df["mdr_text_json"]:
    for code, txt in json.loads(s):
        codes[code] += 1
print()
print("Text types:", codes.most_common())

lens = df["mdr_text_json"].apply(
    lambda s: sum(len(t or "") for _, t in json.loads(s))
)
print()
print("Narrative length (chars):")
print(lens.describe().round(0).to_string())

for i in [10, 2000, 4500]:
    row = df.iloc[i]
    print()
    print("=" * 60)
    print("Device:", row["generic_name"], "|", row["manufacturer"])
    print("Event:", row["event_type"], "| Problems:", row["product_problems"])
    for code, txt in json.loads(row["mdr_text_json"]):
        print("  [" + str(code) + "]", (txt or "")[:350])
