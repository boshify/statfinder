import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup

# Set up the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Google Search function
def google_search(query, api_key, cse_id, **kwargs):
    service_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
    }
    params.update(kwargs)
    response = requests.get(service_url, params=params)
    response.raise_for_status()
    return response.json()['items']

# Extract content from URL
def extract_content_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.text for para in paragraphs])
        return content
    except Exception as e:
        st.error(f"Unable to extract content from the provided URL. {e}")
        return None

# Summarize text with GPT-3
def summarize_text_with_gpt(text):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Summarize the following text:\n\n{text}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"Error in summarize_text_with_gpt: {e}")
        return None

# Generate queries with GPT-3
def generate_queries_with_gpt(text):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Generate 10 search queries based on the following text to find relevant statistics:\n\n{text}",
            max_tokens=200,
            n=10,
            stop=["\n"]
        )
        return [choice.text.strip() for choice in response.choices]
    except Exception as e:
        st.error(f"Error in generate_queries_with_gpt: {e}")
        return []

# Main app
st.title("URL Statistics Enhancer")

# Input URL
url = st.text_input("Insert the URL you want to enhance with statistics:")

if url:
    # Extract content
    content = extract_content_from_url(url)
    if content:
        # Summarize content
        summarized_text = summarize_text_with_gpt(content)
        st.write("Summarized Text:\n")
        st.write(summarized_text)

        # Generate search queries
        queries = generate_queries_with_gpt(summarized_text)
        for query in queries:
            try:
                # Search Google for statistics
                results = google_search(query, st.secrets["GOOGLE_API_KEY"], st.secrets["CSE_ID"], num=1)
                for result in results:
                    st.write(f"Statistic: {result['title']}\n")
                    st.write(f"Statistic URL: {result['link']}\n")
                    st.write(f"Example Use: {summarized_text} [source]({result['link']})\n")
            except Exception as e:
                st.error(f"Error while searching for statistics: {e}")

