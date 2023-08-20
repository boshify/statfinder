import streamlit as st
import requests
import openai
from bs4 import BeautifulSoup

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
        response = openai.Completion.create(
          model="gpt-3.5-turbo",
          prompt=f"Summarize the following content:\n\n{text}",
          max_tokens=1000,
          n=1,
          stop=None,
          temperature=0.7
        )
        return response.choices[0].text.strip()
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
    if data.get("items"):
        for item in data["items"]:
            # Ensure the statistic contains a number
            if any(char.isdigit() for char in item["title"]):
                return {"stat": item["title"], "link": item["link"]}
    return None

# Streamlit layout and components
c30, c31 = st.columns([10.5, 1])

with c30:
    st.title("URL Statistics Enhancer")

st.markdown("----")

url = st.text_input('Insert the URL you want to enhance with statistics:')

if url:
    text = extract_text_from_url(url)
    if text:
        summarized_text = summarize_text_with_gpt(text)
        st.write(f"Summarized Text: {summarized_text[:500]}...")  # Displaying the first 500 characters
        queries = generate_queries_with_gpt(summarized_text)
        for query in queries:
            stat_data = fetch_stat_from_google(query)
            if stat_data:
                st.markdown(f"**Statistic:** {stat_data['stat']}")
                st.markdown(f"**Statistic URL:** [{stat_data['link']}]({stat_data['link']})")
                st.markdown(f"**Example Use:** `{query} [source]({stat_data['link']})`")
                st.markdown("---")
    else:
        st.error("Unable to extract content from the provided URL.")

st.markdown("----")
