import streamlit as st

# Meta tag for Google AdSense verification
meta_tag = """
<head>
    <meta name="google-adsense-account" content="ca-pub-5836320764804844">
</head>
"""

# Add the meta tag to the Streamlit app
st.markdown(meta_tag, unsafe_allow_html=True)

# Example content for your app
st.title("Welcome to My Streamlit App")
st.write("Here is some content with Google Ads integration.")
