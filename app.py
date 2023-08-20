import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

# Set up the OpenAI API key
openai.api_key = st.secrets["secrets"]["OPENAI_API_KEY"]

# Set up the Google Custom Search API credentials
GOOGLE_API_KEY = st.secrets["secrets"]["GOOGLE_API_KEY"]
CSE_ID = st.secrets["secrets"]["CSE_ID"]

def extract_content_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([p.text for p in paragraphs])
        return content
    except Exception as e:
        st.write(f"Error in extracting content: {e}")
        return ""

def summarize_text_with_gpt(text):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Summarize the following text:\n\n{text}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.write(f"Error in summarizing text: {e}")
        return ""

def generate_queries_with_gpt(text):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Generate 5 statistical queries based on the following summary:\n\n{text}",
            max_tokens=150,
            n=5
        )
        return [choice.text.strip() for choice in response.choices]
    except Exception as e:
        st.write(f"Error in generating queries: {e}")
        return []

def fetch_statistics(queries):
    try:
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
        return results
    except Exception as e:
        st.write(f"Error in fetching statistics: {e}")
        return []

def generate_trust_score_with_gpt(statistic_title):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"How trustworthy is the following statistic title: \"{statistic_title}\"? Rate from 1 to 10.",
            max_tokens=10
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.write(f"Error in generating trust score: {e}")
        return "Error"

def generate_example_use_with_gpt(statistic_title, statistic_url):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Create a natural sentence using the following statistic title: \"{statistic_title}\" and its source: \"{statistic_url}\".",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.write(f"Error in generating example use: {e}")
        return "Error"

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

    # Display the results
    st.write("Results:")
    for stat in stats:
        trust_score = generate_trust_score_with_gpt(stat['title'])
        example_use = generate_example_use_with_gpt(stat['title'], stat['link'])
        
        st.write("Statistic:", stat['title'])
        st.write("Statistic URL:", stat['link'])
        st.write("Trust Score:", trust_score)
        st.write("Example Use:", example_use)
