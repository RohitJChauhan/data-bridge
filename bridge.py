import logging
import sqlite3

import pandas as pd
import requests

from log_config import setup_logging

logger = logging.getLogger(__name__)

URL = "https://api.open-meteo.com/v1/forecast"
DB_PATH = "data_bridge.db"

CITIES = {
    "Delhi": (28.61, 77.20),
    "Mumbai": (19.07, 72.87),
    "Bengaluru": (12.97, 77.59),
    "Chennai": (13.08, 80.27),
}


def extract():
    """Call the API for each city and return raw records."""
    records = []
    for city, (lat, lon) in CITIES.items():
        params = {"latitude": lat, "longitude": lon,
                  "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"}
        response = requests.get(URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()["current"]
        data["city"] = city
        records.append(data)
        logger.info("Fetched %s", city)
    return records


def transform(records):
    """Clean the raw records and return a tidy table."""
    df = pd.DataFrame(records)
    df = df.rename(columns={"temperature_2m": "temp_c",
                            "relative_humidity_2m": "humidity_pct",
                            "wind_speed_10m": "wind_kmh"})
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop(columns=["interval"])

    before = len(df)
    df = df.dropna(subset=["temp_c"])
    df = df[(df["temp_c"] > -50) & (df["temp_c"] < 60)]
    df = df.drop_duplicates(subset=["city", "time"])
    removed = before - len(df)
    if removed:
        logger.warning("Removed %d bad or duplicate rows", removed)

    return df[["city", "time", "temp_c", "humidity_pct", "wind_kmh"]]


def load(df):
    """Save the table into SQLite and return how many new rows were added."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            city TEXT, time TEXT, temp_c REAL,
            humidity_pct REAL, wind_kmh REAL,
            UNIQUE(city, time)
        )
    """)
    df = df.assign(time=df["time"].astype(str))
    before = conn.total_changes
    for row in df.itertuples(index=False):
        conn.execute("INSERT OR IGNORE INTO weather VALUES (?, ?, ?, ?, ?)", tuple(row))
    conn.commit()
    added = conn.total_changes - before
    conn.close()
    return added


def run():
    raw = extract()
    clean = transform(raw)
    added = load(clean)
    logger.info("Extracted %d | Clean %d | New rows saved %d", len(raw), len(clean), added)


if __name__ == "__main__":
    setup_logging()
    run()