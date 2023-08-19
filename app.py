import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("URL Statistics Finder")

url = st.text_input("Enter a URL:")

def fetch_stats_from_google(url):
    # This function will fetch the top 10 search results from Google for the given URL.
    # Note: This is a basic example and might not work for all URLs.
    GOOGLE_SEARCH_URL = "https://www.google.com/search?q=" + url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(GOOGLE_SEARCH_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    search_results = soup.find_all("div", class_="tF2Cxc", limit=10)
    stats = []
    for result in search_results:
        title = result.find("h3", class_="LC20lb DKV0Md").text
        link = result.find("a")["href"]
        stats.append({"stat": title, "link": link})
    return stats

if url:
    stats = fetch_stats_from_google(url)
    for s in stats:
        st.write(f"Stat: {s['stat']}")
        st.write(f"Link: {s['link']}")
        st.write(f"Example Usage: {s['stat']} [source]({s['link']})")
