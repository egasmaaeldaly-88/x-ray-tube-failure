import json
import pandas as pd

df = pd.read_csv("data/maude_raw.csv")

terms = df["product_problems"].fillna("").str.split("; ").explode()
terms = terms[terms != ""]
counts = terms.value_counts()
counts.rename_axis("term").reset_index(name="count").to_csv(
    "data/problem_terms.csv", index=False
)

print("Terms:", len(counts))
for term, c in counts.items():
    print(f"{c:>5}  {term}")


def desc(s):
    return " ".join(
        (t or "") for code, t in json.loads(s)
        if code == "Description of Event or Problem"
    )


d = df["mdr_text_json"].apply(desc)
print()
print("Reports with no description:", int((d.str.strip() == "").sum()))
for w in ["SERVICE", "ENGINEER", "REPLACED", "INVESTIGAT"]:
    share = d.str.upper().str.contains(w).mean()
    print(f"'{w}' appears in description: {share:.3f}")
