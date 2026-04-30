import json
import psycopg2
import psycopg2.extras
import re
from uuid import uuid4

psycopg2.extras.register_uuid()

# --- Test connection before doing any work ---
try:
    conn = psycopg2.connect(dbname='alba')
    conn.close()
    print("Database connection OK.")
except Exception as e:
    raise SystemExit(f"Cannot connect to database: {e}")

# --- Helpers ---


def get_section(sections, title):
    for s in sections:
        if s['title'] == title:
            return s['values']
    return []

def get_first(sections, title):
    vals = get_section(sections, title)
    return vals[0] if vals else None

DUTCH_MONTHS = {
    'januari': 1, 'februari': 2, 'maart': 3, 'april': 4,
    'mei': 5, 'juni': 6, 'juli': 7, 'augustus': 8,
    'september': 9, 'oktober': 10, 'november': 11, 'december': 12
}

def parse_date(value):
    if not value:
        return None
    # "13 juli 1842"
    m = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', value)
    if m:
        day, month_name, year = m.groups()
        month = DUTCH_MONTHS.get(month_name.lower())
        if month:
            return f"{year}-{month:02d}-{max(int(day), 1):02d}"
    # "1842/1917" or "1842"
    m = re.match(r'^(\d{4})', value.strip())
    if m:
        return f"{m.group(1)}-01-01"
    return None

def parse_int_prefix(value):
    """Parse leading integer from strings like '317 mm' or '133 fol'"""
    if value:
        m = re.match(r'(\d+)', value)
        if m:
            return int(m.group(1))
    return None

# --- Load data ---

with open('data/scraped.jsonl', encoding='utf-8') as f:
    raw = [json.loads(line) for line in f]

# Deduplicate by URL
seen = set()
data = []
for entry in raw:
    if entry['url'] not in seen:
        seen.add(entry['url'])
        data.append(entry)

# Separate albums (Book) and bijdrages (Chapter) by type
albums = []
bijdrages = []
for entry in data:
    types = get_section(entry['sections'], 'type')
    if 'Chapter' in types:
        bijdrages.append(entry)
    else:
        albums.append(entry)

# Pre-assign a UUID to every entry, keyed by URL
url_to_uuid = {entry['url']: uuid4() for entry in data}

BASE = 'http://data.bibliotheken.nl/id/alba/'

# Build bijdrage_url -> album_uuid mapping from hasPart
bijdrage_to_album = {}
for album in albums:
    album_uuid = url_to_uuid[album['url']]
    for part_id in get_section(album['sections'], 'hasPart'):
        bijdrage_url = BASE + part_id
        bijdrage_to_album[bijdrage_url] = album_uuid

# --- Insert ---

conn = psycopg2.connect(dbname='alba')
cur = conn.cursor()

for album in albums:
    sec = album['sections']
    album_uuid = url_to_uuid[album['url']]
    identifiers = get_section(sec, 'identifier')
    date_vals = get_section(sec, 'dateCreated')

    cur.execute("""
        INSERT INTO album_table
            (albumId, url, name, dateCreated, width, height, funder, identifier1, identifier2, identifier3, numberOfPages)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (albumId) DO NOTHING
    """, (
        album_uuid,
        album['url'],
        get_first(sec, 'name'),
        parse_date(date_vals[0]) if date_vals else None,
        parse_int_prefix(get_first(sec, 'width')),
        parse_int_prefix(get_first(sec, 'height')),
        get_first(sec, 'funder'),
        identifiers[0] if len(identifiers) > 0 else None,
        identifiers[1] if len(identifiers) > 1 else None,
        identifiers[2] if len(identifiers) > 2 else None,
        parse_int_prefix(get_first(sec, 'numberOfPages')),
    ))

    for author in get_section(sec, 'author'):
        cur.execute(
            "INSERT INTO album_author_table (authorId, albumId, name) VALUES (%s, %s, %s)",
            (uuid4(), album_uuid, author)
        )

    for desc in get_section(sec, 'description'):
        cur.execute(
            "INSERT INTO description_album_table (descriptionId, albumId, description) VALUES (%s, %s, %s)",
            (uuid4(), album_uuid, desc[:255])
        )

    for loc in get_section(sec, 'locationCreated'):
        cur.execute(
            "INSERT INTO location_album_table (locationId, albumId, location) VALUES (%s, %s, %s)",
            (uuid4(), album_uuid, loc[:255])
        )

    for lang in get_section(sec, 'inLanguage'):
        cur.execute(
            "INSERT INTO album_language_table (languageId, albumId, language) VALUES (%s, %s, %s)",
            (uuid4(), album_uuid, lang[:255])
        )

    for mat in get_section(sec, 'material'):
        cur.execute(
            "INSERT INTO album_material_table (materialId, albumId, material) VALUES (%s, %s, %s)",
            (uuid4(), album_uuid, mat[:255])
        )

for bijd in bijdrages:
    sec = bijd['sections']
    bijd_uuid = url_to_uuid[bijd['url']]
    album_uuid = bijdrage_to_album.get(bijd['url'])
    date_vals = get_section(sec, 'dateCreated')

    pagination = get_first(sec, 'pagination')
    page = None
    if pagination:
        m = re.search(r'(\d+)', pagination)
        if m:
            page = int(m.group(1))

    position_str = get_first(sec, 'position')
    position = int(position_str) if position_str and position_str.lstrip('-').isdigit() else None

    cur.execute("""
        INSERT INTO bijdrage_table (bijdrageId, albumId, url, dateCreated, name, page, position)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (bijdrageId) DO NOTHING
    """, (
        bijd_uuid,
        album_uuid,
        bijd['url'],
        parse_date(date_vals[0]) if date_vals else None,
        get_first(sec, 'name'),
        page,
        position,
    ))

    for author in get_section(sec, 'author'):
        cur.execute(
            "INSERT INTO bijdrage_author_table (authorId, bijdrageId, name) VALUES (%s, %s, %s)",
            (uuid4(), bijd_uuid, author)
        )

    for desc in get_section(sec, 'description'):
        cur.execute(
            "INSERT INTO description_bijdrage_table (descriptionId, bijdrageId, description) VALUES (%s, %s, %s)",
            (uuid4(), bijd_uuid, desc[:255])
        )

    for loc in get_section(sec, 'locationCreated'):
        cur.execute(
            "INSERT INTO location_bijdrage_table (locationId, bijdrageId, location) VALUES (%s, %s, %s)",
            (uuid4(), bijd_uuid, loc[:255])
        )

conn.commit()
cur.close()
conn.close()
print(f"Inserted {len(albums)} albums and {len(bijdrages)} bijdrages.")
