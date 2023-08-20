import streamlit as st
import requests
from googleapiclient.discovery import build
import openai

# Load secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def google_search(query, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, **kwargs).execute()
    return res['items']

def summarize_with_openai(text):
    response = openai.Completion.create(
      engine="davinci",
      prompt=f"Summarize the following search results:\n{text}",
      max_tokens=150
    )
    return response.choices[0].text.strip()

st.title("Google Search and Summary App")

# User input
query = st.text_input("Enter your search query:")

if query:
    # Google Search
    results = google_search(query, GOOGLE_API_KEY, CSE_ID)
    search_results = "\n".join([result["title"] + ": " + result["link"] for result in results])
    st.write(search_results)

    # Summarize with OpenAI
    summary = summarize_with_openai(search_results)
    st.subheader("Summary:")
    st.write(summary)
