# =============================================================================
# SCRIPT 3 — Section 930: Create Map with Custom Mapbox Style
# =============================================================================
#
# ripped from my main portfolio project with only editing in the file names so that everything can be run accurately here :)
#
# WHAT THIS SCRIPT DOES:
#   Uses the geocoded restaurant data and swaps out the plain OpenStreetMap
#   basemap from Script 2 for YOUR custom Mapbox style created in Mapbox Studio.
#   The markers and popups are identical to Script 2 — only the basemap changes.
#
# BEFORE YOU RUN THIS SCRIPT:
#   1. You must have completed Mapbox Studio Step 4 (built your custom style)
#   2. You must have published your style and have the Style URL ready
#   3. You must have your Mapbox access token (same one from Script 2)
#   4. Script 2 must have been run so data/lenzieswholunchanddinner_geocoded.csv exists
#
# OUTPUT:
#   data/lenzieswholunchanddinner.html
#
# TO RUN:
#   python custommapboxstyle.py
# =============================================================================


# =============================================================================
# STEP 1: IMPORT LIBRARIES
# =============================================================================

import pandas as pd     # For reading the geocoded CSV
import folium           # For creating the interactive map
import os               # For file path operations


# =============================================================================
# STEP 2: ADD YOUR MAPBOX CREDENTIALS
# =============================================================================
# You need TWO things from your Mapbox account for this script:
#
# --- A) YOUR MAPBOX ACCESS TOKEN ---
# Same token you used in Script 2 (starts with "pk.")
# Find it at: https://account.mapbox.com/access-tokens/
MAPBOX_TOKEN = "pk.eyJ1Ijoic2xsZW56aWUiLCJhIjoiY21sdG13MjB3MDF5dTNlcHBqZGt0NGVvdSJ9.-DaMTxcKxtsIZSl9_S7wNg"

# --- B) YOUR MAPBOX STYLE URL ---
# This is the URL of the custom style you created in Mapbox Studio.
# HOW TO FIND YOUR STYLE URL:
#   1. Go to https://studio.mapbox.com
#   2. Click on your style to open it
#   3. Click the "Share" button in the top right
#   4. Make sure the style is set to "Public"
#   5. Your Style URL looks like: mapbox://styles/yourusername/yourstyleid
#      (e.g., mapbox://styles/johndoe1/clxabcdef123456)
#   6. Copy that URL and paste it below
MAPBOX_STYLE_URL = "mapbox://styles/sllenzie/cmnhm67m2000t01p1hnlc98z3"

# --- Validate that tokens were entered ---
if MAPBOX_TOKEN == "PASTE_YOUR_MAPBOX_TOKEN_HERE":
    print("ERROR: Please add your Mapbox access token to this script.")
    print("  (Look for the MAPBOX_TOKEN variable near the top.)")
    exit()

if "YOUR_USERNAME" in MAPBOX_STYLE_URL or "YOUR_STYLE_ID" in MAPBOX_STYLE_URL:
    print("ERROR: Please add your Mapbox Style URL to this script.")
    print("  (Look for the MAPBOX_STYLE_URL variable near the top.)")
    print("  Your style URL looks like: mapbox://styles/yourusername/yourstyleid")
    exit()


# =============================================================================
# STEP 3: CONVERT MAPBOX STYLE URL TO A TILE URL
# =============================================================================
# Folium uses a "tile URL" to load map tiles from a web server.
# A tile URL is a web address template with {z}, {x}, {y} placeholders
# that tell the browser which map tile to load at which zoom level and position.
#
# Mapbox style URLs (mapbox://styles/...) are NOT tile URLs — they are
# just identifiers for the style in the Mapbox ecosystem.
# We need to convert it into the actual HTTP tile URL format.
#
# The conversion formula:
#   mapbox://styles/USERNAME/STYLEID
#   → https://api.mapbox.com/styles/v1/USERNAME/STYLEID/tiles/256/{z}/{x}/{y}@2x?access_token=TOKEN
#
# Let's extract the username and style ID from the style URL and build the tile URL.

# Remove the "mapbox://styles/" prefix to get "username/styleid"
style_path = MAPBOX_STYLE_URL.replace("mapbox://styles/", "")

