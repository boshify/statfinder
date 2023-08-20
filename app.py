import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup

# Initialize OpenAI API
try:
    openai.api_key = st.secrets["openai_api_key"]
except KeyError:
    st.error("Please set up the OpenAI API key in your secrets.")

# Streamlit Layout
st.title("URL Statistics Enhancer")
url = st.text_input("Insert the URL you want to enhance with statistics:")

def extract_content_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([para.text for para in paragraphs])
        return text
    except:
        return "Unable to extract content from the provided URL."

def summarize_text_with_gpt(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Summarize the following text:\n\n{text}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in summarize_text_with_gpt: {str(e)}"

def generate_queries_with_gpt(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Generate 10 questions based on the following text that could be enhanced with statistics:\n\n{text}",
            max_tokens=200,
            n=10,
            stop=None
        )
        queries = [choice.text.strip() for choice in response.choices]
        return queries
    except Exception as e:
        return f"Error in generate_queries_with_gpt: {str(e)}"

def fetch_stat_from_google(query):
    try:
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query} statistics&key={st.secrets['google_api_key']}&cx={st.secrets['google_cse_id']}"
        response = requests.get(search_url).json()
        stats = []
        for item in response['items']:
            stats.append({
                "stat": item['title'],
                "link": item['link']
            })
        return stats
    except:
        return []

if url:
    extracted_text = extract_content_from_url(url)
    st.write("Extracted Text:")
    st.write(extracted_text)
    
    summarized_text = summarize_text_with_gpt(extracted_text)
    st.write("Summarized Text:")
    st.write(summarized_text)
    
    queries = generate_queries_with_gpt(summarized_text)
    st.write("Generated Queries:")
    st.write(queries)
    
    for query in queries:
        stats = fetch_stat_from_google(query)
        for stat in stats:
            st.write(f"Statistic: {stat['stat']}")
            st.write(f"Statistic URL: {stat['link']}")
            st.write(f"Example Use: . According to a recent study, {query}. [source]({stat['link']})")
            st.write("------")
