import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Load secrets
secrets = st.secrets["secrets"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI with your API key
openai.api_key = OPENAI_API_KEY

def extract_h1_or_title(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    h1_heading = soup.find('h1').text.strip() if soup.find('h1') else None
    if not h1_heading:
        h1_heading = soup.title.string if soup.title else None

    return h1_heading

def generate_statistic_search_queries(topic):
    prompt = f"For the topic '{topic}', generate 10 search queries that someone might use to find statistics related to it:"
    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=150,
      n=1,
      stop=None,
      temperature=0.5
    )
    queries = response.choices[0].text.strip().split("\n")
    return queries


# Streamlit UI
st.title("Statfinder")
url = st.text_input("Enter a URL:")

if url:
    topic = extract_h1_or_title(url)
    if topic:
        queries = generate_statistic_search_queries(topic)
        st.subheader(f"10 Search Queries for Finding Statistics on '{topic}':")
        for query in queries:
            st.write(query)
    else:
        st.write("No h1 heading or title found on the page.")
