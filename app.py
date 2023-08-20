import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import time
import random
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

# Load secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def extract_keywords(text, num=5):
    # Tokenize the text and tag with POS
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)

    # Get all non-stopword nouns
    keywords = [word for word, pos in tagged if pos in ['NN', 'NNS', 'NNP', 'NNPS'] and word.lower() not in stopwords.words('english')]
    keywords_frequency = nltk.FreqDist(keywords)
    return [word for word, freq in keywords_frequency.most_common(num)]

STATISTIC_PATTERNS = [
    re.compile(r'(?P<stat>\d+%?\s?[-–—]\s?\d+%)'),
    re.compile(r'(?P<stat>\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|trillion)?\b)'),
    re.compile(r'(?P<stat>\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\s*(?:million|billion|trillion)?\b)'),
    re.compile(r'(?P<stat>\d+%?\s?(?:of|from|to|between)\s?.+?)\.')
]

def chunk_text(text, max_length=1500):
    sentences = sent_tokenize(text)
    chunks = []
    chunk = []
    current_length = 0

    for sentence in sentences:
        current_length += len(sentence)
        if current_length < max_length:
            chunk.append(sentence)
        else:
            chunks.append(" ".join(chunk))
            chunk = [sentence]
            current_length = len(sentence)

    if chunk:
        chunks.append(" ".join(chunk))
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

# Styling
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

st.title("StatFinder")
st.write("Enter a URL and find statistics you can link to quickly!")
url = st.text_input("Enter URL:")

fun_messages = [
    "Calculating all the pixels...",
    "Finding the best statistics...",
    "Analyzing the content...",
    "Thinking really hard...",
    "Grabbing some coffee...",
    "Doing some cool AI stuff..."
]

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

def show_loading_message(duration=6):
    with st.empty():
        start_time = time.time()
        while time.time() - start_time < duration:
            message = random.choice(fun_messages)
            st.write(message)
            time.sleep(2)

def is_valid_content(sentence):
    return len(sentence.split()) >= 5 and all(symbol not in sentence for symbol in ['{', '}', '%', '='])

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    response = requests.get(url).json()
    return response['items'][0]['link']

def score_statistic(statistic, keywords):
    score = 0
    for keyword in keywords:
        score += statistic.lower().count(keyword.lower())
    return score

def extract_statistic_from_url(url, keywords):
    page_content = get_webpage_content(url)
    if not page_content:
        return []
    page_text = extract_content_from_html(page_content)
    
    potential_statistics = []

    for pattern in STATISTIC_PATTERNS:
        matches = re.finditer(pattern, page_text)
        for match in matches:
            start_idx = match.start()
            end_idx = match.end()

            start_sentence_idx = page_text.rfind('.', 0, start_idx) + 1  # start of the sentence
            end_sentence_idx = page_text.find('.', end_idx)  # end of the sentence
            surrounding_text = page_text[start_sentence_idx:end_sentence_idx + 1].strip()

            if surrounding_text and surrounding_text[-1] == '.' and is_valid_content(surrounding_text):
                potential_statistics.append((surrounding_text.strip(), score_statistic(surrounding_text, keywords)))

    potential_statistics.sort(key=lambda x: x[1], reverse=True)
    return [(stat[0], search_google(stat[0])) for stat in potential_statistics[:10]]

def process_url(url):
    content = get_webpage_content(url)
    if not content:
        return []

    text = extract_content_from_html(content)
    if not text:
        return []

    main_keywords = extract_keywords(text)
    statistics = extract_statistic_from_url(url, main_keywords)
    return statistics

if url:
    show_loading_message()
    statistics = process_url(url)
    if statistics:
        for statistic, link in statistics:
            example_use = f"<em>'According to a recent report, {statistic} (source: <a href='{link}'>{link}</a>)'</em>"
            st.markdown(stylish_box(
                f"<strong>Statistic:</strong> {statistic} <br> " +
                f"<strong>Link:</strong> <a href='{link}' target='_blank'>{link}</a> <br> " +
                f"<strong>Example Use:</strong> {example_use}"
            ), unsafe_allow_html=True)
    else:
        st.warning("No statistics found. Try another URL or ensure the page contains relevant data.")
