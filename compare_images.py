"""
Compare old bulk-scan images vs newly scraped per-contribution images.

For each album and contribution reports:
  - only_old     : has old page-heuristic image, no scraped image yet
  - only_new     : has scraped image(s), no old match found
  - both_same    : has both; perceptual hash difference ≤ threshold (looks same)
  - both_differ  : has both; images look visually different
  - neither      : no image at all

Run:
    uv run python compare_images.py [--album-id UUID] [--verbose] [--threshold N]

Options:
    --album-id UUID    Only compare one album
    --verbose          Print per-contribution detail (default: album summaries only)
    --threshold N      Max perceptual hash distance to count as "same" (default: 10)
    --no-hash          Skip visual comparison (faster, just checks existence)
"""

import argparse
import pathlib

import imagehash
import psycopg2
import psycopg2.extras
from PIL import Image

IMAGES_DIR = pathlib.Path(__file__).parent / "client" / "public" / "images"

# ── same heuristic as the backend ──────────────────────────────────────────

def old_image_path(album_id: str, page: int | None, total_scans: int, num_pages: int | None) -> pathlib.Path | None:
    if page is None:
        return None
    folder = IMAGES_DIR / album_id
    if not folder.is_dir():
        return None
    is_double = num_pages is not None and total_scans >= num_pages * 1.5
    if is_double:
        for offset in (1, -1):
            n = 2 * page + offset
            if 1 <= n <= total_scans:
                p = folder / f"page_{n:03d}.jpg"
                if p.exists():
                    return p
    direct = folder / f"page_{page:03d}.jpg"
    return direct if direct.exists() else None


def new_image_paths(album_id: str, bijdrage_id: str) -> list[pathlib.Path]:
    d = IMAGES_DIR / album_id / "contributions"
    if not d.is_dir():
        return []
    return sorted(d.glob(f"{bijdrage_id}_*.jpg"))


# ── perceptual hash comparison ──────────────────────────────────────────────

def phash(path: pathlib.Path) -> imagehash.ImageHash | None:
    try:
        return imagehash.phash(Image.open(path).convert("RGB"))
    except Exception:
        return None


def images_look_same(old: pathlib.Path, new: pathlib.Path, threshold: int) -> bool:
    h1, h2 = phash(old), phash(new)
    if h1 is None or h2 is None:
        return False
    return (h1 - h2) <= threshold


def image_size(path: pathlib.Path) -> str:
    try:
        img = Image.open(path)
        return f"{img.width}×{img.height}"
    except Exception:
        return "?"


# ── database ────────────────────────────────────────────────────────────────

