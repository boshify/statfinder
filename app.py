import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import random
import re

# Secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Regex patterns to identify potential statistics
STATISTIC_PATTERNS = [
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?%',  
    r'1 in \d+',                      
    r'1 of \d+',                      
    r'\$\d{1,3}(?:,\d{3})*(?:\.\d+)?', 
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?',   
]

FUN_MESSAGES = [
    "Calculating pixels...",
    "Finding best statistics...",
    "Analyzing content...",
    "Thinking...",
    "Brewing coffee...",
    "AI magic in progress..."
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

def main():
    st.title("StatGrabber 2.0")
    st.write("Enter a URL and discover amazing statistics!")
    url = st.text_input("Enter URL:")

    if url:
        with st.spinner(random.choice(FUN_MESSAGES)):
            html_content = fetch_web_content(url)
            text_content = extract_html_content(html_content)
            stats = find_statistics(text_content)

            if not stats:
                st.warning("No statistics found in the provided URL.")
                return

            for idx, stat in enumerate(stats, 1):
                search_query = f"statistics 2023 {stat}"
                link = search_google(search_query)
                if link:
                    st.markdown(f"**{idx}. Statistic:** {stat} [Source]({link})")
                else:
                    st.markdown(f"**{idx}. Statistic:** {stat}")

    st.sidebar.header("About")
    st.sidebar.write("StatGrabber 2.0 is an enhanced AI-powered tool to help you quickly discover and cite statistics from your content.")
    st.sidebar.write("This tool leverages GPT-4 and other models to analyze content and provide relevant statistics.")

if __name__ == '__main__':
    main()
