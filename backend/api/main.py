import uuid as _uuid
import os as _os
import pathlib as _pathlib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import get_cursor
from .models import AlbumDetail, AlbumSummary, Contribution, Location

app = FastAPI(title="Alba Amicorum API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Placeholder location names that have no meaningful coordinates.
# These are treated as unknown — lat/lng will be None.
_UNKNOWN_LOCATIONS = {"zonder plaats", "onbekend", "Onbekend"}

# Full lookup for all distinct raw_location values found in location_album_table.
_LOCATION_COUNTRY: dict[str, str] = {
    # Netherlands
    "Alkmaar": "Netherlands",
    "Amersfoort": "Netherlands",
    "Amsterdam": "Netherlands",
    "Baarn": "Netherlands",
    "Breda": "Netherlands",
    "Den Bosch": "Netherlands",
    "Den Haag": "Netherlands",
    "Deventer": "Netherlands",
    "Dordrecht": "Netherlands",
    "Edam": "Netherlands",
    "Ede": "Netherlands",
    "Enkhuizen": "Netherlands",
    "Geertruidenberg": "Netherlands",
    "Gouda": "Netherlands",
    "Groningen": "Netherlands",
    "Grosthuizen": "Netherlands",
    "Haarlem": "Netherlands",
    "Haastrecht": "Netherlands",
    "Harderwijk": "Netherlands",
    "Leeuwarden": "Netherlands",
    "Leiden": "Netherlands",
    "Lith": "Netherlands",
    "Maarssen": "Netherlands",
    "Medemblik": "Netherlands",
    "Meppel": "Netherlands",
    "Middelburg": "Netherlands",
    "Middelharnis": "Netherlands",
    "Mijnsheerenland": "Netherlands",
    "Nederland": "Netherlands",
    "Neerijnen": "Netherlands",
    "Nijmegen": "Netherlands",
    "Olst": "Netherlands",
    "Ouderkerk aan den IJssel": "Netherlands",
    "Overveen": "Netherlands",
    "Rotterdam": "Netherlands",
    "Santpoort": "Netherlands",
    "Schiedam": "Netherlands",
    "Schönauwen": "Netherlands",
    "Sommelsdijk": "Netherlands",
    "Steenwijk": "Netherlands",
    "Tiel": "Netherlands",
    "Utrecht": "Netherlands",
    "Vlissingen": "Netherlands",
    "Wassenaar": "Netherlands",
    "Zeist": "Netherlands",
    "Zierikzee": "Netherlands",
    "Zutphen": "Netherlands",
    "Zwolle": "Netherlands",
    # Germany
    "Augsburg": "Germany",
    "Bad Wimpfen": "Germany",
    "Berlijn": "Germany",
    "Böttingen": "Germany",
    "Bonn": "Germany",
    "Dittmannsdorf": "Germany",
    "Dresden": "Germany",
    "Duisburg": "Germany",
    "Duitsland": "Germany",
    "Erlangen": "Germany",
    "Frankfurt": "Germany",
    "Fraustadt": "Germany",
    "Giessen": "Germany",
    "Gotha": "Germany",
    "Greiffenberg": "Germany",
    "Jamburg": "Germany",
    "Krauschow": "Germany",
    "Krefeld": "Germany",
    "Leipzig": "Germany",
    "Marburg": "Germany",
    "Memmingen": "Germany",
    "Mosbach": "Germany",
    "München": "Germany",
    "Neuenburg": "Germany",
    "Nuremberg": "Germany",
    "Öhringen": "Germany",
    "Prenzlau": "Germany",
    "Schleusingen": "Germany",
    "Schwäbisch Hall": "Germany",
    "Stuttgart": "Germany",
    "Thierhaupten": "Germany",
    "Tübingen": "Germany",
    # Belgium
    "Atrecht": "Belgium",
    "Brussel": "Belgium",
    "Douai": "Belgium",
    # France
    "Angers": "France",
    "Blois": "France",
    "Bourges": "France",
    "Orléans": "France",
    "Parijs": "France",
    "Saumur": "France",
    # Switzerland
    "Genève": "Switzerland",
    "Lausanne": "Switzerland",
    "Neuchâtel": "Switzerland",
    # Poland
    "Chojna": "Poland",
    "Fraustadt": "Poland",
    "Krauschow": "Poland",
    "Sulechów": "Poland",
    # Russia
    "Sint Petersburg": "Russia",
    # Dutch colonies / overseas
    "Batavia": "Dutch East Indies",
    "Curaçao": "Curaçao",
    "Demerary": "Guyana",
    "Essequibo": "Guyana",
    # Other
    "Kaliningrad": "Russia",
    "Bentheim": "Germany",
    # Unknown / placeholders — no country
    "zonder plaats": "Unknown",
    "onbekend": "Unknown",
    "Onbekend": "Unknown",
    "Aan boord van Z.M. Brik Gier": "Unknown",
    "Aan boord van Z.M. Brik Zwaluw": "Unknown",
    "Duivenvoord": "Unknown",
}


def _coords_or_none(
    raw_location: str | None, latitude: float | None, longitude: float | None
) -> tuple[float | None, float | None]:
    """Return None coords for placeholder locations or when geocoding failed."""
    if raw_location in _UNKNOWN_LOCATIONS:
        return None, None
    return latitude, longitude


_LANGUAGE_CODES: dict[str, str] = {
    "dut": "Dutch",
    "eng": "English",
    "fra": "French",
    "ger": "German",
    "ita": "Italian",
    "lat": "Latin",
    "mis": "Uncoded language",
    "mul": "Multiple languages",
    "und": "Undetermined",
}


def _expand_languages(raw: str | None) -> str | None:
    if not raw:
        return None
    return ", ".join(_LANGUAGE_CODES.get(code.strip(), code.strip()) for code in raw.split(","))


def _derive_country(place_name: str | None) -> str:
    if not place_name:
        return "Unknown"
    return _LOCATION_COUNTRY.get(place_name, "Unknown")


_IMAGES_DIR = _pathlib.Path(__file__).parent.parent.parent / "client" / "public" / "images"

def _scan_urls(album_id: str) -> list[str]:
    folder = _IMAGES_DIR / album_id
    if not folder.is_dir():
        return []
    files = sorted(f.name for f in folder.iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png"})
    return [f"/images/{album_id}/{name}" for name in files]


def _contribution_scan_url(album_id: str, page: int | None, total_scans: int, num_pages: int | None) -> str | None:
    """Return the scan URL for a contribution page, handling both single- and double-scan albums.

    Double-scan albums (both recto and verso scanned for each leaf) have ~2× scan files
    relative to their page count. For those, scan = 2 * page + 1 (recto, 2 front-matter
    scans assumed). Single-scan albums use page directly as the scan file number.
    """
    if page is None:
        return None
    folder = _IMAGES_DIR / album_id
    if not folder.is_dir():
        return None

    is_double_scan = num_pages is not None and total_scans >= num_pages * 1.5

    if is_double_scan:
        for offset in (1, -1):
            scan_num = 2 * page + offset
            if 1 <= scan_num <= total_scans:
                candidate = folder / f"page_{scan_num:03d}.jpg"
                if candidate.exists():
                    return f"/images/{album_id}/page_{scan_num:03d}.jpg"

    direct = folder / f"page_{page:03d}.jpg"
    return f"/images/{album_id}/page_{page:03d}.jpg" if direct.exists() else None


@app.get("/api/stats")
def get_stats():
    """Return aggregate stats: total albums, distinct countries, and year span."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM album_table")
        album_count = cur.fetchone()["count"]

        cur.execute("SELECT DISTINCT raw_location FROM location_album_table")
        location_rows = cur.fetchall()
        country_count = len({
            _derive_country(row["raw_location"])
            for row in location_rows
            if _derive_country(row["raw_location"]) != "Unknown"
        })

        cur.execute("""
            SELECT
                MIN(EXTRACT(YEAR FROM datecreated))::int AS min_year,
                MAX(EXTRACT(YEAR FROM datecreated))::int AS max_year
            FROM album_table
            WHERE datecreated IS NOT NULL
        """)
        year_row = cur.fetchone()

    year_span = 0
    if year_row and year_row["min_year"] and year_row["max_year"]:
        year_span = year_row["max_year"] - year_row["min_year"]

    return {"albums": album_count, "countries": country_count, "years": year_span}


@app.get("/api/countries", response_model=list[str])
def list_countries():
    """Return the sorted list of countries present in the album data."""
    query = """
        SELECT DISTINCT la.raw_location
        FROM location_album_table la
    """
    with get_cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    countries = {
        _derive_country(row["raw_location"])
        for row in rows
        if _derive_country(row["raw_location"]) != "Unknown"
    }
    return sorted(countries)


@app.get("/api/albums", response_model=list[AlbumSummary])
def list_albums():
    """Return all albums with their primary geocodable location."""
    query = """
        SELECT DISTINCT ON (a.albumid)
            a.albumid,
            a.name,
            EXTRACT(YEAR FROM a.datecreated)::int AS year,
            aa.name AS owner,
            COALESCE(p.location, la.raw_location) AS place_name,
            la.raw_location,
            p.latitude,
            p.longitude,
            a.numberofpages
        FROM album_table a
        LEFT JOIN album_author_table aa ON aa.albumid = a.albumid
        LEFT JOIN location_album_table la ON la.albumid = a.albumid
        LEFT JOIN place_table p ON p.location = la.raw_location
            AND la.raw_location NOT IN ('zonder plaats', 'onbekend', 'Onbekend')
        ORDER BY a.albumid, p.latitude NULLS LAST
    """
    with get_cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    results = []
    for row in rows:
        lat, lng = _coords_or_none(
            row["raw_location"], row["latitude"], row["longitude"]
        )
        place = row["place_name"] or "Unknown"

        results.append(AlbumSummary(
            id=str(row["albumid"]),
            title=row["name"] or "Untitled",
            owner=row["owner"] or "Unknown",
            year=row["year"] or 0,
            location=Location(name=place, lat=lat, lng=lng),
            country=_derive_country(row["raw_location"]),
        ))

    return results


@app.get("/api/albums/{album_id}", response_model=AlbumDetail)
def get_album(album_id: str):
    """Return a single album with all its contributions and their locations."""
    try:
        _uuid.UUID(album_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Album not found")

    album_query = """
        SELECT DISTINCT ON (a.albumid)
            a.albumid,
            a.name,
            EXTRACT(YEAR FROM a.datecreated)::int AS year,
            aa.name AS owner,
            COALESCE(p.location, la.raw_location) AS place_name,
            la.raw_location,
            p.latitude,
            p.longitude,
            a.numberofpages,
            a.width,
            a.height
        FROM album_table a
        LEFT JOIN album_author_table aa ON aa.albumid = a.albumid
        LEFT JOIN location_album_table la ON la.albumid = a.albumid
        LEFT JOIN place_table p ON p.location = la.raw_location
            AND la.raw_location NOT IN ('zonder plaats', 'onbekend', 'Onbekend')
        WHERE a.albumid = %s
        ORDER BY a.albumid, p.latitude NULLS LAST
    """

    language_query = """
        SELECT string_agg(language, ', ' ORDER BY language) AS languages
        FROM album_language_table
        WHERE albumid = %s
    """

    description_query = """
        SELECT string_agg(description, E'\n\n— — —\n\n' ORDER BY descriptionid) AS description
        FROM description_album_table
        WHERE albumid = %s
    """

    contributions_query = """
        SELECT DISTINCT ON (b.bijdrageid)
            b.bijdrageid,
            b.albumid,
            b.datecreated,
            b.page,
            b.url,
            b.name,
            COALESCE(ba.name, 'Unknown') AS contributor,
            COALESCE(lbj.raw_location, 'Unknown') AS location_name,
            lbj.raw_location,
            p.latitude,
            p.longitude,
            (SELECT string_agg(d.description, E'\n\n' ORDER BY d.descriptionid)
             FROM description_bijdrage_table d
             WHERE d.bijdrageid = b.bijdrageid) AS description
        FROM bijdrage_table b
        LEFT JOIN bijdrage_author_table ba ON ba.bijdrageid = b.bijdrageid
        LEFT JOIN location_bijdrage_table lbj ON lbj.bijdrageid = b.bijdrageid
        LEFT JOIN place_table p ON p.location = lbj.raw_location
            AND lbj.raw_location NOT IN ('zonder plaats', 'onbekend', 'Onbekend')
        WHERE b.albumid = %s
        ORDER BY b.bijdrageid, p.latitude NULLS LAST
    """

    with get_cursor() as cur:
        cur.execute(album_query, (album_id,))
        album_row = cur.fetchone()

        if not album_row:
            raise HTTPException(status_code=404, detail="Album not found")

        cur.execute(language_query, (album_id,))
        lang_row = cur.fetchone()

        cur.execute(description_query, (album_id,))
        desc_row = cur.fetchone()

        cur.execute(contributions_query, (album_id,))
        contribution_rows = cur.fetchall()

    lat, lng = _coords_or_none(
        album_row["raw_location"], album_row["latitude"], album_row["longitude"]
    )
    place = album_row["place_name"] or "Unknown"

    width = album_row["width"]
    height = album_row["height"]
    dimension = f"{width} x {height} mm" if width and height else None

    scans = _scan_urls(album_id)
    total_scans = len(scans)
    num_pages = album_row["numberofpages"]

    contributions = []
    for c in contribution_rows:
        c_lat, c_lng = _coords_or_none(
            c["raw_location"], c["latitude"], c["longitude"]
        )
        page = c["page"]
        scan_url = _contribution_scan_url(album_id, page, total_scans, num_pages)

        # Format date: show full date when month/day are known, otherwise just the year
        d = c["datecreated"]
        if d:
            if d.month == 1 and d.day == 1:
                date_str = str(d.year)
            else:
                date_str = d.strftime("%-d %B %Y")
        else:
            date_str = "Unknown"

        contributions.append(Contribution(
            id=str(c["bijdrageid"]),
            albumId=str(c["albumid"]),
            contributor=c["contributor"],
            date=date_str,
            location=c["location_name"],
            lat=c_lat,
            lng=c_lng,
            pageNumber=page,
            scanUrl=scan_url,
            name=c["name"],
            description=c["description"],
            sourceUrl=c["url"],
        ))

    return AlbumDetail(
        id=str(album_row["albumid"]),
        title=album_row["name"] or "Untitled",
        owner=album_row["owner"] or "Unknown",
        year=album_row["year"] or 0,
        location=Location(name=place, lat=lat, lng=lng),
        country=_derive_country(album_row["raw_location"]),
        description=desc_row["description"] if desc_row else None,
        language=_expand_languages(lang_row["languages"] if lang_row else None),
        pages=album_row["numberofpages"],
        dimension=dimension,
        scans=scans,
        contributions=contributions,
    )
