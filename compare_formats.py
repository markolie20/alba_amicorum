import json
import re
from collections import defaultdict

RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
ALBA_PATTERN = re.compile(r'http://data\.bibliotheken\.nl/id/alba/')

# ── N-Triples parser (works for .nt and .ttl since both use N-Triples syntax) ──

def parse_ntriples(path):
    """Extract {subject: {types}} from an N-Triples file for alba subjects only."""
    type_triple = f'<{RDF_TYPE}>'
    id_types = defaultdict(set)
    with open(path, encoding='utf-8') as f:
        for line in f:
            if type_triple not in line or not ALBA_PATTERN.search(line):
                continue
            # <subject> <rdf:type> <object> .
            m = re.match(r'<([^>]+)>\s+<[^>]+>\s+<([^>]+)>', line)
            if m:
                subject, obj = m.group(1), m.group(2)
                type_label = obj.split('/')[-1].split('#')[-1]
                id_types[subject].add(type_label)
    return id_types

# ── TriG parser (named graphs, same triple syntax inside graph blocks) ──

def parse_trig(path):
    """Extract {subject: {types}} from a TriG file for alba subjects only."""
    type_triple = f'<{RDF_TYPE}>'
    id_types = defaultdict(set)
    with open(path, encoding='utf-8') as f:
        for line in f:
            if type_triple not in line or not ALBA_PATTERN.search(line):
                continue
            m = re.match(r'<([^>]+)>\s+<[^>]+>\s+<([^>]+)>', line)
            if m:
                subject, obj = m.group(1), m.group(2)
                type_label = obj.split('/')[-1].split('#')[-1]
                id_types[subject].add(type_label)
    return id_types

# ── JSONLD parser ──

def parse_jsonld(path):
    with open(path, encoding='utf-8') as f:
        data = json.loads(f.readline())
    graph = data[0]['@graph']
    id_types = defaultdict(set)
    for entry in graph:
        if RDF_TYPE not in entry or not ALBA_PATTERN.search(entry.get('@id', '')):
            continue
        subject = entry['@id']
        type_label = entry[RDF_TYPE]['@id'].split('/')[-1].split('#')[-1]
        id_types[subject].add(type_label)
    return id_types

# ── Run ──

files = {
    'jsonld': ('data/http___data.bibliotheken.nl_rise-alba.jsonld', parse_jsonld),
    'nt':     ('data/http___data.bibliotheken.nl_rise-alba.nt',     parse_ntriples),
    'ttl':    ('data/http___data.bibliotheken.nl_rise-alba.ttl',    parse_ntriples),
    'trig':   ('data/https___data.bibliotheken.nl_nta.trig',        parse_trig),
}

results = {}
for fmt, (path, parser) in files.items():
    print(f"Parsing {fmt}...")
    id_types = parser(path)
    by_type = defaultdict(set)
    for id_, types in id_types.items():
        for t in types:
            by_type[t].add(id_)
    results[fmt] = {t: sorted(ids) for t, ids in by_type.items()}
    print(f"  {fmt}: " + ", ".join(f"{t}={len(ids)}" for t, ids in sorted(by_type.items())))

print()

# Compare Book counts across formats
print("── Book (album) counts ──")
for fmt, by_type in results.items():
    print(f"  {fmt}: {len(by_type.get('Book', []))}")

print()
print("── Chapter (bijdrage) counts ──")
for fmt, by_type in results.items():
    print(f"  {fmt}: {len(by_type.get('Chapter', []))}")

# Check if any format has Books the jsonld is missing
jsonld_books = set(results['jsonld'].get('Book', []))
for fmt in ('nt', 'ttl', 'trig'):
    fmt_books = set(results[fmt].get('Book', []))
    only_in_fmt = fmt_books - jsonld_books
    only_in_jsonld = jsonld_books - fmt_books
    if only_in_fmt or only_in_jsonld:
        print(f"\n── jsonld vs {fmt} (Book) ──")
        print(f"  Only in {fmt}: {len(only_in_fmt)}")
        print(f"  Only in jsonld: {len(only_in_jsonld)}")

with open('data/compare_formats.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nWritten to data/compare_formats.json")
