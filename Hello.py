import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import plotly.express as px
import time
import numpy as np

st.set_page_config(page_title="Dashboard", layout="wide")
@st.cache_resource
def initialize_database_connection():
    # MongoDB connection
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Job']
    collection = db['jobs']
    return collection
collection = initialize_database_connection() 

# Query to fetch data based on filters (placeholder query)
query = {}
sample_size = 1000



# Sidebar for filters
st.sidebar.title("Filters")


# 1. Multi-selection for category
# Fetch distinct categories (Cached once per session)
@st.cache_data
def fetch_distinct_categories(_collection):
    categories = list(_collection.aggregate([
    {
        '$unwind': {
            'path': '$orgTags.CATEGORIES'
        }
    }, {
        '$match': {
            'orgTags.CATEGORIES': {
                '$ne': None
            }
        }
    }, {
        '$group': {
            '_id': '$orgTags.CATEGORIES', 
            'Count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'Count': -1
        }
    }, {
        '$limit': 30
    }, {
        '$group': {
            '_id': None, 
            'distinctCategories': {
                '$push': '$_id'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'distinctCategories': 1
        }
    }
    ]))[0]['distinctCategories']
    return categories

dist_categories= fetch_distinct_categories(collection)

selected_categories = st.sidebar.multiselect("Select Categories", dist_categories)

if selected_categories:
    query['Categories'] = {"$in": selected_categories}
else:
    query['Categories'] = {"$ne": {}}
# 2. Input for salary value
salary = st.sidebar.number_input("Enter Salary", min_value=0, step=1000)
if salary:
    query["salary_value"] = {"salary.value":{"$gte": salary}}
else:
    query["salary_value"] = {}


# 3. Multi-selection for country code
@st.cache_data
def fetch_distinct_countries(_collection):
    countries = list(collection.aggregate([
    {
        '$match': {
            'sourceCC': {
                '$ne': None
            }
        }
    }, {
        '$group': {
            '_id': '$sourceCC', 
            'Count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'Count': -1
        }
    }, {
        '$limit': 30
    }, {
        '$group': {
            '_id': None, 
            'distinct_countires': {
                '$push': '$_id'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'distinct_countires': 1
        }
    }
]))[0]['distinct_countires']
    return countries
countries = fetch_distinct_countries(collection)

# Create a multiselect widget for country selection
selected_countries = st.sidebar.multiselect('Select countries:',countries)

# Query to fetch data based on selected country
if selected_countries:
    query['country_codes'] = {"$in":selected_countries}
else:
    query['country_codes'] = {"$ne":None}


# 4. Text field for name search
name_search = st.sidebar.text_input("Name Search")

if name_search:
    query["name"] = {"name":{"$regex": name_search, "$options": "i"}}
else:
    query["name"] = {}
# 5. Multi-selection for job type
@st.cache_data
def fetch_distinct_job_types(_collection):
    job_types = list(_collection.aggregate([
    {
        '$match': {
            'position.workType': {
                '$ne': None
            }
        }
    }, {
        '$group': {
            '_id': '$position.workType', 
            'Count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'Count': -1
        }
    }, {
        '$limit': 50
    }, {
        '$group': {
            '_id': None, 
            'jobs_distinct': {
                '$push': '$_id'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'jobs_distinct': 1
        }
    }
]))[0]['jobs_distinct']
    return job_types
job_types = fetch_distinct_job_types(collection)
selected_job_types = st.sidebar.multiselect("Select Job Types", job_types)
if selected_job_types:
    query["job_type"] = {"$in": selected_job_types}
else:
    query["job_type"] = {"$ne":{}}


# 6. Date picker for date range
date_range = st.sidebar.date_input("Select Date Range", [])
if date_range and len(date_range) == 2:
    query["date"] = {"$and":[{"dateUploaded":{"$ne":None}},{"dateUploaded":{"$gte": datetime.combine(date_range[0], datetime.min.time()), "$lte": datetime.combine(date_range[1], datetime.max.time())}}]}
else:
    query["date"] = {}





cursor = collection.aggregate([

    {
        "$match": {"sourceCC":query['country_codes']}
    },
    {
         "$match": {"orgTags.CATEGORIES":query['Categories']}
    },
    {
         "$match": query["salary_value"]
    },
    {
         "$match": {"position.workType": query["job_type"]}
    },
    {
         "$match": query["name"]
    },
    {
         "$match": query["date"]
    },
    {
        "$limit":1000
    },
])
data = list(cursor)
df = pd.DataFrame(data)

# Calculate general information


num_documents = len(df)

# Main content
st.title('Dashboard')

# Display general information
st.markdown(f"**Number of Returned Documents:** {num_documents}")
st.write(df)
# Plot interactive linear histogram grouped by job types
st.subheader("General Informations-Job Types")
@st.cache_data
def plot_1_data(_collection):
    jobs_df = list(collection.aggregate([
    {
        "$group": {"_id": "$position.workType","count":{"$sum":1}}
    },
    {
        "$sort": {"count": -1}
    },
    {
        "$limit": 10
    }
    ]))
    return jobs_df


# Convert the result to a DataFrame
jobs_df = pd.DataFrame(plot_1_data(collection))

# Debugging: Output the DataFrame
st.write("Jobs DataFrame:", jobs_df)

# Plot interactive linear histogram grouped by job types
st.subheader("Interactive Linear Histogram Grouped by Job Types")
if not jobs_df.empty:
    fig = px.histogram(jobs_df, x="count", y="_id", color="_id", labels={'_id': 'Job Type', 'count': 'Count'}, marginal="rug")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No data available to plot the histogram")



@st.cache_data
def plot_2_data(_collection):
    uploaded_data = list(collection.aggregate([
    {
        "$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateUploaded"}},"count":{"$sum":1}}
    },
    {
        "$sort": {"_id": 1}
    }
    ]))
    return uploaded_data
