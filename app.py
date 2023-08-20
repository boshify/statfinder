import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from urllib.parse import urlparse

# Set up the OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set up the Google Custom Search API credentials
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["CSE_ID"]

def extract_content_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    content = ' '.join([p.text for p in paragraphs])
    return content

def summarize_text_with_gpt(text):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Summarize the following text:\n\n{text}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

def generate_queries_with_gpt(text):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Generate 5 statistical queries based on the following summary:\n\n{text}",
        max_tokens=150,
        n=5
    )
    return [choice.text.strip() for choice in response.choices]

def fetch_statistics(queries):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    results = []
    for query in queries:
        result = service.cse().list(q=query, cx=CSE_ID).execute()
        if 'items' in result:
            for item in result['items']:
                results.append({
                    'title': item['title'],
                    'link': item['link']
                })
    # Ensure unique sources
    unique_links = set()
    unique_stats = []
    for stat in results:
        if stat['link'] not in unique_links:
            unique_links.add(stat['link'])
            unique_stats.append(stat)
    return unique_stats[:10]  # Limit to 10 statistics

def get_trust_score(stat_title):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Rate the trustworthiness of the following statistic on a scale of 1 to 10:\n\n{stat_title}\n\n",
        max_tokens=5
    )
    score = response.choices[0].text.strip()
    return f"{score}/10"

def generate_example_use(stat_title, stat_link):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Create a natural sentence using the following statistic:\n\n{stat_title}\n\n",
        max_tokens=100
    )
    sentence = response.choices[0].text.strip()
    return f"{sentence} [source]({stat_link})"

# Streamlit UI
st.title("URL Statistics Enhancer")
url = st.text_input("Insert the URL you want to enhance with statistics:")

if url:
    st.write("URL provided:", url)

    # Extract and summarize the content
    extracted_content = extract_content_from_url(url)
    st.write("Extracted Content:", extracted_content)

    summarized_text = summarize_text_with_gpt(extracted_content)
    st.write("Summarized Text:", summarized_text)

    # Generate queries for statistics
    queries = generate_queries_with_gpt(summarized_text)
    st.write("Generated Queries:", queries)

    # Fetch statistics based on the queries
    stats = fetch_statistics(queries)
    st.write("Fetched Statistics:", stats)

    # Display the results
    st.write("Results:")
    st.write("Summarized Text:\n", summarized_text)
    for stat in stats:
        st.write("Statistic:", stat['title'])
        st.write("Statistic URL:", stat['link'])
        trust_score = get_trust_score(stat['title'])
        st.write("Trust Score:", trust_score)
        example_use = generate_example_use(stat['title'], stat['link'])
        st.write("Example Use:", example_use)
