import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Load secrets
secrets = st.secrets["secrets"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI with your API key
openai.api_key = OPENAI_API_KEY

def extract_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting content: paragraphs, headings, and list items
    contents = [tag.text.strip() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']) if len(tag.text.split()) > 5]  # Filter short content
    return contents

def suitability_score_for_statistic(content):
    prompt = f"On a scale of 1 to 10, rate the suitability of the content for adding a statistic: '{content}'"
    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=5,
      n=1,
      stop=None,
      temperature=0.5
    )
    score = response.choices[0].text.strip()
    try:
        return int(score)
    except ValueError:
        return 0

def rank_content_for_statistics(contents):
    scored_contents = [(content, suitability_score_for_statistic(content)) for content in contents]
    sorted_scored_contents = sorted(scored_contents, key=lambda x: x[1], reverse=True)
    top_contents = [item[0] for item in sorted_scored_contents[:10]]
    return top_contents

# Streamlit UI
st.title("Top 10 Content Placements for Statistics")
url = st.text_input("Enter a URL:")

if url:
    contents = extract_content(url)
    if contents:
        top_contents = rank_content_for_statistics(contents)
        st.subheader("Top 10 Contents Suitable for Statistics:")  
        for content in top_contents:
            st.write(content)
    else:
        st.write("No suitable content found on the page.")