Data_2 = pd.DataFrame(plot_2_data(collection))

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

# If data is available, animate the plot
if not Data_2.empty:
    chart = st.line_chart(Data_2[['count']].iloc[:1])

    for i in range(1, len(Data_2)):
        new_row = Data_2[['count']].iloc[i:i+1]
        chart.add_rows(new_row)
        progress_bar.progress(int((i + 1) / len(Data_2) * 100))
        status_text.text(f"{int((i + 1) / len(Data_2) * 100)}% Complete")
        time.sleep(0.1)

    progress_bar.empty()
else:
    st.write("No data available to plot")

# Re-run button to refresh the data and plot
st.button("Re-run")

@st.cache_data
def plot_3_data(_collection):
    uploaded_data = list(collection.aggregate([
    {
        "$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$dateUploaded"}},"count":{"$sum":1}}
    },
    {
        "$sort": {"count": -1}
    }
    ]))
    return uploaded_data
# Plot the data if available
data3 = pd.DataFrame(plot_3_data(collection))
if not df.empty:
    fig = px.bar(data3, x="_id", y="count", title="#Uploads/Day")
    fig.update_layout(xaxis_title='Date', yaxis_title='Count') 
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No data available to plot")



@st.cache_data
def plot_4_data(_collection):
    dt4 = list(_collection.aggregate([
    {
        '$group': {
            '_id': '$orgCompany.nameOrg', 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'count': -1
        }
    },
    {
        "$limit": 100
    }
]))
    return dt4

data4 = pd.DataFrame(plot_4_data(collection))
# Ensure column names are appropriate
data4.columns = ['Organization', 'Count']

# Convert the 'Organization' column to string to ensure compatibility
data4['Organization'] = data4['Organization'].astype(str)

# Create the interactive treemap
fig = px.treemap(data4, path=['Organization'], values='Count', color='Count',
                 color_continuous_scale='RdYlGn', title='Organization Count Treemap')

# Display the treemap in Streamlit
st.plotly_chart(fig)
#--------------------------------------------------------------------------------------------

@st.cache_data
def plot_5_Data(_collection):
    dt5 = list(_collection.aggregate([
    {
        '$group': {
            '_id': {
                'company': '$orgCompany.nameOrg', 
                'Country': '$sourceCC'
            }, 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'count': -1
        }
    }, {
        '$limit': 100
    }
]))
    return dt5

data5 = pd.DataFrame(plot_5_Data(collection))
# Flatten the nested '_id' field
data5 = pd.concat([data5['_id'].apply(pd.Series), data5['count']], axis=1)

# Ensure column names are appropriate
data5.columns = ['Organization', 'Country', 'Count']

# Create the interactive treemap
fig = px.treemap(data5, path=['Country', 'Organization'], values='Count', color='Count',
                 color_continuous_scale='RdYlGn', title='Organization Count Treemap by Country')

# Display the treemap in Streamlit
st.plotly_chart(fig)

#-------------------------------------------------------------------------------------------------------
@st.cache_data
def plot_6_Data(_collection):
    most_companies = list(_collection.aggregate([
        {
            "$group":{"_id":"$orgCompany.nameOrg", "count": {"$sum":1}}
        },
        {
            "$sort":{"count":-1} 
        },
        {
            "$limit":30
        },
        {
        '$group': {
            '_id': None, 
            'distinctCompanies': {
                '$push': '$_id'
            }
        }
    }, {
        '$project': {
            '_id': 0, 
            'distinctCompanies': 1
        }
    }
    ]))[0]['distinctCompanies']


    dt6 = list(_collection.aggregate([
    {
        '$unwind': {
            'path': '$orgTags.CATEGORIES'
        }
    }, {
        '$match': {
            'orgTags.CATEGORIES': {
                '$in': dist_categories
            }
        }
    }, {
        '$match': {
            'orgCompany.nameOrg': {
                '$in': most_companies
            }
        }
    }, {
        '$group': {
            '_id': {
                'company': '$orgCompany.nameOrg', 
                'Categories': '$orgTags.CATEGORIES'
            }, 
            'count': {
                '$sum': 1
            }
        }
    }
]))
    return dt6

# Fetch the data
data6 = pd.DataFrame(plot_6_Data(collection))

# Flatten the nested '_id' field
data6 = pd.concat([data6['_id'].apply(pd.Series), data6['count']], axis=1)

# Ensure column names are appropriate
data6.columns = ['Organization', 'Categories', 'count']

# Create the heatmap
heatmap_data = data6.pivot(index='Categories', columns='Organization', values='count')
fig = px.imshow(heatmap_data, labels=dict(x="Organization", y="Categories", color="count"),
                title="Heatmap of Organization and Categories",width=1200, height=1200)

# Display the heatmap in Streamlit
st.plotly_chart(fig)