# Build the tile URL using the Mapbox Styles API format
# {z} = zoom level, {x} = tile column, {y} = tile row (these are filled in automatically)
TILE_URL = (
    f"https://api.mapbox.com/styles/v1/{style_path}/tiles/256/{{z}}/{{x}}/{{y}}"
    f"?access_token={MAPBOX_TOKEN}"
)

# Attribution text that must be displayed on the map (Mapbox requires this)
TILE_ATTRIBUTION = (
    '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> '
    '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
)

print("=" * 60)
print("  Lenzie Who Lunches and Dinners — Custom Mapbox Style Map")
print("=" * 60)
print(f"\nUsing style: {MAPBOX_STYLE_URL}")


# =============================================================================
# STEP 4: READ THE GEOCODED WINERY DATA
# =============================================================================
input_path = os.path.join("data", "lenzieswholunchanddinner_geocoded.csv")

# Check that Script 2 has already been run and the file exists
if not os.path.exists(input_path):
    print(f"\nERROR: File not found: {input_path}")
    print("Please run Script 2 first (02_geocode_map_basic.py) to create this file.")
    exit()

df = pd.read_csv(input_path)

# Keep only rows that have valid coordinates (Latitude and Longitude not blank)
df_mapped = df.dropna(subset=["Latitude", "Longitude"]).copy()

print(f"\nLoaded {len(df)} restaurants. {len(df_mapped)} have coordinates for mapping.")


# =============================================================================
# STEP 5: CREATE THE FOLIUM MAP WITH YOUR CUSTOM STYLE
# =============================================================================
print("\nBuilding map with custom Mapbox basemap...")

# Calculate the center of all mapped restaurants
if len(df_mapped) > 0:
    center_lat = df_mapped["Latitude"].mean()
    center_lon = df_mapped["Longitude"].mean()
else:
    # Default to South Bay if no coordinates
    print("Warning: No geocoded coordinates found. Using default center.")
    center_lat = 33.8688
    center_lon = -118.3940

# --- Create the Map with the Custom Tile Layer ---
# This time, instead of using a named basemap like "OpenStreetMap",
# we pass our Mapbox tile URL directly.
#
# tiles=TILE_URL         tells Folium WHERE to load map images from
# attr=TILE_ATTRIBUTION  sets the copyright credit displayed on the map
restaurant_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11,
    tiles=TILE_URL,
    attr=TILE_ATTRIBUTION
)

# --- Add a Title ---
title_html = """
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
     z-index: 1000; background-color: rgba(255,255,255,0.9); padding: 10px 20px;
     border: 2px solid #8B0000; border-radius: 8px; font-family: Georgia, serif;
     font-size: 16px; font-weight: bold; color: #8B0000; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
     Lenzie Who Lunches and Dinners — Custom Style
</div>
"""
restaurant_map.get_root().html.add_child(folium.Element(title_html))

# --- Add Markers for Each Restaurant ---
# This loop is identical to Script 2 — the markers haven't changed, only the basemap.
# Notice how easy it is to swap the basemap by just changing the 'tiles' parameter!
for i, row in df_mapped.iterrows():

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

    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=6,
        color="#8B0000",
        fill=True,
        fill_color="#C41E3A",
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["Name"]
    ).add_to(restaurant_map)

# --- Add a Layer Control ---
folium.LayerControl().add_to(restaurant_map)


# =============================================================================
# STEP 6: SAVE THE MAP
# =============================================================================
os.makedirs("data", exist_ok=True)
output_path = os.path.join("data", "lenzieswholunchanddinner_map_custom.html")

restaurant_map.save(output_path)

print(f"  Map saved to: {output_path}")
print("\n" + "=" * 60)
print("  SCRIPT COMPLETE!")
print("=" * 60)
print(f"\nTo view your map:")
print(f"  1. Right-click '{output_path}' in VS Code")
print(f"  2. Select 'Open with Live Server' OR open it in your web browser")
print(f"\nCompare this map side-by-side with your Script 2 output:")
print(f"  data/lenzieswholunchanddinner_map_basic.html   ← plain OpenStreetMap")
print(f"  data/lenzieswholunchanddinner_map_custom.html  ← YOUR custom Mapbox style")
print(f"\nThis file is ready to include in your portfolio!")
