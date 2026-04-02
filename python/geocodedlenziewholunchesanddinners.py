# =============================================================================
# Geocode the Restaurants and Build a Map!
# =============================================================================
# this was almost entirely ripped from the in class excercise on geocoding and mapping, but i changed everything to match the new data that i made :)
#
# this is ripped (again) from my main portfolio project with only editing in the file names so that everything can be run accurately here :)
#
# WHAT THIS SCRIPT DOES:
#   1. Reads the restaurant data CSV
#   2. For each restaurant, sends the address to the Mapbox Geocoding API
#      to get back latitude and longitude coordinates
#   3. Saves the enriched data (with lat/lon) as a new CSV
#   4. Creates an interactive web map using Folium with a simple basemap
#   5. Saves the map as an HTML file you can open in any browser!!
#
# BEFORE YOU RUN THIS SCRIPT:
#   You must add your Mapbox access token (see Step 2 below).
#   You must have some sort of CSV file that this can read.
#
# OUTPUT:
#   data/lenzieswholunchanddinner_geocoded.csv   — restaurant data with lat/lon columns added
#   data/lenzieswholunchanddinner_map_basic.html — interactive map (open in browser)
#
# TO RUN:
#   python geocodelenzieswholunchanddinner.py
# =============================================================================


# =============================================================================
# STEP 1: IMPORT LIBRARIES
# =============================================================================

import requests         # For sending API calls to Mapbox over the internet
import pandas as pd     # For reading the CSV and working with tabular data
import folium           # For creating interactive HTML maps
import os               # For file/folder path operations
import time             # For adding a small pause between API calls (be polite!)


# =============================================================================
# STEP 2: ADD YOUR MAPBOX ACCESS TOKEN
# =============================================================================
# IMPORTANT: You must replace the placeholder below with your REAL token.
#
# HOW TO FIND YOUR MAPBOX ACCESS TOKEN:
#   1. Go to https://account.mapbox.com/access-tokens/
#   2. Sign in to your Mapbox account
#   3. You will see a "Default public token" — it starts with "pk."
#   4. Click the copy button next to it
#   5. Paste it below, replacing the placeholder text
#
# SECURITY NOTE: Never share your access token publicly or commit it to GitHub.
# For now, pasting it directly in the script is fine for class exercises.

MAPBOX_TOKEN = "pk.eyJ1Ijoic2xsZW56aWUiLCJhIjoiY21tYXc5YXFlMGpwdDJ3b2ltaTU4dHIxaCJ9.yAsfpMXpkTRiH-Gvn0-J-g"  

# Quick check — remind the student if they forgot to set the token
if MAPBOX_TOKEN == "PASTE_YOUR_MAPBOX_TOKEN_HERE":
    print("ERROR: You need to add your Mapbox access token!")
    print("  Open this script, find the MAPBOX_TOKEN line near the top,")
    print("  and replace PASTE_YOUR_MAPBOX_TOKEN_HERE with your real token.")
    print("  Your token starts with 'pk.' and can be found at:")
    print("  https://account.mapbox.com/access-tokens/")
    exit()

# For the record!! There's a public token you can get and use, and that's what is included in here. It's a special token that you can add specific URLs to be able to use. 

# =============================================================================
# STEP 3: DEFINE THE GEOCODING FUNCTION
# =============================================================================
# A "function" in Python is a reusable block of code. We define it once
# here, then call it multiple times (once per restaurant) in our loop below.
#
# This function takes an address string, sends it to the Mapbox Geocoding
# API, and returns a [latitude, longitude] pair (or [None, None] if it fails).

def geocode_address(address_string, token):
    """
    Look up the lat/lon coordinates for a text address using Mapbox.

    Parameters:
        address_string (str): The full address to look up, e.g.,
                              "1160 Oak Knoll Ave, Napa, California 94558"
        token (str): Your Mapbox public access token

    Returns:
        tuple: (latitude, longitude) as floats, or (None, None) if lookup fails
    """

    # Skip addresses that are blank or PO Boxes — Mapbox can't place those
    # on a map because they don't represent a physical street location.
    if not address_string or "P.O. Box" in address_string or "PO Box" in address_string:
        return None, None

    # Build the Mapbox Geocoding API URL.
    # The Mapbox v6 "forward geocoding" endpoint converts text → coordinates.
    # We include the token for authentication.
    # "country=us" limits results to the United States (improves accuracy)
    # "limit=1" means only return the single most relevant result
    geocode_url = (
        f"https://api.mapbox.com/search/geocode/v6/forward"
        f"?q={requests.utils.quote(address_string)}"  # URL-encode the address
        f"&country=us"
        f"&limit=1"
        f"&access_token={token}"
    )

    try:
        # Send the request and wait up to 10 seconds for a response
        response = requests.get(geocode_url, timeout=10)

        # Check if the request was successful
        if response.status_code != 200:
            return None, None

        # Parse the JSON response into a Python dictionary
        data = response.json()

        # Navigate the JSON structure to get the coordinates.
        # Mapbox returns results in a 'features' list. The first item
        # is the best match. Coordinates are stored as [longitude, latitude].
        features = data.get("features", [])
        if features:
            coords = features[0]["geometry"]["coordinates"]
            longitude = coords[0]
            latitude = coords[1]
            return latitude, longitude

    except requests.exceptions.RequestException:
        # If anything goes wrong with the request, return None
        return None, None

    return None, None  # Fallback if no features were found


