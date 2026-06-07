tables_creation = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS album_table (
    albumId UUID PRIMARY KEY,
    url TEXT UNIQUE,
    name TEXT,
    dateCreated DATE,
    width INTEGER,
    height INTEGER,
    funder TEXT,
    identifier1 TEXT,
    identifier2 TEXT,
    identifier3 TEXT,
    numberOfPages INTEGER
);

CREATE TABLE IF NOT EXISTS bijdrage_table (
    bijdrageId UUID PRIMARY KEY,
    albumId UUID REFERENCES album_table(albumId),
    url TEXT UNIQUE,
    dateCreated DATE,
    name TEXT,
    page INTEGER,
    position INTEGER
);

CREATE TABLE IF NOT EXISTS place_table (
    placeId UUID PRIMARY KEY,
    location TEXT NOT NULL UNIQUE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    coordinates GEOGRAPHY(POINT, 4326)
);

CREATE TABLE IF NOT EXISTS location_album_table (
    locationId UUID PRIMARY KEY,
    albumId UUID REFERENCES album_table(albumId) ON DELETE CASCADE,
    raw_location TEXT NOT NULL,
    placeId UUID REFERENCES place_table(placeId) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS location_bijdrage_table (
    locationId UUID PRIMARY KEY,
    bijdrageId UUID REFERENCES bijdrage_table(bijdrageId) ON DELETE CASCADE,
    raw_location TEXT NOT NULL,
    placeId UUID REFERENCES place_table(placeId) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS album_author_table (
    authorId UUID PRIMARY KEY,
    albumId UUID REFERENCES album_table(albumId) ON DELETE CASCADE,
    name TEXT
);

CREATE TABLE IF NOT EXISTS bijdrage_author_table (
    authorId UUID PRIMARY KEY,
    bijdrageId UUID REFERENCES bijdrage_table(bijdrageId) ON DELETE CASCADE,
    name TEXT
);

CREATE TABLE IF NOT EXISTS description_album_table (
    descriptionId UUID PRIMARY KEY,
    albumId UUID REFERENCES album_table(albumId) ON DELETE CASCADE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS description_bijdrage_table (
    descriptionId UUID PRIMARY KEY,
    bijdrageId UUID REFERENCES bijdrage_table(bijdrageId) ON DELETE CASCADE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS album_language_table (
    languageId UUID PRIMARY KEY,
    albumId UUID REFERENCES album_table(albumId) ON DELETE CASCADE,
    language TEXT
);

CREATE TABLE IF NOT EXISTS album_material_table (
    materialId UUID PRIMARY KEY,
    albumId UUID REFERENCES album_table(albumId) ON DELETE CASCADE,
    material TEXT
);
CREATE TABLE IF NOT EXISTS location_normalization (
    raw_location TEXT PRIMARY KEY,
    normalized_location TEXT NOT NULL
);
"""


insert_normalization_table = """
        INSERT INTO location_normalization (raw_location, normalized_location)
        VALUES (%s, %s)
        ON CONFLICT (raw_location)
        DO UPDATE 
        SET normalized_location = EXCLUDED.normalized_location
    """

select_unique_locations = """
    SELECT DISTINCT raw_location
    FROM (
        SELECT raw_location FROM location_album_table
        UNION
        SELECT raw_location FROM location_bijdrage_table
    ) AS all_locations
    WHERE raw_location IS NOT NULL
    ORDER BY raw_location
"""