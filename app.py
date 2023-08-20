import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup

# Initialize OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Streamlit Layout
st.title("URL Statistics Enhancer")
url = st.text_input("Insert the URL you want to enhance with statistics:")

def extract_content_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.text for para in paragraphs])
        return text
    except:
        st.error("Unable to extract content from the provided URL.")
        return ""

def summarize_text_with_gpt(text):
    try:
        response = openai.Completion.create(
          model="gpt-3.5-turbo",
          prompt=f"Summarize the following text:\n\n{text}",
          max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"Error in summarize_text_with_gpt: {e}")
        return ""

def generate_queries_with_gpt(text):
    try:
        response = openai.Completion.create(
          model="gpt-3.5-turbo",
          prompt=f"From the following text, generate 10 queries where statistics might be useful:\n\n{text}",
          max_tokens=200
        )
        queries = response.choices[0].text.strip().split('\n')
        return queries
    except Exception as e:
        st.error(f"Error in generate_queries_with_gpt: {e}")
        return []

def fetch_stat_from_google(query):
    try:
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query} statistics&key=YOUR_GOOGLE_API_KEY&cx=YOUR_CSE_ID"
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

def get_trust_score_with_gpt(stat):
    try:
        response = openai.Completion.create(
          model="gpt-3.5-turbo",
          prompt=f"On a scale of 1-10, score this information based on its believability. 10 being highly believable and 1 being least believable:\n\n{stat}",
          max_tokens=50
        )
        score = int(response.choices[0].text.strip().split()[0])
        return score
    except Exception as e:
        st.error(f"Error in get_trust_score_with_gpt: {e}")
        return 5

def generate_example_use_with_gpt(query, stat):
    try:
        response = openai.Completion.create(
          model="gpt-3.5-turbo",
          prompt=f"Generate a sentence using the following statistic related to {query}:\n\n{stat}",
          max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"Error in generate_example_use_with_gpt: {e}")
        return f"According to a recent study, {query} {stat}"

if url:
    extracted_text = extract_content_from_url(url)
    summarized_text = summarize_text_with_gpt(extracted_text)
    st.markdown(f"**Summarized Text:**\n\n{summarized_text}\n")
    queries = generate_queries_with_gpt(summarized_text)
    displayed_links = set()
    count = 0
    for query in queries:
        stats_data = fetch_stat_from_google(query)
        for stat_data in stats_data:
            if stat_data["link"] not in displayed_links:
                displayed_links.add(stat_data["link"])
                trust_score = get_trust_score_with_gpt(stat_data["stat"])
                example_use = generate_example_use_with_gpt(query, stat_data["stat"])
                st.markdown(f"**Statistic:** {stat_data['stat']}")
                st.markdown(f"**Statistic URL:** [{stat_data['link']}]({stat_data['link']})")
                st.markdown(f"**Trust Score:** {trust_score}/10")
                st.markdown(f"**Example Use:** `{example_use} [source]({stat_data['link']})`")
                st.markdown("---")
                count += 1
                if count >= 10:
                    break
        if count >= 10:
            break
