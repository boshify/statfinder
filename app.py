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
        # Your headers here...
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting content, focusing on paragraphs
    paragraphs = [p.text.strip() for p in soup.find_all('p') if len(p.text.split()) > 5]  # Filter short paragraphs
    return paragraphs

def is_suitable_for_statistic(content):
    prompt = f"Does the content '{content}' seem like a good place to add a statistic? (Yes/No)"
    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      max_tokens=5,
      n=1,
      stop=None,
      temperature=0.5
    )
    return response.choices[0].text.strip().lower() == "yes"

def rank_content_for_statistics(contents):
    suitable_contents = [content for content in contents if is_suitable_for_statistic(content)]
    return suitable_contents[:10]  # Returns top 10 suitable contents

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
