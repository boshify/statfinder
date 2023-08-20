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

def generate_statistic_keywords(topic):
    prompt = f"Given the topic '{topic}', list 10 unique ideas for search queries someone would use to find statistics specific to the h1/page title."
    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=150,
      n=1,
      stop=None,
      temperature=0.5
    )
    keywords = response.choices[0].text.strip().split("\n")
    return keywords

# Streamlit UI
st.title("Statfinder")
url = st.text_input("Enter a URL:")

if url:
    topic = extract_h1_or_title(url)
    if topic:
        keywords = generate_statistic_keywords(topic)
        st.subheader(f"10 Ideas for Statistic searches for '{topic}':")
        for keyword in keywords:
            st.write(keyword)
    else:
        st.write("No h1 heading or title found on the page.")
