import streamlit as st

# Google AdSense script
adsense_script = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5836320764804844"
     crossorigin="anonymous"></script>
"""

# HTML container for the ad (Optional: you can define the ad size or placement here)
adsense_html = """
<!-- Example Ad Slot -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-5836320764804844"
     data-ad-slot="XXXXXXX"   <!-- Replace with your ad slot -->
     data-ad-format="auto"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""

# Add the script and the ad HTML to the app
st.markdown(adsense_script, unsafe_allow_html=True)
st.markdown(adsense_html, unsafe_allow_html=True)

# Example content for your app
st.title("Welcome to My Streamlit App")
st.write("Here is some content with Google Ads below.")
