import streamlit as st
import requests
import json

# Set Streamlit page configuration
st.set_page_config(
    page_title="URL Statistics Finder",
    page_icon="🔍",
    layout="wide",
)

# Your site, API key, and Custom Search Engine ID
api_key = st.text_input("Enter your Google API Key")
cse_id = st.text_input("Enter your Custom Search Engine ID")

def fetch_stats_from_google(query, api_key, cse_id):
    stats = []
    try:
        GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': api_key,
            'cx': cse_id,
        }
        response = requests.get(GOOGLE_CSE_URL, params=params)
        data = response.json()
        
        for item in data.get("items", []):
            title = item["title"]
            link = item["link"]
            stats.append({"stat": title, "link": link})
    except Exception as e:
        stats.append({"stat": f"Error: {str(e)}", "link": "#"})
    return stats

# Streamlit layout and components
c30, c31 = st.columns([10.5, 1])

with c30:
    st.title("URL Statistics Finder")

with st.expander("ℹ - About the App"):
    st.write(
        """
- This application aims to find relevant statistics about the topic of a given URL.
- To do so, simply enter your Google API Key, Custom Search Engine ID, and the URL you're interested in.
- The app will provide you with a list of relevant statistics and links.
	    """
    )

st.markdown("----")

c1, c2 = st.columns([1.5, 4])

with c1:
    url = st.text_input('Insert the URL you want to search for statistics:')
    
    if url:
        stats = fetch_stats_from_google(url, api_key, cse_id)

        with c2:
            for s in stats:
                if "Error" in s['stat']:
                    st.error(s['stat'])  # Display the error message
                else:
                    st.write(f"Stat: {s['stat']}")
                    st.write(f"Link: {s['link']}")
                    st.write(f"Example Usage: {s['stat']} [source]({s['link']})")

st.markdown("----")
