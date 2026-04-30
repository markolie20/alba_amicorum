import json

RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'

with open('data/http___data.bibliotheken.nl_rise-alba.jsonld', encoding='utf-8') as f:
    data = json.loads(f.readline())

graph = data[0]['@graph']

# Map each ID to its schema types
id_types = {}
for entry in graph:
    if RDF_TYPE not in entry:
        continue
    id_ = entry['@id']
    type_ = entry[RDF_TYPE]['@id'].split('schema.org/')[-1]
    id_types.setdefault(id_, set()).add(type_)

albums = [id_ for id_, types in id_types.items() if 'Book' in types]
bijdrages = [id_ for id_, types in id_types.items() if 'Chapter' in types]
other = [id_ for id_, types in id_types.items() if 'Book' not in types and 'Chapter' not in types]

by_type = {}
for id_, types in id_types.items():
    for type_ in types:
        by_type.setdefault(type_, []).append(id_)

for type_, ids in sorted(by_type.items(), key=lambda x: -len(x[1])):
    print(f"{type_}: {len(ids)}")

with open('data/urls_by_type.json', 'w', encoding='utf-8') as f:
    json.dump(by_type, f, ensure_ascii=False, indent=2)

print(f"\nWritten to data/urls_by_type.json")