def get_data(album_id: str | None):
    conn = psycopg2.connect(dbname="alba")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    where = "WHERE b.url IS NOT NULL" + (f" AND b.albumid = %s" if album_id else "")
    params = (album_id,) if album_id else ()

    cur.execute(f"""
        SELECT
            a.albumid,
            a.name AS album_name,
            a.numberofpages,
            b.bijdrageid,
            b.page
        FROM bijdrage_table b
        JOIN album_table a ON a.albumid = b.albumid
        {where}
        ORDER BY a.albumid, b.page NULLS LAST, b.bijdrageid
    """, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ── main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--album-id", default=None)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--threshold", type=int, default=10)
    parser.add_argument("--no-hash", action="store_true")
    args = parser.parse_args()

    rows = get_data(args.album_id)
    if not rows:
        print("No contributions found.")
        return

    # Group by album
    albums: dict[str, dict] = {}
    for row in rows:
        aid = str(row["albumid"])
        if aid not in albums:
            albums[aid] = {
                "name": row["album_name"] or "Untitled",
                "num_pages": row["numberofpages"],
                "contributions": [],
            }
        albums[aid]["contributions"].append(row)

    # Totals
    grand = dict(only_old=0, only_new=0, both_same=0, both_differ=0, neither=0,
                 new_extra=0)

    for aid, album in albums.items():
        folder = IMAGES_DIR / aid
        total_scans = len(list(folder.glob("page_*.jpg"))) if folder.is_dir() else 0
        num_pages = album["num_pages"]

        counts = dict(only_old=0, only_new=0, both_same=0, both_differ=0, neither=0,
                      new_extra=0)
        detail_lines = []

        for c in album["contributions"]:
            bid = str(c["bijdrageid"])
            page = c["page"]

            old = old_image_path(aid, page, total_scans, num_pages)
            new_list = new_image_paths(aid, bid)

            has_old = old is not None
            has_new = len(new_list) > 0
            extra_new = len(new_list) - 1  # images beyond the first

            if has_old and has_new:
                if args.no_hash:
                    same = None
                    label = "BOTH      "
                    counts["both_same"] += 1  # "both_same" slot reused as "both exists"
                else:
                    same = images_look_same(old, new_list[0], args.threshold)
                    label = "SAME ✓   " if same else "DIFFER ✗ "
                    if same:
                        counts["both_same"] += 1
                    else:
                        counts["both_differ"] += 1
            elif has_old:
                label = "OLD ONLY  "
                counts["only_old"] += 1
            elif has_new:
                label = "NEW ONLY  "
                counts["only_new"] += 1
            else:
                label = "NONE ✗✗  "
                counts["neither"] += 1

            if extra_new > 0:
                counts["new_extra"] += extra_new

            if args.verbose:
                old_info = f"{old.name} ({image_size(old)})" if old else "—"
                new_info = (
                    f"{len(new_list)}× scraped ({image_size(new_list[0])})"
                    if new_list else "—"
                )
                detail_lines.append(
                    f"  {label}  p{page or '?':>4}  {bid[:8]}…  "
                    f"old={old_info}  new={new_info}"
                )

        total = sum(counts[k] for k in ("only_old", "only_new", "both_same", "both_differ", "neither"))
        scraped_pct = round((counts["only_new"] + counts["both_same"] + counts["both_differ"]) * 100 / total) if total else 0

        print(f"\n{'─'*70}")
        print(f"Album: {album['name'][:50]}")
        print(f"  ID : {aid}")
        print(f"  contributions : {total}")
        print(f"  bulk scans    : {total_scans}  (num_pages={num_pages})")
        print(f"  scraped       : {scraped_pct}%")
        print(f"  ├ only old    : {counts['only_old']}")
        print(f"  ├ only new    : {counts['only_new']}")
        if not args.no_hash:
            print(f"  ├ both SAME   : {counts['both_same']}")
            print(f"  ├ both DIFFER : {counts['both_differ']}")
        else:
            print(f"  ├ both (exist): {counts['both_same']}")
        print(f"  ├ no image    : {counts['neither']}")
        if counts["new_extra"]:
            print(f"  └ extra imgs  : +{counts['new_extra']} additional scraped images")

        if args.verbose:
            for line in detail_lines:
                print(line)

        for k in grand:
            grand[k] += counts.get(k, 0)

    n_albums = len(albums)
    n_contrib = len(rows)
    print(f"\n{'═'*70}")
    print(f"TOTAL  {n_albums} albums  |  {n_contrib} contributions")
    print(f"  only old    : {grand['only_old']}  ({grand['only_old']*100//n_contrib if n_contrib else 0}%)")
    print(f"  only new    : {grand['only_new']}  ({grand['only_new']*100//n_contrib if n_contrib else 0}%)")
    if not args.no_hash:
        print(f"  both SAME   : {grand['both_same']}  ({grand['both_same']*100//n_contrib if n_contrib else 0}%)")
        print(f"  both DIFFER : {grand['both_differ']}  ({grand['both_differ']*100//n_contrib if n_contrib else 0}%)")
    print(f"  no image    : {grand['neither']}  ({grand['neither']*100//n_contrib if n_contrib else 0}%)")
    if grand["new_extra"]:
        print(f"  extra imgs  : +{grand['new_extra']} additional scraped images (multi-page contributions)")


if __name__ == "__main__":
    main()
