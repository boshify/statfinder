import streamlit as st
import requests
import json
import openai
from bs4 import BeautifulSoup
import re

# Set Streamlit page configuration
st.set_page_config(
    page_title="URL Statistics Enhancer",
    page_icon="🔍",
    layout="wide",
)

# Fetch secrets
API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["CSE_ID"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text from H1 to start of footer
        h1 = soup.find('h1')
        footer = soup.find('footer')
        if h1 and footer:
            content = ''.join(str(item) for item in h1.find_all_next() if item != footer)
            return BeautifulSoup(content, 'html.parser').get_text()
        return None
    except:
        return None

def generate_queries_with_gpt(text):
    try:
        response = openai.Completion.create(
          engine="gpt-3.5-turbo",
          prompt=f"From the following content, generate 10 sentences where a statistic should be added:\n\n{text}",
          max_tokens=500,
          n=1,
          stop=None,
          temperature=0.7
        )
        queries = response.choices[0].text.strip().split('\n')
        return queries
    except:
        return []

def fetch_stat_from_google(query):
    try:
        GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': f"statistics about {query}",
            'key': API_KEY,
            'cx': CSE_ID,
        }
        response = requests.get(GOOGLE_CSE_URL, params=params)
        data = response.json()
        if data.get("items"):
            for item in data["items"]:
                # Ensure the statistic contains a number, percent, or amount
                if re.search(r'\d+|\d+\.\d+|\d+%', item["title"]):
                    return {"stat": item["title"], "link": item["link"]}
        return None
    except:
        return None

# Streamlit layout and components
c30, c31 = st.columns([10.5, 1])

with c30:
    st.title("URL Statistics Enhancer")

st.markdown("----")

url = st.text_input('Insert the URL you want to enhance with statistics:')

if url:
    text = extract_text_from_url(url)
    if text:
        queries = generate_queries_with_gpt(text)
        for query in queries:
            stat_data = fetch_stat_from_google(query)
            if stat_data:
                st.markdown(f"**Statistic:** {stat_data['stat']}")
                st.markdown(f"**Statistic URL:** [{stat_data['link']}]({stat_data['link']})")
                st.markdown(f"**Example Use:** `{query} [source]({stat_data['link']})`")
                st.markdown("---")
    else:
        st.error("Unable to extract content from the provided URL.")

st.markdown("----")
