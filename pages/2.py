import streamlit as st

adsense_script = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5836320764804844"
     crossorigin="anonymous"></script>
"""

# Add the meta tag to the Streamlit app
st.markdown(adsense_script , unsafe_allow_html=True)

# Example content for your app
st.title("Welcome to My Streamlit App")
st.write("Here is some content with Google Ads integration.")
