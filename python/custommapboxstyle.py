"""
this script checks for the presence of the custom Mapbox style HTML file and the geocoded CSV file.
it reports on their existence and the number of rows in the CSV and does nothing else (finally).
"""

import os
import pandas as pd

MAP_HTML_PATH = os.path.join("data", "lenzieswholunchanddinner_map_custom.html")
GEOCODED_CSV_PATH = os.path.join("data", "lenzieswholunchanddinner_geocoded.csv")


def main():
    print("=" * 60)
    print("  Lenzie Who Lunches and Dinners Asset Check")
    print("=" * 60)

    if os.path.exists(MAP_HTML_PATH):
        print(f"Map file found: {MAP_HTML_PATH}")
    else:
        print(f"Map file missing: {MAP_HTML_PATH}")

    if not os.path.exists(GEOCODED_CSV_PATH):
        print(f"Geocoded CSV missing: {GEOCODED_CSV_PATH}")
        print("No map generation occurs in this script.")
        return

    df = pd.read_csv(GEOCODED_CSV_PATH)
    row_count = len(df)

    has_lat = "Latitude" in df.columns
    has_lon = "Longitude" in df.columns

    if has_lat and has_lon:
        coord_rows = df["Latitude"].notna().sum() if row_count else 0
    else:
        coord_rows = 0

    print(f"Geocoded CSV found: {GEOCODED_CSV_PATH}")
    print(f"Rows in CSV: {row_count}")
    print(f"Rows with coordinates: {coord_rows}")
    print("No map generation occurs in this script.")


if __name__ == "__main__":
    main()
