# Import required libraries
from geopy.geocoders import Nominatim
import time
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium

# App title and introduction
st.markdown('<h1 style="text-align:center;"> GEOCODER 📍🗺️ </h1>', unsafe_allow_html=True)

# Brief app description
st.markdown(
  """
  <div style='font-size:1.1em;'>
  <b>Welcome!</b> This app lets you easily <span style='color:green;'>geocode</span> and <span style='color:orange;'>reverse geocode</span> addresses using <b>OpenStreetMap (OSM) Nominatim</b>.
  </div>
  """,
  unsafe_allow_html=True
)



# Initialize the geolocator with a custom user agent and timeout
geolocator = Nominatim(user_agent= 'favtai', timeout=10)


# Geocoding function: takes an address string and returns (latitude, longitude)
def geocoder(row_or_string):
  location = geolocator.geocode(row_or_string)
  time.sleep(1)  # Respect Nominatim's usage policy (1 request/sec)
  if location is None:
    return (None, None)  # Return a tuple of None values if not found
  else:
    return (location.latitude, location.longitude)



# Reverse geocoding function: takes a 'lat,lon' string and returns the address
def rev_geocoder(row_or_string):
  if row_or_string == "None,None" or row_or_string == 'nan,nan':
    return None
  location = geolocator.reverse(row_or_string)
  time.sleep(1)  # Respect Nominatim's usage policy (1 request/sec)
  if location is None:
    return None
  return location.address



# Toggle for switching between Geocode and Reverse Geocode modes
st.markdown('<span style="color:green; font-weight:bold; font-size:1.3em;">Toggle between <b>Geocode</b> and <b>Reverse Geocode</b>:</span>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 2])
col1.markdown("📍 <b>Geocode</b>", unsafe_allow_html=True)
on = col2.toggle("🔄 Switch Mode", value=False)
col3.markdown("🏠 <b>Reverse Geocode</b>", unsafe_allow_html=True)



# Main logic for Geocode mode
if not on:
  # Choose between single entry or batch mode
  input_method = st.radio("Select input method", ["Single Entry", "Batch (CSV Upload)"])
  if input_method == "Single Entry":
    # Single address input
    address = st.text_input("Enter an address:")
    if st.button("Geocode"):
      lat, lon = geocoder(address)
      if lat and lon:
        st.success(f"Latitude: {lat}, Longitude: {lon}")

        # Show result on a Folium map
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], tooltip=str.title(address)).add_to(m)
        folium_static(m, width=700, height=500)
      else:
        st.error("Address could not be geocoded.")
  else:
    # Batch geocoding from CSV
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
      df = pd.read_csv(uploaded_file)
      st.subheader("Preview of uploaded data:")
      st.dataframe(df.head())
      cols = [None] + df.columns.tolist()
      col = st.selectbox("Select address column", cols)
      if col is None:
        st.warning("Please select an address column.")
        st.stop()
      else:
        if st.button("Geocode"):
          st.text("Processing...")
          st.info("Note: OSM Nominatim Geocoding usage is limited to 1 request per second, Please Wait...")
          # Apply geocoding to the selected column
          df[['Latitude', 'Longitude']] = df[col].apply(geocoder).apply(pd.Series)
          st.dataframe(df)
          st.download_button(
            label="Download Results",
            data=df.to_csv(index=False),
            file_name='geocoded_results.csv',
            mime='text/csv'
          )


# Main logic for Reverse Geocode mode
else:
  # Choose between single entry or batch mode
  input_method = st.radio("Select input method", ["Single Entry", "Batch (CSV Upload)"])
  if input_method == "Single Entry":
    # Single coordinate input
    col1, col2 = st.columns(2)
    lat = col1.number_input("Latitude", format="%.6f")   
    lon = col2.number_input("Longitude", format="%.6f")
    if st.button("Reverse Geocode"):
      coord_str = f"{lat},{lon}"
      address = rev_geocoder(coord_str)
      if address:
        st.success(f"Address =>> {address}")
        # Show result on a Folium map
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], tooltip=str.title(address)).add_to(m)
        folium_static(m, width=700, height=500)
      else:
        st.error("Coordinates could not be reverse geocoded.")
  else:
    # Batch reverse geocoding from CSV
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
      df = pd.read_csv(uploaded_file)
      st.subheader("Preview of uploaded data:")
      st.dataframe(df.head())
      cols = [None] + df.columns.tolist()
      col1, col2 = st.columns(2)
      lat_col = col1.selectbox("Select Latitude column", cols)
      lon_col = col2.selectbox("Select Longitude column", cols)
      if lat_col is None or lon_col is None:
        st.warning("Please select both Latitude and Longitude columns.")
        st.stop()
      elif lat_col == lon_col:
        st.warning("Latitude and Longitude columns cannot be the same.")
        st.stop()
      else:
        if st.button("Reverse Geocode"):
          st.text("Processing...")
          st.info("Note: OSM Nominatim Geocoding usage is limited to 1 request per second, Please Wait...")
          # Apply reverse geocoding to the selected columns
          df['address'] = df[[lat_col, lon_col]].apply(lambda row: rev_geocoder(f"{row[lat_col]},{row[lon_col]}"), axis=1)
          st.dataframe(df)
          st.download_button(
            label="Download Results",
            data=df.to_csv(index=False),
            file_name='reverse_geocoded_results.csv',
            mime='text/csv'
          )


# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("Made with ❤️ by [Favour Taiwo](https://www.linkedin.com/in/favour-taiwo-57232023a/) with special thanks to" \
            " [Ujaval Gandhi](https://www.linkedin.com/in/spatialthoughts/) for his tutorials")