import streamlit as st
from pymongo import MongoClient
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import plotly.express as px

adsense_script = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5836320764804844"
     crossorigin="anonymous"></script>
"""

# Add the meta tag to the Streamlit app
st.markdown(adsense_script , unsafe_allow_html=True)
# MongoDB connection
client = MongoClient('mongodb+srv://reader:Rb07Blz8WxjR37Ut@cluster0.2kwup.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['Job']
collection = db['jobs']

# Streamlit app
st.title('Jobs Distribution')

# Input for sample size
sample_size = st.number_input('Enter sample size:', min_value=1, max_value=100000, value=1000, step=1000)

# Create a selectbox widget for country selection
countries = collection.distinct('sourceCC')

# Create a multiselect widget for country selection
selected_countries = st.multiselect('Select countries:',countries)

# Query to fetch data based on selected country
if selected_countries:
    query = {"sourceCC": {"$in":selected_countries}}
else:
    query = {}

cursor = collection.aggregate([
    {"$match": query},
    {
        '$match': {
            'orgAddress.geoPoint': {
                '$ne': None
            }
        }
    },
    {"$project": {"_id": 0, "lat": "$orgAddress.geoPoint.lat", "lng": "$orgAddress.geoPoint.lng","label":"$name" ,"country": "$sourceCC"}},
    {"$sample": {"size": sample_size}}
])

# Convert cursor to DataFrame
data = list(cursor)
df = pd.DataFrame(data)

#col1, col2 = st.columns(2)

st.subheader("MAP")
# Create a folium map centered around a general location
m = folium.Map(location=[20, 0], zoom_start=2)

# Add points to the map
marker_cluster = MarkerCluster().add_to(m)
for i, row in df.iterrows():
    folium.Marker(location=[row['lat'], row['lng']],popup=[row['label'],row['country']]).add_to(marker_cluster)

# Display the map in Streamlit
folium_static(m)

st.subheader("Country Ratio Pie Chart")
if not df.empty: 
        country_counts = df['country'].value_counts().reset_index()
        country_counts.columns = ['country', 'count']
        fig = px.pie(country_counts, values='count', names='country', title='Country Distribution')
        st.plotly_chart(fig, use_container_width=True)
else:
        st.write("No data to display in pie chart")
