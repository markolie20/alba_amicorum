from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import local_functions as LF
import local_queries as LQ
import pandas as pd
import time

conn = LF.connect_db()
cur = conn.cursor()
cur.execute(LQ.select_unique_locations)

def geo_mapper():
    geolocator = Nominatim(user_agent="alba_amicorum_geocoder")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    locations_map = []
    for (place,) in cur.fetchall():
        try:

            location = geocode(place)
            if location:
                locations_map.append({
                    "place": place,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "display_name": location.address
                })
                print(f"✔ {place} -> {location.latitude}, {location.longitude}")
            else:
                locations_map.append({
                    "place": place,
                    "latitude": None,
                    "longitude": None,
                    "display_name": None
                })
                print(f"✘ No result for {place}")

        except Exception as e:
            print(f"Error for {place}: {e}")

        time.sleep(1)
    df = pd.DataFrame(locations_map)

    # Save CSV
    csv_path = "places_coordinates.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")

    print(f"\nSaved results to: {csv_path}")
    print(df.head())

    for _, row in df.iterrows():
        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
            cur.execute(
                """
                INSERT INTO place_table (
                    location,
                    latitude,
                    longitude,
                    coordinates
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                )
                ON CONFLICT (location)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    coordinates = EXCLUDED.coordinates
                """,
                (
                    row["place"],
                    row["latitude"],
                    row["longitude"],
                    row["longitude"],
                    row["latitude"]
                )
            )

conn.commit()
cur.close()
conn.close()


