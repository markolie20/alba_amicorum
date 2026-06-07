import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote


def get_album_name(url):
    return urlparse(url).path.rstrip("/").split("/")[-1]


def get_identifier(url):
    params = parse_qs(urlparse(url).query)
    return unquote(params["identifier"][0])


def download_album(url, session):
    album_name = get_album_name(url)
    identifier = get_identifier(url)

    out_dir = Path("data/images") / album_name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  [{album_name}] identifier={identifier}")

    count = 1
    while True:
        image_url = (
            f"https://resolver.kb.nl/resolve"
            f"?urn=urn:gvn:{identifier}&role=page&count={count}&role=image&size=large"
        )
        response = session.get(image_url, timeout=30)

        if response.status_code != 200:
            break

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            break

        ext = content_type.split("/")[-1].split(";")[0].strip()
        if ext == "jpeg":
            ext = "jpg"

        out_file = out_dir / f"page_{count:03d}.{ext}"
        out_file.write_bytes(response.content)
        print(f"    page {count:03d} -> {out_file}")
        count += 1

    print(f"  done: {count - 1} pages")


with open("links.txt") as f:
    urls = [line.strip() for line in f if line.strip()]

with requests.Session() as session:
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        download_album(url, session)