# =============================================================================
# STEP 4: READ THE RESTAURANT DATA FROM CSV
# =============================================================================
print("=" * 60)
print("  Lenzie Who Lunches and Dinners Geocoder & Basic Map Builder")
print("=" * 60)

# Define the path to our input file (output of Script 1)
input_path = os.path.join("data", "lenzieswholunchanddinner.csv")

# Check that the file actually exists before trying to open it
if not os.path.exists(input_path):
    print(f"\nERROR: Input file not found: {input_path}")
    print("Please run Script 1 first (lenzieswholunchanddinner.py)")
    exit()

# pd.read_csv() loads the CSV file into a pandas DataFrame
df = pd.read_csv(input_path)

print(f"\nLoaded {len(df)} restaurants from: {input_path}")

# Check if we already have geocoded data
geocoded_path = os.path.join("data", "lenzieswholunchanddinner_geocoded.csv")
if os.path.exists(geocoded_path):
    df_existing = pd.read_csv(geocoded_path)
    if "Latitude" in df_existing.columns and "Longitude" in df_existing.columns:
        # Check if there are any non-null coordinates
        existing_geocoded = df_existing["Latitude"].notna().sum()
        if existing_geocoded > 0:
            print(f"Found existing geocoded file with {existing_geocoded} coordinates.")
            print("Using existing coordinates instead of re-geocoding.")
            df = df_existing
            # Skip to map building
            skip_geocoding = True
        else:
            skip_geocoding = False
    else:
        skip_geocoding = False
else:
    skip_geocoding = False


# =============================================================================
# STEP 5: GEOCODE EACH ADDRESS (OR SKIP IF ALREADY DONE)
# =============================================================================
if not skip_geocoding:
    print("\nGeocoding addresses using Mapbox API...")
    print("(This may take a minute — we pause briefly between each request\n"
          " to avoid overwhelming the API server.)")

    # Create empty lists to store the coordinates we get back
    latitudes = []
    longitudes = []

    # Loop through each row in the DataFrame using iterrows().
    # 'i' is the row index (0, 1, 2...), 'row' is the row data.
    for i, row in df.iterrows():

        # Build the full address string for geocoding.
        # We combine the address fields for the best possible result.
        address = row.get("Address", "")

        # Show progress so students can see the script is working
        name = row.get("Name", f"Row {i}")
        print(f"  [{i+1}/{len(df)}] Geocoding: {name[:40]}...")

        # Call our geocoding function
        lat, lon = geocode_address(address, MAPBOX_TOKEN)

        # Append the result to our lists
        latitudes.append(lat)
        longitudes.append(lon)

        # time.sleep() pauses execution for 0.1 seconds between requests.
        # This is called "rate limiting" — it's considerate to API servers
        # and prevents your account from being flagged for excessive requests.
        time.sleep(0.1)

    # Add the latitude and longitude as new columns in our DataFrame
    df["Latitude"] = latitudes
    df["Longitude"] = longitudes

    # Count how many addresses were successfully geocoded
    geocoded_count = df["Latitude"].notna().sum()
    print(f"\nSuccessfully geocoded: {geocoded_count} out of {len(df)} restaurants")
    print(f"Could not geocode:      {len(df) - geocoded_count} restaurants")
    print("  (PO Boxes, missing addresses, and very rural locations may not geocode)")


# =============================================================================
# STEP 6: SAVE THE GEOCODED DATA TO A NEW CSV
# =============================================================================
os.makedirs("data", exist_ok=True)
geocoded_path = os.path.join("data", "lenzieswholunchanddinner_geocoded.csv")

# Save the updated DataFrame (now with Latitude/Longitude columns) to CSV
df.to_csv(geocoded_path, index=False, encoding="utf-8-sig")
print(f"\nGeocoded data saved to: {geocoded_path}")


# =============================================================================
# STEP 7: CREATE THE INTERACTIVE MAP WITH FOLIUM
# =============================================================================
print("\nBuilding interactive map with Folium...")

