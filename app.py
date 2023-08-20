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
    prompt = "Given the following headings from an article, rank the top 10 headings where adding a statistic from a reputable source would be most beneficial:\n"
    for idx, heading in enumerate(headings):
        prompt += f"{idx + 1}. {heading}\n"
    prompt += "\nRank the headings by number (e.g., 1, 3, 5):"

    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=50,  # Limiting the number of tokens
      n=1,
      stop=None,
      temperature=0.5
    )

    st.write("Model's Output:")  # Debugging line
    st.write(response.choices[0].text.strip())  # Debugging line

    ranked_output = response.choices[0].text.strip().split(",")  # Assuming the model returns a comma-separated list of numbers
    ranked_headings = []
    for index_str in ranked_output:
        index_str = index_str.strip()
        if index_str.isdigit():
            index = int(index_str) - 1
            if 0 <= index < len(headings):
                ranked_headings.append(headings[index])

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
