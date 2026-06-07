from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from uuid import uuid4
import local_functions as LFunc

import pandas as pd

def insert_postgis():

    conn = LFunc.connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT raw_location
        FROM (
            SELECT raw_location FROM location_album_table
            UNION
            SELECT raw_location FROM location_bijdrage_table
        ) AS all_locations
        ORDER BY raw_location
    """)

    places = [row[0] for row in cur.fetchall()]

    print(f"Unique locations found: {len(places)}")

    geolocator = Nominatim(user_agent="alba_amicorum_geocoder")
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1,
        swallow_exceptions=False
    )

    results = []

    for place in places:
        try:
            location = geocode(place)

            if location:
                results.append({
                    "place": place,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "display_name": location.address
                })

                print(f"✔ {place} -> {location.latitude}, {location.longitude}")

            else:
                results.append({
                    "place": place,
                    "latitude": None,
                    "longitude": None,
                    "display_name": None
                })

                print(f"✘ No result for {place}")

        except Exception as e:
            results.append({
                "place": place,
                "latitude": None,
                "longitude": None,
                "display_name": None
            })

            print(f"Error for {place}: {e}")

    df = pd.DataFrame(results)

    df.to_csv("places_coordinates.csv", index=False, encoding="utf-8")

    print("\nSaved results to places_coordinates.csv")
    print(df.head())

    for row in results:
        if row["latitude"] is not None:
            cur.execute("""
                INSERT INTO place_table (placeId, location, latitude, longitude, coordinates)
                VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                ON CONFLICT (location) DO NOTHING
            """, (
                str(uuid4()),
                row["place"],
                row["latitude"],
                row["longitude"],
                row["longitude"],
                row["latitude"],
            ))
        else:
            cur.execute("""
                INSERT INTO place_table (placeId, location, latitude, longitude, coordinates)
                VALUES (%s, %s, NULL, NULL, NULL)
                ON CONFLICT (location) DO NOTHING
            """, (str(uuid4()), row["place"]))

    conn.commit()
    print(f"Inserted {len(results)} rows into place_table.")

    cur.close()
    conn.close()
