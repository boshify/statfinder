import streamlit as st
import requests
import openai
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

# Accessing the secrets
GOOGLE_API_KEY = st.secrets.GOOGLE_API_KEY
CSE_ID = st.secrets.CSE_ID
OPENAI_API_KEY = st.secrets.OPENAI_API_KEY


# Extract key points from text using OpenAI
def extract_key_points_from_text(text):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Summarize the following article into 5 key points:\n{text}",
        max_tokens=150
    )
    return response.choices[0].text.strip().split('\n')

# Fetch statistics related to the key points
def fetch_statistics(query):
    service = build("customsearch", "v1", developerKey=st.secrets["GOOGLE_API_KEY"])
    res = service.cse().list(q=query, cx=st.secrets["CSE_ID"], num=1).execute()
    return res['items'][0] if 'items' in res else None

# Streamlit UI
st.title("URL Statistics Enhancer")

# Input URL
url = st.text_input("Insert the URL you want to enhance with statistics:")

if url:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    article_text = ' '.join([p.get_text() for p in paragraphs])
    
    key_points = extract_key_points_from_text(article_text)
    
    for point in key_points:
        st.write(f"Summarized Text:\n\n{point}\n")
        
        # Fetch statistics
        statistic = fetch_statistics(point)
        if statistic:
            st.write(f"Statistic: {statistic['title']}")
            st.write(f"Statistic URL: {statistic['link']}")
            st.write(f"Example Use: {point}\n")
        else:
            st.write("No relevant statistics found for this point.\n")
