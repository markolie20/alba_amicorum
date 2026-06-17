"""
Scrape the correct scan image(s) for every contribution from data.bibliotheken.nl.

Navigation path:
  1. source URL (data.bibliotheken.nl/id/alba/pXXX)
       → find "image" link → blank-node URL
  2. blank-node page (/KB/Production/browser?resource=<blank-node>)
       → find "contentUrl" links → resolver.kb.nl URLs (one per image)
  3. Download each resolver.kb.nl URL directly as JPEG

Images are saved as:
    client/public/images/<album_id>/contributions/<bijdrage_id>_0.jpg
    client/public/images/<album_id>/contributions/<bijdrage_id>_1.jpg
    ...

Run:
    uv run python scrape_contribution_images.py [options]

Options:
    --limit N        Only process N contributions (useful for testing)
    --album-id UUID  Only process contributions belonging to this album
    --no-skip        Re-download even when images already exist (default: skip)
    --delay SECS     Seconds between requests (default: 1.0)
"""

import argparse
import pathlib
import sys
import time
from urllib.parse import parse_qs, urlparse

import psycopg2
import psycopg2.extras
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

IMAGES_DIR = pathlib.Path(__file__).parent / "client" / "public" / "images"
REQUEST_TIMEOUT = 30
BASE_URL = "https://data.bibliotheken.nl"

