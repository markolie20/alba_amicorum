import json
import re

with open("http___data.bibliotheken.nl_rise-alba.jsonld", "r", encoding="utf-8") as file:
    data = json.loads(file.readline())
    text = str(data)
    ids = re.findall(r"/alba/([A-Za-z0-9_-]+)", text)
    print(ids)