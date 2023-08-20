import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
from functools import lru_cache
import time
import random
import re
import lxml

# Load secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Regex patterns to identify sentences with potential statistics
STATISTIC_PATTERNS = [
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?%',  # Matches percentages
    r'1 in \d+',                      # Matches '1 in 10'
    r'1 of \d+',                      # Matches '1 of 10'
    r'\$\d{1,3}(?:,\d{3})*(?:\.\d+)?',  # Matches dollar values
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?',    # Matches decimal and non-decimal numbers
]

# Styling and layout
st.markdown(
    """
    <style>
        .reportview-container {
            background: black;
            color: white;
        }
        h1 {
            font-size: 50px;
            margin-bottom: 30px;
        }
        img {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin-top: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@lru_cache(maxsize=None)
def get_webpage_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.text if response.status_code == 200 else None
    except:
        return None

def is_html(content):
    return content is not None and any(tag in content.lower() for tag in ['<html', '<body', '<head', '<script', '<div', '<span', '<a'])

def extract_content_from_html(html_content):
    if not is_html(html_content):
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception:
        soup = BeautifulSoup(html_content, 'lxml')

    for script in soup(["script", "style"]):
        script.extract()
    return " ".join(soup.stripped_strings)

def search_google(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': GOOGLE_API_KEY,
        'cx': CSE_ID
    }
    response = requests.get(url, params=params).json()
    return response['items'][0]['link']

def extract_statistic_from_url(url):
    page_content = get_webpage_content(url)
    if not page_content:
        return None, url
    page_text = extract_content_from_html(page_content)
    
    for pattern in STATISTIC_PATTERNS:
        matches = re.findall(pattern, page_text)
        for match in matches:
            start_idx = page_text.find(match)
            surrounding_text = page_text[max(0, start_idx - 60):min(start_idx + len(match) + 60, len(page_text))]
            if len(surrounding_text.split()) > 5:
                return surrounding_text.strip(), url
    return None, url

def process_url(url):
    with st.spinner():
        html_content = get_webpage_content(url)
        if html_content:
            text_content = extract_content_from_html(html_content)
            chunks = chunk_text(text_content)
            aggregated_points = analyze_content(chunks)
            
            for idx, point in enumerate(aggregated_points[:10], 1):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": f"Provide a concise summary for the following statement:\n{point}"}
                    ]
                )
                summarized_point = response.choices[0]["message"]["content"].strip()
                summarized_point = point if not is_valid_content(summarized_point) else summarized_point
                search_query = f"statistics 2023 {summarized_point}"
                statistic, stat_url = extract_statistic_from_url(search_google(search_query))
                
                if statistic:
                    content = f"{idx}. {summarized_point}<br><br>Statistic: {statistic}<br>URL: {stat_url}<br><button onclick=\"navigator.clipboard.writeText('{statistic} - Source: {stat_url}')\">Copy to clipboard</button>"
                    st.markdown(stylish_box(content), unsafe_allow_html=True)
                else:
                    content = f"{idx}. {summarized_point}<br><br>No relevant statistic found."
                    st.markdown(stylish_box(content), unsafe_allow_html=True)
        else:
            st.error("Unable to fetch the content from the provided URL. Please check if the URL is correct and try again.")

# The main app
st.title("StatGrabber")
st.write("Enter a URL and find statistics you can link to quickly!")
url = st.text_input("Enter URL:")

if url:
    process_url(url)

st.sidebar.header("About")
st.sidebar.write("StatGrabber is an AI-powered tool to help you quickly find and cite statistics related to your article or content.")
st.sidebar.write("This tool uses GPT-4 and other AI models to analyze the content and fetch relevant statistics.")
