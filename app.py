import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("URL Statistics Finder")

url = st.text_input("Enter a URL:")

def fetch_stats_from_google(query):
    stats = []
    try:
        GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": "YOUR_API_KEY",  # Replace with your API key
            "cx": "YOUR_CSE_ID",   # Replace with your Custom Search Engine ID
            "q": query
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


if url:
    stats = fetch_stats_from_google(url)
    for s in stats:
        st.write(f"Stat: {s['stat']}")
        st.write(f"Link: {s['link']}")
        st.write(f"Example Usage: {s['stat']} [source]({s['link']})")
