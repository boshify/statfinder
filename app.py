import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import time
import random
import re

# Load secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Regex patterns to identify sentences with potential statistics
STATISTIC_PATTERNS = [
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?%',  # Percentages
    r'1 in \d+',                      # '1 in 10'
    r'1 of \d+',                      # '1 of 10'
    r'\$\d{1,3}(?:,\d{3})*(?:\.\d+)?',  # Dollar values
    r'\d{1,3}(?:,\d{3})*(?:\.\d+)?',    # Decimal and non-decimal numbers
]

def chunk_text(text, max_length=1500):
    sentences = text.split('.')
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_length:
            chunk += sentence + "."
        else:
            chunks.append(chunk)
            chunk = sentence + "."
    if chunk:
        chunks.append(chunk)
    return chunks

def stylish_box(content):
    box_style = """
    <div style="
        border: 2px solid #f1f1f1;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0px;
        box-shadow: 2px 2px 12px #aaa;">
        {content}
    </div>
    """
    return box_style.format(content=content)

st.title("StatGrabber")
st.write("Enter a URL and find statistics you can link to quickly!")
url = st.text_input("Enter URL:")

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

def search_google(query, exclude_url):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    response = requests.get(url).json()
    if 'items' in response:
        for item in response['items']:
            link = item.get('link')
            if link and link != exclude_url:
                return link
    return None

def extract_statistic_from_url(stat_url):
    page_content = get_webpage_content(stat_url)
    if not page_content:
        return None, stat_url
    page_text = extract_content_from_html(page_content)
    
    for pattern in STATISTIC_PATTERNS:
        matches = re.findall(pattern, page_text)
        for match in matches:
            start_idx = page_text.find(match)
            surrounding_text = page_text[max(0, start_idx - 60):min(start_idx + len(match) + 60, len(page_text))]
            surrounding_text = surrounding_text.strip()
            if len(surrounding_text.split()) > 5:
                return surrounding_text, stat_url
    return None, stat_url

def process_url(main_url):
    html_content = get_webpage_content(main_url)
    if html_content:
        text_content = extract_content_from_html(html_content)
        chunks = chunk_text(text_content)
        aggregated_points = []
        
        for text_chunk in chunks:
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Provide concise summaries for the main ideas in the following content:\n{text_chunk}",
                max_tokens=150
            )
            key_points = response.choices[0].text.strip().split("\n")
            aggregated_points.extend(key_points)
            
        for idx, point in enumerate(aggregated_points[:10], 1):
            search_query = f"statistics 2023 {point}"
            stat_url = search_google(search_query, main_url)
            if stat_url:
                statistic, _ = extract_statistic_from_url(stat_url)
            else:
                statistic = None

            if statistic:
                content = f"<h3>{idx}. {point}</h3><br>Statistic: {statistic}<br>Example: In a recent discussion on cryptocurrencies, I mentioned that '{statistic}'.<br><br>URL: {stat_url}"
            else:
                content = f"<h3>{idx}. {point}</h3><br>No relevant statistic found."
            st.markdown(stylish_box(content), unsafe_allow_html=True)
    else:
        st.error("Unable to fetch the content from the provided URL. Please check if the URL is correct and try again.")

if url:
    process_url(url)

st.sidebar.header("About")
st.sidebar.write("StatGrabber is an AI-powered tool to help you quickly find and cite statistics related to your article or content.")
st.sidebar.write("This tool uses GPT-3.5-turbo and other AI models to analyze the content and fetch relevant statistics.")
