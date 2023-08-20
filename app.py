import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Load secrets
secrets = st.secrets["secrets"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def extract_headings(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    headings = [tag.text.strip() for tag in soup.find_all(['h1', 'h2', 'h3'])]
    return headings

def rank_headings_for_statistics(headings):
    prompt = "Rank the following headings based on their relevance for adding a statistic from a reputable source:\n"
    for idx, heading in enumerate(headings):
        prompt += f"{idx + 1}. {heading}\n"

    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=500,
      n=1,
      stop=None,
      temperature=0.5
    )

    ranked_output = response.choices[0].text.strip().split("\n")
    # Extract the original headings from the ranked list
    ranked_headings = [headings[int(line.split('.')[0]) - 1] for line in ranked_output if line.split('.')[0].isdigit()]

    return ranked_headings[:10]


st.title("Top 10 Headings for Statistics")

# User input
url = st.text_input("Enter a URL:")

if url:
    headings = extract_headings(url)
    top_headings = rank_headings_for_statistics(headings)
    st.write("Top 10 Headings for Adding Statistics:")
    for heading in top_headings:
        st.write(heading)