HEADERS = {
    "User-Agent": "AlbaAmicorumResearch/1.0 (academic project; contact molieman2002@gmail.com)",
    "Accept": "text/html,application/xhtml+xml",
}


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_contributions(album_id: str | None = None, limit: int | None = None):
    conn = psycopg2.connect(dbname="alba")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    where = "WHERE b.url IS NOT NULL AND b.url != ''"
    if album_id:
        where += f" AND b.albumid = %s"
    limit_clause = f"LIMIT {limit}" if limit else ""

    if album_id:
        cur.execute(
            f"SELECT b.bijdrageid, b.albumid, b.url FROM bijdrage_table b {where} ORDER BY b.albumid, b.bijdrageid {limit_clause}",
            (album_id,),
        )
    else:
        cur.execute(
            f"SELECT b.bijdrageid, b.albumid, b.url FROM bijdrage_table b {where} ORDER BY b.albumid, b.bijdrageid {limit_clause}"
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def existing_images(album_id: str, bijdrage_id: str) -> list[pathlib.Path]:
    contrib_dir = IMAGES_DIR / str(album_id) / "contributions"
    if not contrib_dir.exists():
        return []
    return sorted(contrib_dir.glob(f"{bijdrage_id}_*.jpg"))


def save_image(image_bytes: bytes, album_id: str, bijdrage_id: str, index: int) -> pathlib.Path:
    dest = IMAGES_DIR / str(album_id) / "contributions" / f"{bijdrage_id}_{index}.jpg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(image_bytes)
    return dest


# ---------------------------------------------------------------------------
# HTML parsing helpers
# ---------------------------------------------------------------------------

def find_field_links(soup: BeautifulSoup, field_name: str) -> list[str]:
    """
    Return hrefs of all <a rel=nofollow> tags inside the section whose h5 label
    matches field_name. Skips duplicate sections (MUI clones elements).
    """
    seen = set()
    for h5 in soup.find_all("h5"):
        if h5.get_text(strip=True) != field_name:
            continue
        try:
            # DOM: h5 → div[data-mui] → div.flex → section container
            section = h5.parent.parent.parent
        except AttributeError:
            continue
        sid = id(section)
        if sid in seen:
            continue
        seen.add(sid)
        return [a["href"] for a in section.find_all("a", rel="nofollow") if a.get("href")]
    return []


def extract_resource(href: str) -> str | None:
    """Decode the resource= query param from a /KB/Production/browser?resource=... URL."""
    full = href if href.startswith("http") else BASE_URL + href
    params = parse_qs(urlparse(full).query)
    return params.get("resource", [None])[0]


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def scrape_resolver_urls(source_url: str, session: requests.Session) -> list[str]:
    """
    Follow the two-hop navigation and return all resolver.kb.nl image URLs
    for this contribution.

    Raises ValueError with a descriptive message if the page structure is
    not as expected (e.g. the site switched to client-side rendering).
    """
    # Step 1: contribution page → image blank-node link
    resp = session.get(source_url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    image_hrefs = find_field_links(soup, "image")
    if not image_hrefs:
        # Check whether we at least got any _outLink sections so we know the
        # page rendered correctly.
        if not soup.find("h5"):
            raise ValueError(
                "Page returned no <h5> elements — likely client-side rendered. "
                "Try installing playwright/selenium and re-running with --selenium."
            )
        raise ValueError(f"No 'image' section found on {source_url}")

    blank_node_url = extract_resource(image_hrefs[0])
    if not blank_node_url:
        raise ValueError(f"Could not decode blank-node URL from href: {image_hrefs[0]}")

    # Step 2: blank-node page → contentUrl links
    browser_url = f"{BASE_URL}/KB/Production/browser?resource={blank_node_url}"
    resp2 = session.get(browser_url, timeout=REQUEST_TIMEOUT)
    resp2.raise_for_status()
    soup2 = BeautifulSoup(resp2.text, "html.parser")

    content_url_hrefs = find_field_links(soup2, "contentUrl")
    if not content_url_hrefs:
        raise ValueError(
            f"No 'contentUrl' section found on blank-node page: {browser_url}\n"
            f"  (blank-node came from image link on {source_url})"
        )

    resolver_urls = []
    for href in content_url_hrefs:
        resource = extract_resource(href)
        if resource and "resolver.kb.nl" in resource:
            resolver_urls.append(resource)

    if not resolver_urls:
        raise ValueError(
            f"Found contentUrl links but none point to resolver.kb.nl: {content_url_hrefs}"
        )

    return resolver_urls


def download_image(url: str, session: requests.Session) -> bytes:
    """Download image bytes; raises requests.RequestException on failure."""
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    ct = resp.headers.get("content-type", "")
    if "image" not in ct and "jpeg" not in ct and "jpg" not in ct:
        raise ValueError(f"Unexpected content-type '{ct}' for {url}")
    return resp.content


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape contribution images from data.bibliotheken.nl")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--album-id", type=str, default=None)
    parser.add_argument("--no-skip", action="store_true", help="Re-download existing images")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    args = parser.parse_args()

    rows = get_contributions(album_id=args.album_id, limit=args.limit)
    print(f"Found {len(rows)} contributions to process")
    if not rows:
        return

    session = requests.Session()
    session.headers.update(HEADERS)

    ok = skipped = failed = 0

    for i, row in enumerate(rows, 1):
        bijdrage_id = str(row["bijdrageid"])
        album_id = str(row["albumid"])
        source_url = row["url"]

        # Resume: skip if images already exist for this contribution
        if not args.no_skip and existing_images(album_id, bijdrage_id):
            skipped += 1
            continue

        print(f"[{i}/{len(rows)}] {bijdrage_id}")
        print(f"  source: {source_url}")

        try:
            resolver_urls = scrape_resolver_urls(source_url, session)
        except (requests.RequestException, ValueError) as e:
            print(f"  ERROR finding images: {e}")
            failed += 1
            time.sleep(args.delay)
            continue

        print(f"  found {len(resolver_urls)} image(s)")

        contribution_ok = True
        for idx, img_url in enumerate(resolver_urls):
            print(f"  [{idx}] {img_url}")
            try:
                image_bytes = download_image(img_url, session)
                dest = save_image(image_bytes, album_id, bijdrage_id, idx)
                print(f"      saved → {dest.relative_to(pathlib.Path(__file__).parent)}")
            except (requests.RequestException, ValueError) as e:
                print(f"      ERROR downloading: {e}")
                contribution_ok = False

            time.sleep(args.delay)

        if contribution_ok:
            ok += 1
        else:
            failed += 1

    print(f"\nDone — {ok} saved, {skipped} skipped (already existed), {failed} failed")
    if failed:
        print("Re-run the script to retry failed contributions (already saved ones will be skipped).")


if __name__ == "__main__":
    main()
