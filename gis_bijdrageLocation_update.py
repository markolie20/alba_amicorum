from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import local_functions as LF


def update_missing_gis_data():
    conn = LF.connect_db()
    cur = conn.cursor()

    geolocator = Nominatim(user_agent="alba_amicorum_geocoder")
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1,
        swallow_exceptions=False
    )

    try:
        cur.execute("""
            SELECT placeid, place_name
            FROM place_table
            WHERE latitude IS NULL
               OR longitude IS NULL
               OR coordinates IS NULL
            ORDER BY place_name
        """)

        places = cur.fetchall()
        print(f"Places needing GIS data: {len(places)}")

        for placeid, place_name in places:
            try:
                location = geocode(place_name)

                if location is None:
                    print(f"not found: {place_name}")
                    continue

                lat = location.latitude
                lon = location.longitude

                cur.execute("""
                    UPDATE place_table
                    SET
                        latitude = %s,
                        longitude = %s,
                        coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    WHERE placeid = %s
                """, (
                    lat,
                    lon,
                    lon,
                    lat,
                    placeid,
                ))

                conn.commit()
                print(f"updated: {place_name} -> {lat}, {lon}")

            except Exception as e:
                conn.rollback()
                print(f"failed for {place_name}: {e}")

    finally:
        cur.close()
        conn.close()
