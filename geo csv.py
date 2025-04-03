import pandas as pd
import folium
from folium.plugins import AntPath
import streamlit as st
from streamlit_folium import st_folium

# Load the CSV file
csv_file = r"C:\Users\A509159\Downloads\geomapping data.csv"
df = pd.read_csv(csv_file)

def parse_coordinates(coord_str):
    if pd.notna(coord_str) and ',' in coord_str.strip():  # Ensure value is not NaN and contains a comma
        try:
            lon, lat = map(float, coord_str.split(','))
            return lat, lon  # Return as (lat, lon)
        except ValueError:  # Handle cases where conversion fails
            return None
    return None 

# Function to get coordinates for a specific tier1_name
def get_coordinates_for_tier1(tier1_name):
    data = []
    for _, row in df.iterrows():
        # Parse coordinates for each tier
        tier1_coord = parse_coordinates(row['tier1_geometry_coordinates'])
        tier2_coord = parse_coordinates(row['tier2_geometry_coordinates'])
        tier3_coord = parse_coordinates(row['tier3_geometry_coordinates'])

        # Ensure tier1 and tier2 coordinates are valid, tier3 can be None
        if tier1_coord and tier2_coord and row['tier1_name'] == tier1_name:
            data.append([tier1_coord, tier2_coord, tier3_coord])
    
    return data

# Streamlit App UI
st.set_page_config(layout="wide")
st.title("Geomapping Visualization")
st.write("Enter the company name to visualize tier 1 coordinates.")

# User input for tier1_name
user_specified_tier1_name = st.text_input("Enter the company name for tracking:", "")

if user_specified_tier1_name:
    # Fetch coordinates for the specified tier1_name
    coordinates_for_tier1 = get_coordinates_for_tier1(user_specified_tier1_name)

    if not coordinates_for_tier1:
        st.warning(f"No data found for {user_specified_tier1_name}.")
    else:
        # Initialize lists for latitudes and longitudes
        latitudes = []
        longitudes = []

        # Loop through the coordinates and append valid points
        for row in coordinates_for_tier1:
            for point in row:
                if point:  # Ensure point is not None
                    latitudes.append(point[0])  # Latitude is the first value in the tuple
                    longitudes.append(point[1])  # Longitude is the second value in the tuple

        # Calculate the average latitude and longitude to find the center
        center_lat = sum(latitudes) / len(latitudes) if latitudes else 0
        center_lon = sum(longitudes) / len(longitudes) if longitudes else 0

        # Create a Folium map centered at the calculated average location
        m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

        # Marker colors for each tier
        marker_colors = {
            0: "red",     # tier1
            1: "green",   # tier2
            2: "blue"     # tier3
        }

        # Iterate through each row in the data and plot points and AntPaths
        for row in coordinates_for_tier1:
            for i in range(len(row)):
                point = row[i]
                if point:  # Ensure the point is valid
                    # Add a marker with the corresponding color
                    folium.Marker(
                        location=point,
                        tooltip=f"Tier{i + 1} Point",
                        icon=folium.Icon(color=marker_colors.get(i, "gray"))
                    ).add_to(m)

            # Add AntPath for animations from tier3 -> tier2 -> tier1
            path = [point for point in reversed(row) if point]  # Reverse the order of points
            if len(path) > 1:
                AntPath(
                    locations=path,
                    color="purple",
                    weight=2.5,
                    opacity=0.8,
                    dash_array=[10, 20],  # Pattern of dashes
                    delay=400  # Delay for animation in milliseconds
                ).add_to(m)

        # Display the map in Streamlit
        st_folium(m, width=1920, height=1080)




