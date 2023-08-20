import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import re

# Secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Regex patterns for potential statistics
STATISTIC_PATTERNS = [
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?%',  
    r'1 in \d+',                      
    r'1 of \d+',                      
    r'\$\d{1,3}(?:,\d{3})*(?:\.\d+)?', 
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?',   
]

@st.cache(show_spinner=False)
def fetch_web_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.text if response.status_code == 200 else None
    except:
        return None

@st.cache(show_spinner=False)
def extract_html_content(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    return " ".join(soup.stripped_strings)

def find_statistics(text_content):
    stats = []
    for pattern in STATISTIC_PATTERNS:
        matches = re.findall(pattern, text_content)
        stats.extend(matches)
    return stats

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    response = requests.get(url).json()
    return response.get('items', [{}])[0].get('link', '')

def generate_example_usage(statistic, article_content):
    prompt = f"Provide a sentence using the statistic '{statistic}' in the context of an article about '{article_content[:50]}'..."
    response = openai.Completion.create(prompt=prompt, max_tokens=100)
    return response.choices[0].text.strip()

def stylish_box(statistic, url, example_use):
    return f"""
    <div style="
        border: 2px solid #f1f1f1;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0px;
        box-shadow: 2px 2px 12px #aaa;">
        <strong>Statistic:</strong> {statistic}<br>
        <strong>Source:</strong> <a href='{url}'>{url}</a><br>
        <strong>Example Use:</strong> {example_use}
    </div>
    """

def main():
    st.title("StatGrabber 2.0")
    st.write("Enter a URL and discover amazing statistics!")
    url = st.text_input("Enter URL:")

    if url:
        html_content = fetch_web_content(url)
        text_content = extract_html_content(html_content)
        stats = find_statistics(text_content)

        for idx, stat in enumerate(stats, 1):
            search_query = f"statistics about {stat} related to {text_content[:50]}"
            link = search_google(search_query)
            example_use = generate_example_usage(stat, text_content)
            st.markdown(stylish_box(stat, link, example_use), unsafe_allow_html=True)

    st.sidebar.header("About")
    st.sidebar.write("StatGrabber 2.0 is an enhanced AI-powered tool to help you quickly discover and cite statistics from your content.")
    st.sidebar.write("This tool leverages GPT-4 and other models to analyze content and provide relevant statistics.")

if __name__ == '__main__':
    main()
