import json

with open("product_warehouse.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned = []

import re

def clean_string(s):
    if isinstance(s, str):
        return re.sub(r'[^\x20-\x7E]', '', s)
    return s

for doc in data:
    new_doc = {}

    for field in dict(doc).keys():
        if field in ("_id","id"):
            new_doc[field] = clean_string(doc[field])
        else:
            new_doc[field] = doc[field]

    cleaned.append(new_doc)

with open("product_warehouse_clean2.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2, ensure_ascii=False)
