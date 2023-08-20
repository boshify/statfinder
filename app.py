import streamlit as st
import requests
import openai
from bs4 import BeautifulSoup
import re

# Set Streamlit page configuration
st.set_page_config(
    page_title="URL Statistics Enhancer",
    page_icon="🔍",
    layout="wide",
)

# Fetch secrets
API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["CSE_ID"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

def extract_text_from_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract text from H1 to start of footer
    h1 = soup.find('h1')
    footer = soup.find('footer')
    if h1 and footer:
        content = ''.join(str(item) for item in h1.find_all_next() if item != footer)
        return BeautifulSoup(content, 'html.parser').get_text()
    return None

def summarize_text_with_gpt(text):
    try:
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following content:\n\n{text}"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Error in summarize_text_with_gpt: {e}")
        return text

def generate_queries_with_gpt(text):
    try:
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"From the summarized content, generate 10 sentences where a statistic should be added:\n\n{text}"}
            ]
        )
        queries = response.choices[0].message['content'].strip().split('\n')
        return queries
    except Exception as e:
        st.error(f"Error in generate_queries_with_gpt: {e}")
        return []

def fetch_stat_from_google(query):
    GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': f"statistics about {query}",
        'key': API_KEY,
        'cx': CSE_ID,
    }
    response = requests.get(GOOGLE_CSE_URL, params=params)
    data = response.json()
    results = []
    if data.get("items"):
        for item in data["items"]:
            # Ensure the statistic contains a number
            if any(char.isdigit() for char in item["snippet"]):
                results.append({
                    "stat": item["snippet"],
                    "link": item["link"]
                })
    return results

def get_trust_score_with_gpt(stat):
    try:
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Score this information from 1-10 on a scale of believability. 10 being highly believable and 1 being hardest to believe:\n\n{stat}"}
            ]
        )
        score = int(response.choices[0].message['content'].strip())
        return score
    except Exception as e:
        st.error(f"Error in get_trust_score_with_gpt: {e}")
        return 5  # Default score

# Streamlit layout and components
c30, c31 = st.columns([10.5, 1])

with c30:
    st.title("URL Statistics Enhancer")

st.markdown("----")

url = st.text_input('Insert the URL you want to enhance with statistics:')

if url:
    text = extract_text_from_url(url)
    if text:
        summarized_text = summarize_text_with_gpt(text[:2000])  # Limiting the text to the first 2000 characters
        st.write(f"**Summarized Text:**\n\n{summarized_text[:500]}...")  # Displaying the first 500 characters
        st.markdown("---")
        queries = generate_queries_with_gpt(summarized_text)
        displayed_links = set()  # To avoid repeated websites
        count = 0
        for query in queries:
            stats_data = fetch_stat_from_google(query)
            for stat_data in stats_data:
                if stat_data["link"] not in displayed_links:
                    displayed_links.add(stat_data["link"])
                    trust_score = get_trust_score_with_gpt(stat_data["stat"])
                    st.markdown(f"**Statistic:** {stat_data['stat']}")
                    st.markdown(f"**Statistic URL:** [{stat_data['link']}]({stat_data['link']})")
                    st.markdown(f"**Trust Score:** {trust_score}/10")
                    example_use = re.sub(r'\d+', '', query)  # Remove numbers
                    st.markdown(f"**Example Use:** `{example_use} [source]({stat_data['link']})`")
                    st.markdown("---")
                    count += 1
                    if count >= 10:
                        break
            if count >= 10:
                break
    else:
        st.error("Unable to extract content from the provided URL.")

st.markdown("----")