# --- Filter to Only Geocoded Restaurants ---
# We can only place markers for restaurants where we have coordinates.
# dropna() removes all rows where Latitude OR Longitude is missing (NaN).
df_mapped = df.dropna(subset=["Latitude", "Longitude"]).copy()
print(f"  Placing {len(df_mapped)} markers on the map.")

# --- Calculate the Map Center ---
# We center the map on the average lat/lon of all our mapped restaurants.
# This ensures the map opens centered on your data.
if len(df_mapped) > 0:
    center_lat = df_mapped["Latitude"].mean()
    center_lon = df_mapped["Longitude"].mean()
else:
    # Default to South Bay area if no coordinates
    print("  Warning: No geocoded addresses found. Using default South Bay center.")
    center_lat = 33.8688
    center_lon = -118.3940

# --- Create the Folium Map Object ---
# folium.Map() creates a new blank map.
#   location = [lat, lon] sets where the map is centered
#   zoom_start controls the initial zoom level (higher = more zoomed in)
#   tiles="OpenStreetMap" uses the free OpenStreetMap basemap (no key needed)
napa_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11,
    tiles="OpenStreetMap"
)

# --- Add a Title to the Map ---
# We inject a small HTML block into the map to display a title
title_html = """
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
     z-index: 1000; background-color: white; padding: 10px 20px;
     border: 2px solid #8B0000; border-radius: 8px; font-family: Georgia, serif;
     font-size: 16px; font-weight: bold; color: #8B0000; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    Lenzie Who Lunches and Dinners
</div>
"""
napa_map.get_root().html.add_child(folium.Element(title_html))

# --- Add a Marker for Each Restaurant ---
# We loop through each geocoded restaurant and add a map marker.
for i, row in df_mapped.iterrows():

    # Build the popup HTML content.
    # A "popup" is the text box that appears when you click a marker.
    # We format it as a small HTML card with the restaurant's details.
    address_display = row["Address"] if pd.notna(row["Address"]) else "Address not available"
    cuisine_display = row["Cuisine"] if pd.notna(row["Cuisine"]) else "Not listed"
    attire_display = row["Attire"] if pd.notna(row["Attire"]) else "Not specified"
    description_display = row["Stella's Thoughts"] if pd.notna(row["Stella's Thoughts"]) else "No description available"
    website_display = row["Website"] if pd.notna(row["Website"]) else ""
    image_url = row["Image_URL"] if pd.notna(row["Image_URL"]) else ""

    # Add website link if available
    website_html = f'<br><br><b>Website:</b> <a href="{website_display}" target="_blank">Visit Website</a>' if website_display else ""
    
    # Add image if available
    image_html = f'<img src="{image_url}" style="width: 100%; max-width: 280px; height: auto; border-radius: 4px; margin-bottom: 10px;" alt="{row["Name"]}">' if image_url else ""

    popup_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 13px; min-width: 250px; max-width: 300px;">
        <h4 style="margin: 0 0 8px 0; color: #8B0000; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
            {row['Name']}
        </h4>
        {image_html}
        <b>Address:</b><br>
        {address_display}<br><br>
        <b>Cuisine:</b> {cuisine_display}<br><br>
        <b>Attire:</b> {attire_display}<br><br>
        <b>Stella's Thoughts:</b><br>
        <div style="max-height: 100px; overflow-y: auto; font-size: 12px;">
        {description_display}
        </div>
        {website_html}
    </div>
    """

    # folium.CircleMarker() places a colored circle on the map
    # instead of the default pin icon — great for datasets with many points.
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],  # Position on the map
        radius=6,               # Size of the circle in pixels
        color="#8B0000",        # Circle border color (dark red)
        fill=True,              # Fill the circle with color
        fill_color="#C41E3A",   # Fill color (crimson red)
        fill_opacity=0.7,       # Transparency: 0.0 = invisible, 1.0 = solid
        popup=folium.Popup(popup_html, max_width=300),  # Click popup
        tooltip=row["Name"]     # Text that appears when you HOVER over the marker
    ).add_to(napa_map)          # .add_to() places the marker on our map object


# --- Add a Layer Control ---
# This adds a small toggle in the top-right corner to show/hide layers.
# It's good UX practice even with just one layer.
folium.LayerControl().add_to(napa_map)


# =============================================================================
# STEP 8: SAVE THE MAP AS AN HTML FILE
# =============================================================================
standalone_map_path = os.path.join("data", "lenzieswholunchanddinner_map.html")
napa_map.save(standalone_map_path)

print(f"  Standalone map saved to: {standalone_map_path}")
print("\n" + "=" * 60)
print("  SCRIPT COMPLETE!")
print("=" * 60)
print("\nTo view your map:")
print(f"  1. Open {standalone_map_path} in your browser")
