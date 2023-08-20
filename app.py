import streamlit as st
import requests
import random
import re
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

STATISTIC_PATTERNS = [
    re.compile(r'(?P<stat>\d+%?\s?[-–—]\s?\d+%)'),
    re.compile(r'(?P<stat>\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|trillion)?\b)'),
    re.compile(r'(?P<stat>\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\s*(?:million|billion|trillion)?\b)'),
    re.compile(r'(?P<stat>\d+%?\s?(?:of|from|to|between)\s?.+?)\.')
]

fun_messages = [
    "🔍 Searching for gold...",
    "📊 Digging deep for those stats...",
    "🤖 My digital spade is at work...",
    "⛏️ Miners are hard at work...",
    "💼 Suiting up for some data extraction..."
]

def extract_content_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    return " ".join(soup.stripped_strings)

def extract_statistic_from_url(url):
    try:
        page_content = requests.get(url).text
        page_text = extract_content_from_html(page_content)
        
        potential_statistics = []
        for pattern in STATISTIC_PATTERNS:
            matches = re.finditer(pattern, page_text)
            for match in matches:
                start_idx = match.start()
                end_idx = match.end()

                start_sentence_idx = page_text.rfind('.', 0, start_idx) + 1
                end_sentence_idx = page_text.find('.', end_idx)
                surrounding_text = page_text[start_sentence_idx:end_sentence_idx + 1].strip()

                if surrounding_text and surrounding_text[-1] == '.':
                    potential_statistics.append(surrounding_text)
        
        return potential_statistics
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

st.title("StatFinder")
st.write("Enter a URL and find statistics you can link to quickly!")
url = st.text_input("Enter URL:")

if url:
    st.write(random.choice(fun_messages))
    statistics = extract_statistic_from_url(url)
    if statistics:
        for statistic in statistics:
            example_use = f"<em>'According to a recent report, {statistic} (source: <a href='{url}'>{url}</a>)'</em>"
            st.markdown(
                f"<strong>Statistic:</strong> {statistic} <br> " +
                f"<strong>Link:</strong> <a href='{url}' target='_blank'>{url}</a> <br> " +
                f"<strong>Example Use:</strong> {example_use}",
                unsafe_allow_html=True
            )
    else:
        st.warning("No statistics found. Try another URL or ensure the page contains relevant data.")
